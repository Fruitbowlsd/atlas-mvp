"""Tests der OBIS-Codelisten-Extraktion (Issue #48).

Vier Sorten von Tests:

* Fixwert-Regressionstests je extrahierter Tabellenform gegen die ECHTE
  Codeliste 2.5c. Die Sollwerte stammen aus der empirischen Strukturanalyse
  (Befund zu Issue #48) und aus dem Dokumenttext selbst -- kein Test prueft
  eine Annahme gegen sich selbst.
* Negativtests, die belegen, dass der Parser STRUKTURELL arbeitet:
  Kapitel 7 (Aenderungshistorie) enthaelt 14 OBIS-Kennzahlen und 4
  Messprodukt-Codes als Zitate frueherer Staende, teils inzwischen geloescht.
  Ein dokumentweiter Volltext-Regex wuerde hier durchfallen.
* Ein Idempotenztest gegen die Datenbank.
* Einheitentests der Hilfsfunktionen ohne PDF.

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
from app.regulatory_extraction_obis import (
    TABLE_FORMS,
    _clean,
    _split_codes,
    extract_obis_codelists,
    import_obis_codelists,
)

_BACKEND = Path(__file__).resolve().parents[1]
_PDF = Path(os.getenv(
    "ATLAS_OBIS_CODELISTE_PDF",
    _BACKEND / "data" / "regulatory" / "Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf",
))

pytestmark = pytest.mark.skipif(
    not _PDF.exists(),
    reason=f"Codeliste OBIS 2.5c nicht vorhanden ({_PDF}) -- siehe data/regulatory/README.md",
)

# Gemessen gegen die Codeliste der OBIS-Kennzahlen und Medien 2.5c
# (BNetzA-Mitteilung Nr. 54, Publikationsdatum 01.10.2025).
_SHA256 = "bc43ff890fde3d02203e72b67e10bfeb966c53791d85246067c54c45a67c8aef"
_EXPECTED_ENTRIES = 227
_EXPECTED_CODELISTS = 12
# Kapitel 7 beginnt auf S.39 -- ab dort darf nichts mehr gelesen werden.
_CHANGELOG_FIRST_PAGE = 39


@pytest.fixture(scope="module")
def extracted():
    entries, skipped, missing = extract_obis_codelists(str(_PDF))
    return entries, skipped, missing


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
# Dokumentidentitaet und Gesamtumfang
# ---------------------------------------------------------------------------

def test_dokument_ist_die_erwartete_fassung():
    assert compute_file_hash(str(_PDF)) == _SHA256


def test_alle_freigegebenen_formen_werden_erkannt(extracted):
    _, _, missing = extracted
    assert missing == []


def test_gesamtzahl_der_eintraege(extracted):
    entries, _, _ = extracted
    assert len(entries) == _EXPECTED_ENTRIES


def test_keine_bedeutungslosen_eintraege(extracted):
    """Jeder extrahierte Code traegt eine Bedeutung -- sonst duerfte er laut
    Auftrag Abschnitt 12 nicht importiert werden."""
    entries, _, _ = extracted
    assert [e.code for e in entries if not e.bedeutung] == []


# ---------------------------------------------------------------------------
# Regressionstest je Tabellenform -- echte Beispiele aus dem Dokument
# ---------------------------------------------------------------------------

def _one(entries, form_key, code, **kwargs):
    hits = [e for e in entries if e.form_key == form_key and e.code == code]
    for key, value in kwargs.items():
        hits = [e for e in hits if getattr(e, key) == value]
    return hits


def test_form1_schluesselwerte(extracted):
    """Kapitel 2.2, S.8 -- vier unabhaengige Wertelisten nebeneinander."""
    entries, _, _ = extracted
    form1 = [e for e in entries if e.form_key == "form1-schluesselwerte"]
    assert len(form1) == 21

    medium = _one(entries, "form1-schluesselwerte", "1")
    medium = [e for e in medium if e.codelist_name.endswith("Medium (A)")]
    assert len(medium) == 1
    assert medium[0].bedeutung == "Elektrizität"
    # Die Kanal-Spalte (B) ist laut Befund KEINE Codeliste und darf nicht
    # als eigene Liste entstehen.
    assert not [e for e in form1 if e.codelist_name.endswith("Kanal (B)")]
    # Bedeutung darf nicht in die Nachbarspalte laufen.
    assert "Kanal" not in medium[0].bedeutung

    messgroesse = [e for e in form1 if e.codelist_name.endswith("Messgröße (C)")]
    assert {e.code for e in messgroesse} == {"1", "2", "3", "4", "5", "6", "7", "8"}
    assert _one(entries, "form1-schluesselwerte", "3")[0].bedeutung == (
        "∑ Li Blindleistung positiv"
    )
    tarif = [e for e in form1 if e.codelist_name.endswith("Tarif (E)")]
    assert {e.code for e in tarif} == {"0", "1", "2", "3", "4", "5", "62", "63"}


def test_form2_obis_strom(extracted):
    """Kapitel 3.1, S.10-11 -- Richtung aus dem Unterspaltenkopf."""
    entries, _, _ = extracted
    bezug = _one(entries, "form2-obis-strom", "1-b:1.6.0", richtung="Bezug (+)")
    assert len(bezug) == 1
    e = bezug[0]
    assert e.bedeutung == "Wirkleistung"
    assert e.werteart == "Maximum"
    # Mehrere Pruefidentifikatoren stehen im Dokument untereinander.
    assert e.pruefidentifikatoren == "13017 13016"
    assert e.source_page == 10

    lieferung = _one(entries, "form2-obis-strom", "1-b:2.6.0", richtung="Lieferung (-)")
    assert lieferung and lieferung[0].bedeutung == "Wirkleistung"
    # "--" bedeutet 'nicht anwendbar' und darf KEIN Code werden.
    assert not [x for x in entries if x.code in ("--", "-")]


def test_form3_weitere_obis_strom(extracted):
    """Kapitel 3.2, S.12 -- Anwendung + Hinweise, Silbentrennung zurueckgebaut."""
    entries, _, _ = extracted
    hit = _one(entries, "form3-obis-strom-weitere", "1-1:1.6.0")
    assert len(hit) == 1
    # Im Dokument als "Lieferbe-\nginn" umbrochen.
    assert hit[0].bedeutung == "Bewegungsdaten im Kalenderjahr vor Lieferbeginn"
    assert hit[0].pruefidentifikatoren == "13015"

    # Gross geschriebene Fortsetzungszeile OHNE Code ("Grundpreis / Arbeitspreis")
    # darf keine neue Bezeichnung beginnen.
    grund = [
        e for e in entries
        if e.form_key == "form3-obis-strom-weitere"
        and e.bedeutung.endswith("Grundpreis / Arbeitspreis")
    ]
    assert grund, "abgeschnittene Bezeichnung -- Fortsetzungszeile nicht erkannt"


def test_form6_obis_gas(extracted):
    """Kapitel 4.1, S.30-31 -- Ausspeisung/Einspeisung getrennt."""
    entries, _, _ = extracted
    aus = _one(entries, "form6-obis-gas", "7-b:3.0.0", richtung="Ausspeisung")
    ein = _one(entries, "form6-obis-gas", "7-b:6.0.0", richtung="Einspeisung")
    assert len(aus) == 1 and len(ein) == 1
    assert aus[0].bedeutung == "Betriebsvolumen [m³]"
    assert aus[0].werteart == "Zählerstand"
    assert aus[0].pruefidentifikatoren == "13002"
    assert ein[0].bedeutung == "Betriebsvolumen [m³]"

    # Ueber zwei Tabellenzeilen umbrochene Bezeichnung gilt fuer ALLE
    # Eintraege ihres Blocks, nicht nur fuer die erste Zeile.
    temp = _one(entries, "form6-obis-gas", "7-b:3.1.0", richtung="Ausspeisung")
    assert temp[0].bedeutung == "Betriebsvolumen [m³] temperaturkompensiert"

    # Status wird als eigenes Merkmal gefuehrt, nicht in die Bedeutung verkettet.
    vorlaeufig = _one(entries, "form6-obis-gas", "7-10:99.33.17")
    assert vorlaeufig[0].status == "Vorläufig"
    assert vorlaeufig[0].bedeutung == "Energiewert [kWh]"


def test_form7_geraetespezifisch(extracted):
    """Kapitel 4.3, S.31-33 -- Richtung aus der Prosazeile ueber der Tabelle."""
    entries, _, _ = extracted
    form7 = [e for e in entries if e.form_key == "form7-obis-gas-geraete"]
    assert len(form7) == 72
    # Zwei Tabellen mit identischem Spaltenkopf, unterscheidbar nur an der
    # Prosazeile "OBIS-Kennzahlen für Aus-/Einspeisung".
    assert sum(1 for e in form7 if e.richtung == "Ausspeisung") == 36
    assert sum(1 for e in form7 if e.richtung == "Einspeisung") == 36

    hit = _one(entries, "form7-obis-gas-geraete", "7-b:1.0.0", richtung="Ausspeisung")
    assert len(hit) == 1
    assert hit[0].bedeutung == "Betriebsvolumen [m³]"
    assert hit[0].status == "ungestört"
    assert hit[0].werteart == "Einzelwerte Zählerstand"

    # Die Tabelle laeuft ueber den Seitenumbruch S.32 -> S.33; dort steht die
    # Messgroesse nicht mehr in der Zeile.
    letzte = _one(entries, "form7-obis-gas-geraete", "7-b:66.0.0")
    assert letzte[0].bedeutung == "Masse [kg]"
    assert letzte[0].source_page == 33


def test_form8_zustandsgroessen_und_gasbeschaffenheit(extracted):
    """Kapitel 4.4 und 4.5 beginnen auf DERSELBEN Seite (S.34) und haben
    identische Spaltenkoepfe -- sie duerfen nicht ineinanderlaufen."""
    entries, _, _ = extracted
    zust = [e for e in entries if e.form_key == "form8-zustandsgroessen"]
    gas = [e for e in entries if e.form_key == "form8-gasbeschaffenheit"]
    assert len(zust) == 4
    assert len(gas) == 42

    temp = _one(entries, "form8-zustandsgroessen", "7-b:99.41.16")
    assert temp[0].bedeutung == "Temperatur [°C]"
    assert temp[0].pruefidentifikatoren == "13008"

    stick = _one(entries, "form8-gasbeschaffenheit", "7-b:70.60.ee")
    assert stick[0].bedeutung == "Stickstoff N2 [mol %]"
    assert stick[0].pruefidentifikatoren == "13007"


def test_form9_medien(extracted):
    """Kapitel 5, S.37 -- verbundene Zelle steht optisch MITTIG in ihrem
    Pruefidentifikator-Block."""
    entries, _, _ = extracted
    medien = [e for e in entries if e.form_key == "form9-medien"]
    assert {e.code for e in medien} == {"AUA", "FPA", "SOL", "WID"}
    aua = _one(entries, "form9-medien", "AUA")
    assert aua[0].bedeutung == "Ausfallarbeit"
    # Vier PI, im Dokument um das Label herum gestapelt.
    assert aua[0].pruefidentifikatoren == "13020 13022 13023 13026"
    assert _one(entries, "form9-medien", "WID")[0].bedeutung == "Wind"


# ---------------------------------------------------------------------------
# Platzhalter, Sonderfaelle, Nicht-Datenbereich
# ---------------------------------------------------------------------------

def test_platzhalter_bleiben_unveraendert(extracted):
    """Auftrag Abschnitt 8: Codes werden NICHT normalisiert oder expandiert.
    Der Wertebereich von b ist nicht einmal dokumentweit einheitlich
    (0..65 Strom, 0..64 Gas), eine Expansion waere gar nicht moeglich."""
    entries, _, _ = extracted
    codes = {e.code for e in entries}
    for platzhalter in ("7-b:3.0.0", "1-b:1.8.e", "7-0:54.0.ee", "7-b:99.45.e1"):
        assert platzhalter in codes
    # kein Code wurde in konkrete Kanalwerte aufgeloest
    assert "7-0:3.0.0" not in codes or "7-b:3.0.0" in codes


def test_aenderungshistorie_ist_nicht_datenbereich(extracted):
    """Kapitel 7 zitiert OBIS-Kennzahlen und Messprodukt-Codes frueherer
    Staende. Nichts davon darf importiert werden."""
    entries, _, _ = extracted
    assert [e.code for e in entries if e.source_page >= _CHANGELOG_FIRST_PAGE] == []


def test_messprodukt_codes_werden_nicht_importiert(extracted):
    """Form 4 ist laut Befund eine Zuordnungstabelle, keine Werteliste, und
    wurde zurueckgestellt. Kein Messprodukt-Code darf als Codelisteneintrag
    auftauchen."""
    entries, _, _ = extracted
    assert [e.code for e in entries if e.code.startswith("9991")] == []


def test_fehlerhafte_schreibweise_wird_ausgewiesen_nicht_korrigiert(extracted):
    """S.12 enthaelt "1-1:2:29.0" (Doppelpunkt statt Punkt) -- ein Schreibfehler
    des Quelldokuments. Er wird gemeldet, nicht stillschweigend repariert."""
    entries, skipped, _ = extracted
    assert "1-1:2:29.0" not in {e.code for e in entries}
    assert "1-1:2.29.0" not in {e.code for e in entries}, "Wert wurde geraten"
    assert any(s.raw == "1-1:2:29.0" for s in skipped)


# ---------------------------------------------------------------------------
# Import, Provenienz, Idempotenz
# ---------------------------------------------------------------------------

def test_import_legt_codelisten_mit_provenienz_an(db):
    session, version = db
    report = import_obis_codelists(session, str(_PDF), version.id)
    assert report.errors == []
    assert report.codelists_created == _EXPECTED_CODELISTS

    lists = session.query(models.CodeList).all()
    assert len(lists) == _EXPECTED_CODELISTS
    for cl in lists:
        assert cl.regulatory_version_id == version.id
        assert cl.quelle_hash == _SHA256
        assert cl.quelle_dokument.endswith(".pdf")
        assert cl.quelle_kapitel

    entries = session.query(models.CodeListEntry).all()
    assert len(entries) == report.entries_imported
    for e in entries:
        assert e.codelist_id is not None
        assert e.quelle_seite and e.quelle_seite < _CHANGELOG_FIRST_PAGE
        # gueltig_ab aus der RegulatoryVersion, gueltig_bis offen.
        assert e.gueltig_ab == version.valid_from.date()
        assert e.gueltig_bis is None


def test_import_verknuepft_beispiel_korrekt(db):
    session, version = db
    import_obis_codelists(session, str(_PDF), version.id)
    medien = (
        session.query(models.CodeList)
        .filter(models.CodeList.name == "Medien (Redispatch 2.0)")
        .one()
    )
    assert medien.nachrichtentyp == "MSCONS"
    assert medien.quelle_kapitel == "5"
    aua = [e for e in medien.entries if e.code == "AUA"]
    assert len(aua) == 1
    assert aua[0].bedeutung == "Ausfallarbeit"
    assert aua[0].pruefidentifikatoren == "13020 13022 13023 13026"


def test_import_ist_idempotent(db):
    """Zweimaliger Import derselben Datei -> identisches Ergebnis, keine Duplikate."""
    session, version = db
    first = import_obis_codelists(session, str(_PDF), version.id)
    lists_after_first = session.query(models.CodeList).count()
    entries_after_first = session.query(models.CodeListEntry).count()

    # Zweiter Lauf ohne --reimport: sauberer No-op.
    second = import_obis_codelists(session, str(_PDF), version.id)
    assert second.errors, "zweiter Import haette erkannt werden muessen"
    assert session.query(models.CodeList).count() == lists_after_first
    assert session.query(models.CodeListEntry).count() == entries_after_first

    # Erzwungener Re-Import: gleiches Ergebnis, keine Verdopplung.
    third = import_obis_codelists(session, str(_PDF), version.id, reimport=True)
    assert third.errors == []
    assert third.entries_imported == first.entries_imported
    assert session.query(models.CodeList).count() == lists_after_first
    assert session.query(models.CodeListEntry).count() == entries_after_first


def test_keine_fk_auf_process_identifier():
    """Freigabe Punkt 5: die referenzierten PI sind MSCONS-PI (13xxx), der
    Bestand kennt nur UTILMD (44xxx). Es wird bewusst KEINE FK angelegt."""
    assert not hasattr(models.CodeListEntry, "pi_id")
    assert hasattr(models.CodeListEntry, "pruefidentifikatoren")


# ---------------------------------------------------------------------------
# Einheitentests ohne PDF
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("roh,erwartet", [
    ("Lieferbe-\nginn", "Lieferbeginn"),          # Silbentrennung am Umbruch
    ("VDE-AR-N\n4400", "VDE-AR-N 4400"),          # echter Bindestrich bleibt
    ("Z.-St.-Differenz/h", "Z.-St.-Differenz/h"),  # kein Umbruch, unveraendert
    ("  mehrfach   Leerraum ", "mehrfach Leerraum"),
    (None, ""),
])
def test_clean(roh, erwartet):
    assert _clean(roh) == erwartet


def test_split_codes_trennt_mehrfachzellen():
    form = next(f for f in TABLE_FORMS if f.key == "form2-obis-strom")
    assert _split_codes("1-b:1.8.e, 1-b:1.8.63", form) == ["1-b:1.8.e", "1-b:1.8.63"]
    assert _split_codes("--", form) == []
    assert _split_codes("", form) == []
    # Ein Wert, der nicht der Schreibweise entspricht, liefert keinen Code.
    assert _split_codes("1-1:2:29.0", form) == []
