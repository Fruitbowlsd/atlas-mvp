"""Tests der EBD-Codelisten-Extraktion (Issue #50).

Fuenf Sorten von Tests:

* Fixwert-Regressionstests gegen das ECHTE Dokument 4.2. Die Sollwerte stammen
  aus dem Dokumenttext selbst (Kapitel 5 beschreibt die Codelistenform,
  Kapitel 4 die EBD-Tabellenform) und aus der empirischen Strukturanalyse zu
  Issue #50 -- kein Test prueft eine Annahme gegen sich selbst.
* Ausklammerungstests: das Dokument besteht zu 346 Abschnitten aus
  Entscheidungsbaum-Diagrammen, deren Tabellen EBENFALLS eine Spalte ``Code``
  mit gleich aussehenden Werten fuehren. Sie duerfen unter keinen Umstaenden
  als Codeliste importiert werden (Auftrag Abschnitt 10).
* Der Kontexttest: derselbe Antwortcode hat je Codeliste eine andere
  Bedeutung. Eine globale Deduplizierung ueber den Codewert waere fachlich
  falsch und wird dauerhaft ausgeschlossen.
* Ein Idempotenztest gegen die Datenbank.
* Einheitentests ohne PDF.

Der PDF-abhaengige Teil ueberspringt sich selbst, wenn die Datei nicht
vorliegt; sie ist aus Groessengruenden nicht im Repository (siehe
data/regulatory/README.md).
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.regulatory_extraction import compute_file_hash
from app.regulatory_extraction_ebd import (
    TABLE_FORMS,
    EBD_FORM,
    Section,
    _message_type_of,
    extract_ebd_codelists,
    import_ebd_codelists,
)

_BACKEND = Path(__file__).resolve().parents[1]
_PDF = Path(os.getenv(
    "ATLAS_EBD_CODELISTEN_PDF",
    _BACKEND / "data" / "regulatory" / "EBD_und_Codelisten_4_2_20251001.pdf",
))

pytestmark = pytest.mark.skipif(
    not _PDF.exists(),
    reason=f"EBD und Codelisten 4.2 nicht vorhanden ({_PDF}) -- siehe data/regulatory/README.md",
)

# Gemessen gegen "Entscheidungsbaum-Diagramme und Codelisten fuer die
# Antwortnachrichten" 4.2 (BNetzA-Mitteilung Nr. 54, Publikationsdatum
# 01.10.2025, 851 Seiten).
_SHA256 = "11c3f77b738a4e0e0f743ddc907f82ab01ceb9d1835da4a0b9ce181ae418f8eb"
_EXPECTED_SECTIONS = 127     # Abschnitte S_/G_/GS_
_EXPECTED_CODELISTS = 125    # davon importierbar
_EXPECTED_ENTRIES = 388
_EXPECTED_EBD_SECTIONS = 346
_EXPECTED_EBD_PAGES = 240


@pytest.fixture(scope="module")
def extracted():
    return extract_ebd_codelists(str(_PDF))


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    version = models.RegulatoryVersion(
        name="Testfassung", sector="gas", is_active=True,
        valid_from=datetime(2026, 4, 1),
    )
    session.add(version)
    session.commit()
    yield session, version
    session.close()


# ---------------------------------------------------------------------------
# Dokument
# ---------------------------------------------------------------------------

def test_dokument_ist_die_erwartete_fassung():
    """Version 4.2, wie von der Mitteilung Nr. 54 verlinkt -- nicht die
    kursierende 4.3, die ein spaeterer BDEW-Stand ist."""
    assert compute_file_hash(str(_PDF)) == _SHA256


def test_umfang_der_extraktion(extracted):
    entries, skipped, deferred, empty, stats = extracted
    assert stats["codelist_sections"] == _EXPECTED_SECTIONS
    assert len({(e.section, e.codelist_name) for e in entries}) == _EXPECTED_CODELISTS
    assert len(entries) == _EXPECTED_ENTRIES


# ---------------------------------------------------------------------------
# EBD-Abschnitte: bewusst ausgeklammert (Auftrag Abschnitt 10)
# ---------------------------------------------------------------------------

def test_ebd_abschnitte_werden_gezaehlt_nicht_gelesen(extracted):
    """Die Diagramme werden als bewusst ausgeklammert AUSGEWIESEN -- nicht
    stillschweigend nicht getroffen."""
    entries, _skipped, _deferred, _empty, stats = extracted
    assert stats["ebd_sections"] == _EXPECTED_EBD_SECTIONS
    assert stats["ebd_pages_with_table"] == _EXPECTED_EBD_PAGES
    assert stats["ebd_page_first"] == 28
    assert stats["ebd_page_last"] == 835
    # Kein einziger Eintrag stammt aus einem E_-Abschnitt.
    assert not [e for e in entries if e.codelist_name.startswith("E_")]


def test_ebd_tabelle_wird_nicht_als_codeliste_gelesen(extracted):
    """Der eigentliche Ausklammerungstest.

    Die EBD-Tabelle fuehrt laut Kapitel 4 eine Spalte ``Code`` mit Werten, die
    von Antwortcodes einer Codeliste nicht zu unterscheiden sind (A01, A03 ...).
    Unterscheidbar sind nur die Tabellen. Faellt die Formpruefung aus, landen
    Prueflogik-Codes in der Wissensbasis.

    Geprueft an E_0614_Kündigung Vertrag prüfen (Abschnitt 6.2.1, S. 46): dort
    tragen die Codes A01/A03/A04/A05/A06 Hinweise der Form "Cluster: Ablehnung".
    Das Wort "Cluster" ist EBD-Vokabular (Kapitel 3) und kommt in keiner
    Codeliste vor.
    """
    entries, _skipped, _deferred, _empty, _stats = extracted
    assert not [e for e in entries if "Cluster" in e.bedeutung]
    assert not [e for e in entries if "Cluster" in e.hinweise]
    # Auf den Seiten von E_0614 darf ueberhaupt nichts gelesen worden sein.
    assert not [e for e in entries if 46 <= e.source_page <= 50]


def test_ebd_form_und_codelisten_formen_sind_disjunkt():
    """Strukturell, ohne PDF: keine Codelistenform kann die EBD-Form treffen.

    Die EBD-Tabelle hat weder ``Nutzung`` noch ``Name``, die Codeliste kein
    ``Prüfergebnis``. ``_locate_columns`` verlangt ALLE Kopfzellen -- damit ist
    eine Verwechslung ausgeschlossen, nicht nur unwahrscheinlich.
    """
    ebd_headers = {c.header for c in EBD_FORM.columns}
    for form in TABLE_FORMS:
        headers = {c.header for c in form.columns}
        assert not headers <= ebd_headers, f"{form.key} waere von der EBD-Form erfuellbar"
        assert not ebd_headers <= headers, f"EBD-Form waere von {form.key} erfuellbar"


def test_aenderungshistorie_ist_nicht_datenbereich(extracted):
    """Kapitel 19 (ab S. 836) zitiert Codes frueherer Staende."""
    entries, _skipped, _deferred, _empty, _stats = extracted
    assert not [e for e in entries if e.source_page >= 836]


# ---------------------------------------------------------------------------
# Regressionstests mit echten Daten
# ---------------------------------------------------------------------------

def test_regression_s0103_netznutzungsrechnung(extracted):
    """S_0103 (Abschnitt 6.10.2, S. 157), Form Code/Nutzung/Bedingung/Name."""
    entries, _s, _d, _e, _st = extracted
    got = {e.code: e for e in entries if e.section == "6.10.2"}
    assert set(got) == {"5", "9", "28", "Z01", "Z02", "Z03", "Z06", "Z07", "Z10", "Z33"}
    assert got["5"].bedeutung == "Preis/Rechenregel falsch"
    assert got["Z01"].bedeutung == "Abrechnungsbeginn ungleich Vertragsbeginn"
    assert got["Z06"].bedeutung == "Artikel nicht vereinbart"
    # Nutzungswiederholbarkeit aus Kapitel 5, unveraendert uebernommen.
    assert {e.nutzung for e in got.values()} == {"O"}
    assert all(e.source_page == 157 for e in got.values())
    assert all(e.codelist_name == "S_0103_Netznutzungsrechnung prüfen" for e in got.values())


def test_regression_g0060_wim_gas(extracted):
    """G_0060 (Abschnitt 14.4.2, S. 788), Form Code/Nutzung/Name."""
    entries, _s, _d, _e, _st = extracted
    got = {e.code: e for e in entries if e.section == "14.4.2"}
    assert set(got) == {"E17", "Z07", "ZB5"}
    assert got["ZB5"].bedeutung == "Kein Eigenausbau des MSBA"
    assert got["ZB5"].nutzung == "X"
    assert got["Z07"].nutzung == "O"
    assert got["Z07"].prozessfamilie == "14 WiM Gas"


def test_regression_g0064_form_mit_hinweisspalte(extracted):
    """G_0064 (Abschnitt 14.6.3, S. 792) -- die Variante Code/Nutzung/Hinweis/Name,
    die Kapitel 5 NICHT nennt und die erst der Befund zu Issue #50 gefunden hat."""
    entries, _s, _d, _e, _st = extracted
    got = {e.code: e for e in entries if e.section == "14.6.3"}
    assert set(got) == {"Z13", "Z14"}
    assert got["Z13"].bedeutung == "Zustimmung ohne Korrekturen"
    assert got["Z14"].bedeutung == "Zustimmung mit Terminänderung"
    assert got["Z13"].form_key == "codeliste-hinweis"


def test_fussnotenmarker_bleibt_unveraendert(extracted):
    """Das Dokument schreibt in der Spalte Nutzung "O [41]" (S. 537). Der
    Marker ist Bestandteil des Zellwerts und wird NICHT wegnormalisiert
    (Auftrag Abschnitt 8)."""
    entries, _s, _d, _e, _st = extracted
    z01 = next(e for e in entries if e.section == "8.1.1.1" and e.code == "Z01")
    assert z01.nutzung == "O [41]"
    assert z01.hinweise.startswith("[41] Wenn SG4 DTM+471")


def test_eintraege_laufen_ueber_seitenumbruch_korrekt_weiter(extracted):
    """G_0081 (Abschnitt 13.22.1.1) laeuft von S. 769 auf S. 770 weiter, ohne
    die Kopfzeile zu wiederholen. Der Befund zu Issue #50 hat hier den Fall
    gefunden, in dem Code und Bedeutung auseinanderfielen."""
    entries, _s, _d, _e, _st = extracted
    got = {e.code: e for e in entries if e.section == "13.22.1.1"}
    assert "Z07" in got and "Z03" in got
    assert got["Z03"].source_page == 770
    assert got["Z03"].bedeutung == "Betrag der Abschlagsrechnung falsch"
    assert got["Z07"].bedeutung.startswith(
        "Netznutzungsmesswerte / -energiemengen fehlen")
    # Keine Bedeutung darf leer sein -- genau das war das Symptom.
    assert all(e.bedeutung for e in entries)


# ---------------------------------------------------------------------------
# Kontextbezogene Identitaet: KEINE globale Deduplizierung
# ---------------------------------------------------------------------------

def test_gleicher_code_behaelt_je_codeliste_seine_bedeutung(extracted):
    """Kapitel 3 des Dokuments: "Die Antwortcodes haben eine unterschiedliche
    Bedeutung je EBD."

    Die fachliche Identitaet eines Antwortcodes entsteht erst aus
    RegulatoryVersion + CodeList + Code. Eine Zusammenfuehrung allein ueber den
    Codewert waere fachlich falsch.
    """
    entries, _s, _d, _e, _st = extracted
    z07 = [e for e in entries if e.code == "Z07"]
    bedeutungen = {e.bedeutung.split(" Dieser")[0].strip() for e in z07}
    assert len(z07) > 1
    assert "Netznutzungsmesswerte / -energiemengen fehlen" in bedeutungen
    assert "Ablehnung (Keine Berechtigung) Der Absender lehnt die Transaktion ab." \
        in " ".join(bedeutungen) or any(
            b.startswith("Ablehnung (Keine Berechtigung)") for b in bedeutungen)
    # Deutlich mehr Eintraege als verschiedene Codewerte -- eine globale
    # Deduplizierung wuerde den Grossteil der Wissensbasis vernichten.
    assert len({e.code for e in entries}) < len(entries) / 4


def test_codes_werden_nur_innerhalb_einer_codeliste_zusammengefuehrt(db):
    session, version = db
    import_ebd_codelists(session, str(_PDF), version.id)
    rows = (
        session.query(models.CodeListEntry, models.CodeList)
        .join(models.CodeList)
        .filter(models.CodeListEntry.code == "Z07")
        .all()
    )
    assert len(rows) > 1
    # Jeder Z07 haengt an einer eigenen CodeList.
    assert len({cl.id for _entry, cl in rows}) == len(rows)
    assert len({e.bedeutung for e, _cl in rows}) > 1


# ---------------------------------------------------------------------------
# Sonderfaelle (Auftrag Abschnitt 14)
# ---------------------------------------------------------------------------

def test_s0109_wird_zurueckgestellt_nicht_verfaelscht(extracted):
    """S_0109 (Abschnitt 6.10.4, S. 158) fuehrt ZWEI fachlich verschiedene
    Bedingungsspalten je Code. ``CodeListEntry`` hat dafuer ein Feld; ein
    Import wuerde die Zuordnung "welche Bedingung gilt wann" vernichten.
    Entscheidung zu Issue #50: zurueckstellen statt verfaelschen."""
    entries, _skipped, deferred, _empty, _stats = extracted
    assert len(deferred) == 1
    assert deferred[0].section == "6.10.4"
    assert deferred[0].name.startswith("S_0109")
    assert not [e for e in entries if e.section == "6.10.4"]


def test_abschnitt_ohne_tabelle_erzeugt_keine_leere_codeliste(extracted, db):
    """G_0088 (Abschnitt 15.1.2.2) enthaelt keine Tabelle, sondern den
    Querverweis "Es ist die Codeliste G_0079 zu nutzen."."""
    _entries, _skipped, _deferred, empty, _stats = extracted
    assert [d.section for d in empty] == ["15.1.2.2"]
    session, version = db
    import_ebd_codelists(session, str(_PDF), version.id)
    assert not (
        session.query(models.CodeList)
        .filter(models.CodeList.quelle_kapitel == "15.1.2.2")
        .first()
    )


# ---------------------------------------------------------------------------
# Import, Provenienz, Idempotenz
# ---------------------------------------------------------------------------

def test_import_legt_codelisten_mit_provenienz_an(db):
    session, version = db
    report = import_ebd_codelists(session, str(_PDF), version.id)
    assert not report.errors
    assert report.codelist_sections == _EXPECTED_SECTIONS
    assert report.codelists_created == _EXPECTED_CODELISTS
    assert report.entries_imported == _EXPECTED_ENTRIES

    lists = session.query(models.CodeList).all()
    assert len(lists) == _EXPECTED_CODELISTS
    for cl in lists:
        assert cl.regulatory_version_id == version.id
        assert cl.quelle_hash == _SHA256
        assert cl.quelle_dokument == str(_PDF)
        assert cl.quelle_kapitel          # Abschnittsnummer
        assert not cl.name.startswith("E_")
    for entry in session.query(models.CodeListEntry).all():
        assert entry.quelle_seite and 23 <= entry.quelle_seite <= 835
        assert entry.gueltig_ab == version.valid_from.date()
        assert entry.gueltig_bis is None


def test_gleichnamige_codelisten_bleiben_getrennt(db):
    """"G_0016_Antwort auf Änderung vom NB" kommt in Kapitel 13 mehrfach in
    verschiedenen Abschnitten vor. Jedes Vorkommen ist eine eigene Codeliste in
    ihrem eigenen fachlichen Kontext -- der Name allein darf nicht gruppieren."""
    session, version = db
    import_ebd_codelists(session, str(_PDF), version.id)
    rows = (
        session.query(models.CodeList)
        .filter(models.CodeList.name.like("G_0016%"))
        .all()
    )
    assert len(rows) > 1
    assert len({cl.quelle_kapitel for cl in rows}) == len(rows)


def test_import_ist_idempotent(db):
    session, version = db
    first = import_ebd_codelists(session, str(_PDF), version.id)
    lists_after_first = session.query(models.CodeList).count()
    entries_after_first = session.query(models.CodeListEntry).count()
    assert first.entries_imported == _EXPECTED_ENTRIES

    second = import_ebd_codelists(session, str(_PDF), version.id)
    assert second.errors                      # gleicher Hash -> abgelehnt
    assert second.entries_imported == 0
    assert session.query(models.CodeList).count() == lists_after_first
    assert session.query(models.CodeListEntry).count() == entries_after_first

    third = import_ebd_codelists(session, str(_PDF), version.id, reimport=True)
    assert third.reimported
    assert not third.errors
    assert session.query(models.CodeList).count() == lists_after_first
    assert session.query(models.CodeListEntry).count() == entries_after_first


def test_keine_fk_auf_process_identifier(extracted):
    """Anders als bei der OBIS-Codeliste vermutet: die EBD-Codelisten enthalten
    KEINE Pruefidentifikator-Referenzen. Das Feld bleibt leer, eine
    pi_id-Verknuepfung wird nicht angelegt."""
    entries, _s, _d, _e, _st = extracted
    assert not any(getattr(e, "pruefidentifikatoren", "") for e in entries)


# ---------------------------------------------------------------------------
# Einheitentests ohne PDF
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("titel,erwartet", [
    ("G_0001_ORDRSP Abl. der Anforderung", "ORDRSP"),
    ("S_0103_Netznutzungsrechnung prüfen", ""),
    ("G_0049_ORDRSP_Ablehnung der Anforderung von Stammdaten", "ORDRSP"),
])
def test_message_type_nur_woertlich(titel, erwartet):
    """Der Nachrichtentyp wird NUR uebernommen, wenn er woertlich im
    Abschnittstitel steht -- nicht erraten (Auftrag Abschnitt 14)."""
    assert _message_type_of(titel) == erwartet


@pytest.mark.parametrize("titel,codeliste,ebd", [
    ("S_0103_Netznutzungsrechnung prüfen", True, False),
    ("G_0002_Antwort auf Änderungsmeldung", True, False),
    ("GS_002_MehrMinderMengen-Rechnung prüfen", True, False),
    ("E_0594_Anfrage vom LF prüfen", False, True),
    ("Geräteübernahmeangebot", False, False),
])
def test_abschnittspraefix_trennt_codeliste_von_ebd(titel, codeliste, ebd):
    s = Section(number="1.1.1", title=titel, page=1, top=0.0)
    assert s.is_codelist is codeliste
    assert s.is_ebd is ebd
