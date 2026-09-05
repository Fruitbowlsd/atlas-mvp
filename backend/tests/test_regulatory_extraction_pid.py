"""Tests der PID-Extraktion (Issue #54, Scoping A).

Vier Sorten von Tests:

* Fixwert-Tests gegen die ECHTE PID 3.3. Die Werte stammen aus der empirischen
  Strukturanalyse (docs/befund_pid_uebersicht.md) und sind damit ein
  belastbarer Regressionsanker -- kein Test prueft eine Annahme gegen sich
  selbst.
* Der Konsistenzabgleich mit Prompt 1 (Auftrag Abschnitt 9/17): mindestens ein
  Fall ohne Abweichung und mindestens ein dokumentierter Abweichungsfall aus
  dem echten Dokument.
* Ein Idempotenztest: zweimal importieren darf nichts veraendern.
* Einheitentests der Formpruefung mit synthetischen Tabellen. Sie laufen ohne
  PDF und decken die Faelle ab, die im echten Dokument (noch) nicht vorkommen --
  vor allem das in Abschnitt 16 geforderte Verhalten bei einem neuen oder
  geaenderten Tabellenkonzept.

Die PDF-abhaengigen Tests ueberspringen sich selbst, wenn die Datei nicht
vorliegt; sie ist aus Groessengruenden nicht im Repository (siehe
data/regulatory/README.md).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.regulatory_extraction import compute_file_hash
from app.regulatory_extraction_pid import (
    COL_AHB,
    COL_TRANSPORT,
    MAIN_COLUMNS,
    TABLE_CONCEPTS,
    classify_discrepancy,
    collect_pid_rows,
    compare_with_mig,
    extract_pid,
    flatten,
    header_fingerprint,
    import_pid_process_identifiers,
    message_type_of,
    pid_message_types,
    pid_names_by_number,
)

_BACKEND = Path(__file__).resolve().parents[1]
_PDF = Path(os.getenv(
    "ATLAS_PID_UEBERSICHT_PDF",
    _BACKEND / "data" / "regulatory" / "PID_3_3_Konsultationsfassung_20250801.pdf",
))
_MIG_PDF = Path(os.getenv(
    "ATLAS_MIG_GAS_G11_PDF",
    _BACKEND / "data" / "regulatory" / "UTILMD_MIG_Gas_G1_1_20251001.pdf",
))

pytestmark = pytest.mark.skipif(
    not _PDF.exists(),
    reason=f"PID 3.3 nicht vorhanden ({_PDF}) -- siehe data/regulatory/README.md",
)

# Gemessen gegen die Anwendungsuebersicht der Pruefidentifikatoren 3.3
# (Konsultationsfassung vom 01.08.2025, BNetzA-Mitteilung 52/54).
_SHA256 = "6b4f5e362703d481a4e362f19abd43c197dc5d1b1643750b4a59cb92d9c7139a"

# Harte Vollstaendigkeitsinvarianten aus dem Befund.
_EXPECTED_ROWS = 1370
_EXPECTED_ROWS_WITH_PI = 1312
_EXPECTED_PI_COUNT = 486
_EXPECTED_API_ROWS = 27
_MAIN_PAGES = (7, 77)

# Zeilenzahl je Tabellenkonzept, in Dokumentreihenfolge. Die Erweiterte
# Zuordnungslogik hat 9 Datenzeilen plus 5 Nicht-Datenzeilen (Leerzeile,
# "Legende:", drei Legendeneintraege) -- gezaehlt wird hier der Rohbestand.
_CONCEPT_ROWS = {
    "pi_zu_prozessschritt": 1370,
    "tupel_uebersicht": 68,
    "objekteigenschaften": 11,
    "erweiterte_zuordnungslogik": 14,
    "aenderungshistorie": 6,
}

# Reale Werte, unveraendert aus dem Dokument (Auftrag Abschnitt 8).
# Bewusst ueber mehrere Nachrichtentypen gestreut -- die PID ist nicht auf
# UTILMD beschraenkt.
_REAL_EXAMPLES = {
    "13005": ("EEG-Überf.-ZR", "MSCONS AHB", 7),
    "19301": ("Abl. der Anforderung", "ORDRSP AHB", 8),
    "33001": ("Bestätigung", "REMADV AHB", 15),
    "55066": ("Korrekturliste zu Lieferantenclearingliste", "UTILMD AHB Strom", 16),
    "21038": ("Ansicht BTR", "IFTSTA AHB", 24),
    "44001": ("Anmeldung NN", "UTILMD AHB Gas", 70),
}

# Nicht aufloesbare Verweise -- ausgewiesen, nicht geraten (Abschnitt 14).
_UNRESOLVED_TUPLE = "ZG-T33"
_UNRESOLVED_TUPLE_ROWS = 9
_UNRESOLVED_REACTION_PI = "44108"
_EXPECTED_FREETEXT_ASSIGNMENTS = 42

# Der einzige PI mit zwei Schreibweisen in derselben Quelle.
_AMBIGUOUS_PI = "55672"

# Nachrichtentypen aus der AHB-Spalte. Atlas braucht alle Formate, nicht nur
# UTILMD -- die PID fuehrt 16 verschiedene. Zahlen je Typ ueber alle 486 PIs.
_MESSAGE_TYPES = {
    "UTILMD": 275, "ORDERS": 46, "ORDRSP": 40, "IFTSTA": 35, "MSCONS": 25,
    "PARTIN": 14, "INVOIC": 11, "INSRPT": 8, "UTILTS": 8, "REQOTE": 5,
    "QUOTES": 5, "REMADV": 4, "PRICAT": 3, "ORDCHG": 3, "COMDIS": 2,
    "SSQNOT": 2,
}

# Abgleich mit Prompt 1 (Abschnitt 9).
_MIG_COMMON = 88
_MIG_PREFIX_ONLY = 43
_MIG_WORDING = 45
_MIG_ONLY = ["44096", "44097", "44172"]
# Ein Fall ohne inhaltliche Abweichung -- nur das Prozessfamilien-Praefix der MIG.
_PREFIX_CASE = ("44001", "GeLi Gas / Anmeldung NN", "Anmeldung NN")
# Ein Fall mit tatsaechlich abweichendem Wortlaut.
_WORDING_CASE = ("44010", "GeLi Gas / Abmeldeanfrage des NB", "Abmeldungsanfrage des NB")
# Zwei PIs, die dieselbe PID-Beschreibung tragen -- der Beleg dafuer, dass die
# PID-Bezeichnung ohne ihre Nachbarspalten nicht eindeutig ist.
_NON_UNIQUE_DESCRIPTION = ("44147", "44148", "Anfrage an MSB mit Abhängigkeiten")


@pytest.fixture(scope="module")
def extraction():
    """Ein Durchlauf ueber 82 Seiten dauert ~15 s -- den teilen sich die Tests."""
    return extract_pid(str(_PDF))


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    version = models.RegulatoryVersion(
        name="GeLi Gas 2.0 / UTILMD Gas G1.1", sector="gas", status="final", is_active=True
    )
    session.add(version)
    session.commit()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def test_file_hash_is_stable():
    assert compute_file_hash(str(_PDF)) == _SHA256


def test_rows_carry_document_provenance(extraction):
    """Dokument, Hash und Seite laufen an jeder Zeile mit.

    Das Modell wird fuer diesen Schritt nicht erweitert (Freigabe Scoping A);
    die Provenance haengt deshalb am Extraktionsdatensatz.
    """
    for row in extraction.rows:
        assert row.source_document == _PDF.name
        assert row.source_document_hash == _SHA256
        assert _MAIN_PAGES[0] <= row.source_page <= _MAIN_PAGES[1]


# ---------------------------------------------------------------------------
# Formpruefung ueber das gesamte Dokument
# ---------------------------------------------------------------------------

def test_form_is_recognized(extraction):
    assert extraction.form_recognized is True
    assert extraction.form_notes == []


def test_all_five_table_concepts_are_recognized(extraction):
    """Das Dokument nennt auf S. 2 fuenf Tabellen -- genau die muessen es sein."""
    found = {c.key: c for c in extraction.concepts}
    assert set(found) == {c.key for c in TABLE_CONCEPTS}
    for concept in TABLE_CONCEPTS:
        assert found[concept.key].recognized is True, concept.heading
        assert found[concept.key].data_rows == _CONCEPT_ROWS[concept.key]


def test_only_the_main_table_is_processed(extraction):
    """Scoping A: vier der fuenf Konzepte werden gelesen, aber nicht verarbeitet."""
    processed = {c.key for c in extraction.concepts if c.processed}
    assert processed == {"pi_zu_prozessschritt"}
    # Die zurueckgestellten Konzepte sind trotzdem gezaehlt -- kein PID-Feld
    # geht stillschweigend verloren.
    assert extraction.deferred_rows == {
        k: v for k, v in _CONCEPT_ROWS.items() if k != "pi_zu_prozessschritt"
    }


def test_change_history_is_read_but_not_processed(extraction):
    """Abschnitt 11: Aenderungshistorie nur vermerkt, nicht verarbeitet."""
    history = next(c for c in extraction.concepts if c.key == "aenderungshistorie")
    assert history.recognized is True
    assert history.processed is False
    assert history.pages == [82]


# ---------------------------------------------------------------------------
# Vollstaendigkeit -- harte Invarianten
# ---------------------------------------------------------------------------

def test_all_rows_are_extracted(extraction):
    assert len(extraction.rows) == _EXPECTED_ROWS
    assert len(extraction.rows_with_pi) == _EXPECTED_ROWS_WITH_PI
    assert len(extraction.pi_numbers) == _EXPECTED_PI_COUNT


def test_every_row_has_all_columns(extraction):
    """Anders als MIG und AHB liefert extract_tables() hier saubere Zellen."""
    for row in extraction.rows:
        assert len(row.values) == len(MAIN_COLUMNS)


def test_api_webservice_rows_have_no_pi(extraction):
    """Der API-Zweig steckt in derselben Tabelle und traegt keinen PI.

    Version 3.1 soll dafuer eine eigene Tabelle gehabt haben; in 3.3 sind es
    Zeilen mit Uebertragungsweg "API".
    """
    api_rows = extraction.api_rows
    assert len(api_rows) == _EXPECTED_API_ROWS
    for row in api_rows:
        assert row.pi_number == ""
        assert row.text(COL_TRANSPORT) == "API"
    assert all(r.pi_number == "" for r in extraction.rows_without_pi)


@pytest.mark.parametrize("pi_number", sorted(_REAL_EXAMPLES))
def test_real_examples_are_extracted_verbatim(extraction, pi_number):
    """Originalwert, keine fachliche Interpretation (Auftrag Abschnitt 8)."""
    expected_name, expected_ahb, expected_page = _REAL_EXAMPLES[pi_number]
    rows = [r for r in extraction.rows_with_pi if r.pi_number == pi_number]
    assert rows, f"PI {pi_number} nicht gefunden"
    assert any(
        flatten(r.description) == expected_name and r.source_page == expected_page
        for r in rows
    ), f"PI {pi_number} nicht mit erwarteter Bezeichnung auf S.{expected_page}"
    # Die AHB-Zuordnung ist je PI eindeutig -- das ist die einzige Angabe, die
    # die PID ueber alle Zeilen eines PI hinweg widerspruchsfrei fuehrt.
    assert {r.text(COL_AHB) for r in rows} == {expected_ahb}


def test_footnote_column_is_empty_in_this_version(extraction):
    """Spalte 20 existiert, traegt aber dokumentweit keinen Wert.

    Bewusst als Test festgehalten: taucht in einer kuenftigen Version dort ein
    Wert auf, ist das eine inhaltliche Erweiterung, die auffallen soll.
    """
    assert all(not r.raw(20) for r in extraction.rows)


# ---------------------------------------------------------------------------
# Nicht aufloesbare Verweise (Abschnitt 14 -- ausweisen statt raten)
# ---------------------------------------------------------------------------

def test_undefined_tuple_reference_is_reported(extraction):
    """ZG-T33 wird neunmal verwendet, ist aber nicht definiert.

    ZO-T33 existiert; ob es ein Tippfehler ist, ist nicht entscheidbar und
    wird deshalb nicht "korrigiert".
    """
    hits = [u for u in extraction.unresolved if u.value == _UNRESOLVED_TUPLE]
    assert len(hits) == _UNRESOLVED_TUPLE_ROWS
    assert all(u.kind == "Tupel-Kennzeichnung" for u in hits)


def test_unresolvable_reaction_pi_is_reported(extraction):
    """PI 44108 erscheint nur als Reaktionsziel, nie als eigener Anwendungsfall."""
    hits = [u for u in extraction.unresolved
            if u.kind == "Reaktion auf Prüfidentifikator"]
    assert [u.value for u in hits] == [_UNRESOLVED_REACTION_PI]
    assert _UNRESOLVED_REACTION_PI not in extraction.pi_numbers


def test_conditional_assignment_cells_are_reported_not_parsed(extraction):
    """42 Zuordnungszellen enthalten Bedingungsfreitext statt eines Codes.

    Sie werden gemeldet und im Rohwert belassen -- ein Zerlegen in Codes waere
    fachliche Interpretation.
    """
    assert len(extraction.freetext_assignments) == _EXPECTED_FREETEXT_ASSIGNMENTS
    texts = [t for _, _, t in extraction.freetext_assignments]
    assert any("bei SG4 STS+E01++A04 dann ZO-T1" in t for t in texts)


# ---------------------------------------------------------------------------
# Abgleich mit Prompt 1 (Auftrag Abschnitt 9 und 17)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _MIG_PDF.exists(), reason=f"MIG nicht vorhanden ({_MIG_PDF})")
def test_mig_consistency_check_against_real_documents(db, extraction):
    """Beide echten Quellen gegeneinander -- Prompt 1 gegen Prompt 5.

    Deckt die in Abschnitt 17 geforderten Faelle ab: mindestens einen ohne
    inhaltliche Abweichung (nur Praefix) und mindestens einen mit abweichendem
    Wortlaut.
    """
    report = import_pid_process_identifiers(
        db, str(_PDF), 1, mig_pdf_path=str(_MIG_PDF)
    )
    assert report.mig_document == _MIG_PDF.name
    common = len(report.mig_agreements) + len(report.mig_discrepancies)
    assert common == _MIG_COMMON
    assert report.mig_only == _MIG_ONLY
    prefix = [d for d in report.mig_discrepancies if d.prefix_only]
    wording = [d for d in report.mig_discrepancies if not d.prefix_only]
    assert len(prefix) == _MIG_PREFIX_ONLY
    assert len(wording) == _MIG_WORDING

    pi_number, mig_name, pid_name = _PREFIX_CASE
    hit = next(d for d in prefix if d.pi_number == pi_number)
    assert (hit.mig_name, hit.pid_name) == (mig_name, pid_name)

    pi_number, mig_name, pid_name = _WORDING_CASE
    hit = next(d for d in wording if d.pi_number == pi_number)
    assert (hit.mig_name, hit.pid_name) == (mig_name, pid_name)


def test_pid_description_is_not_unique_per_pi(extraction):
    """Der Grund, warum ProcessIdentifier.name nicht aus der PID kommt.

    44147 und 44148 tragen dieselbe PID-Beschreibung; unterschieden werden sie
    erst durch Kommunikation von/an. Die MIG dagegen fuehrt die Rollenrichtung
    im Namen.
    """
    first, second, description = _NON_UNIQUE_DESCRIPTION
    names = pid_names_by_number(extraction)
    assert names[first] == {description}
    assert names[second] == {description}


def test_classify_discrepancy_distinguishes_prefix_from_wording():
    """Einheitentest ohne PDF -- die Einstufung entscheidet nichts, sie meldet."""
    assert classify_discrepancy("GeLi Gas / Anmeldung NN", "Anmeldung NN") == "praefix"
    assert classify_discrepancy("SDÄ Gas / Antwort auf Anfrage", "Antwort") == "wortlaut"
    assert classify_discrepancy("Anmeldung NN", "Anmeldung NN") is None


def test_compare_with_mig_prefers_the_heavier_classification():
    """Mehrere PID-Schreibweisen: eine Wortlautabweichung darf nicht hinter
    einer Praefixdifferenz verschwinden."""
    agreements, discrepancies, mig_only = compare_with_mig(
        {"44001": {"Anmeldung NN", "Anmeldung"}, "44002": {"Bestätigung Anmeldung"}},
        {"44001": "GeLi Gas / Anmeldung NN", "44003": "GeLi Gas / Ablehnung"},
    )
    assert agreements == []
    assert [d.pi_number for d in discrepancies] == ["44001"]
    assert discrepancies[0].kind == "wortlaut"
    assert mig_only == ["44003"]


# ---------------------------------------------------------------------------
# Import -- Fall A/B/C aus Prompt 1
# ---------------------------------------------------------------------------

def test_import_creates_new_pis_and_preserves_existing(db, extraction):
    """Fall C: ein bestehender ProcessIdentifier wird nie veraendert."""
    db.add(models.ProcessIdentifier(
        pi_number="44001", name="Anmeldung Netznutzung",
        sender_role="LF", receiver_role="NB", message_type="UTILMD",
    ))
    db.commit()

    report = import_pid_process_identifiers(db, str(_PDF), 1)
    assert report.errors == []

    kept = db.query(models.ProcessIdentifier).filter_by(pi_number="44001").one()
    assert kept.name == "Anmeldung Netznutzung"
    assert (kept.sender_role, kept.receiver_role) == ("LF", "NB")
    assert kept.message_type == "UTILMD"
    assert "44001" in [pi for pi, _, _ in report.existing_name_preserved]
    assert "44001" not in report.created


def test_ambiguous_description_is_not_guessed(db):
    """PI 55672 hat zwei Schreibweisen in derselben Quelle -- also kein Import."""
    report = import_pid_process_identifiers(db, str(_PDF), 1)
    assert _AMBIGUOUS_PI not in report.created
    assert db.query(models.ProcessIdentifier).filter_by(
        pi_number=_AMBIGUOUS_PI).one_or_none() is None
    assert any(_AMBIGUOUS_PI in c for c in report.conflicts)
    assert len(report.created) == _EXPECTED_PI_COUNT - 1


def test_new_pis_carry_only_what_the_pid_proves(db):
    """Keine geratenen Werte: Rollen und Prozessgruppe bleiben leer."""
    import_pid_process_identifiers(db, str(_PDF), 1)
    created = db.query(models.ProcessIdentifier).filter_by(pi_number="13005").one()
    assert created.name == "EEG-Überf.-ZR"
    assert created.process_group_id is None
    assert created.sender_role is None
    assert created.receiver_role is None


def test_message_type_covers_all_formats_not_just_utilmd(db):
    """Atlas braucht alle Formate -- der Modell-Default "UTILMD" wäre falsch.

    Die AHB-Spalte nennt das Anwendungshandbuch, dessen Name mit dem
    EDIFACT-Nachrichtentyp beginnt. Die Entnahme ist strukturell, nicht
    interpretiert, und je PI widerspruchsfrei.
    """
    report = import_pid_process_identifiers(db, str(_PDF), 1)
    # 55672 wird wegen zweier Schreibweisen nicht importiert; sein Typ zählt
    # deshalb nicht mit.
    expected = dict(_MESSAGE_TYPES)
    expected["UTILMD"] -= len(report.existing_name_preserved)
    expected["UTILMD"] -= 1   # 55672, Konflikt
    assert report.message_types == expected
    assert report.message_type_missing == []

    by_number = {
        pi.pi_number: pi.message_type
        for pi in db.query(models.ProcessIdentifier).all()
    }
    assert by_number["13005"] == "MSCONS"    # MSCONS AHB
    assert by_number["21038"] == "IFTSTA"    # IFTSTA AHB
    assert by_number["19301"] == "ORDRSP"    # ORDRSP AHB
    assert by_number["55066"] == "UTILMD"    # UTILMD AHB Strom
    assert by_number["70096"] == "SSQNOT"    # "SSQNOT zur Übermittlung von …"
    assert len({t for t in by_number.values() if t}) == len(_MESSAGE_TYPES)


def test_message_type_matches_what_atlas_already_knows(db, extraction):
    """Gegenprobe: die PID widerspricht bei keinem bekannten PI dem Bestand."""
    db.add(models.ProcessIdentifier(
        pi_number="44001", name="Anmeldung Netznutzung", message_type="UTILMD",
    ))
    db.commit()
    report = import_pid_process_identifiers(db, str(_PDF), 1)
    assert not any("Nachrichtentyp" in c for c in report.conflicts)
    assert pid_message_types(extraction)["44001"] == "UTILMD"


def test_message_type_is_left_empty_when_not_derivable():
    """Kein Rateversuch: was nicht mit einem Nachrichtentyp beginnt, bleibt leer."""
    assert message_type_of("MSCONS AHB") == "MSCONS"
    assert message_type_of("UTILMD AHB Strom") == "UTILMD"
    assert message_type_of("SSQNOT zur Übermittlung von Mehr-/Mindermengen") == "SSQNOT"
    assert message_type_of("API-Webdienste zur prozessualen Abwicklung") is None
    assert message_type_of("--") is None
    assert message_type_of("") is None


def test_import_is_idempotent(db):
    """Zweiter Lauf legt nichts an und veraendert nichts (Abschnitt 18)."""
    first = import_pid_process_identifiers(db, str(_PDF), 1)
    after_first = {
        pi.pi_number: (pi.name, pi.sender_role, pi.message_type)
        for pi in db.query(models.ProcessIdentifier).all()
    }
    assert len(after_first) == len(first.created)

    second = import_pid_process_identifiers(db, str(_PDF), 1)
    after_second = {
        pi.pi_number: (pi.name, pi.sender_role, pi.message_type)
        for pi in db.query(models.ProcessIdentifier).all()
    }
    assert second.created == []
    assert len(second.existing_name_preserved) == len(first.created)
    assert after_second == after_first


def test_import_refuses_unknown_regulatory_version(db):
    report = import_pid_process_identifiers(db, str(_PDF), 999)
    assert report.errors
    assert report.created == []


# ---------------------------------------------------------------------------
# Formpruefung -- synthetische Faelle (Abschnitt 16, ohne PDF)
# ---------------------------------------------------------------------------

_MAIN = TABLE_CONCEPTS[0]


def _main_table(*data_rows):
    return [list(_MAIN.header), *[list(r) for r in data_rows]]


def _row(overrides):
    """Eine synthetische Datenzeile: {Spaltenindex: Wert}, Rest leer."""
    values = [""] * len(MAIN_COLUMNS)
    for index, value in overrides.items():
        values[index] = value
    return values


def test_unknown_table_concept_is_reported_not_ignored():
    """Abschnitt 16: ein neu hinzukommendes Konzept muss auffallen."""
    tables = [
        (7, _MAIN.heading, _main_table(_row({0: "1", 3: "44001", 2: "Anmeldung NN"}))),
        (83, "Neue Zuordnungstabelle", [["A", "B"], ["1", "2"]]),
    ]
    result = collect_pid_rows(iter(tables))
    assert result.form_recognized is True   # die Haupttabelle bleibt gueltig
    assert any("unbekanntes Tabellenkonzept" in n for n in result.form_notes)
    unknown = [c for c in result.concepts if not c.recognized]
    assert [c.heading for c in unknown] == ["Neue Zuordnungstabelle"]


def test_changed_header_makes_the_main_table_unrecognized():
    """Eine geaenderte Kopfzeile fuehrt zu SKIP, nicht zu Rateversuchen."""
    header = list(_MAIN.header)
    header[3] = "Prüf-Identifikator"
    tables = [(7, _MAIN.heading, [header, _row({3: "44001", 2: "Anmeldung NN"})])]
    result = collect_pid_rows(iter(tables))
    assert result.form_recognized is False
    assert result.rows == []
    assert any("Kopfzeile" in n for n in result.form_notes)


def test_missing_concept_is_reported_but_main_table_still_imports():
    """Fehlt ein Nebenkonzept, ist das eine Meldung -- kein Grund, die
    vollstaendige Haupttabelle zu verwerfen."""
    tables = [(7, _MAIN.heading, _main_table(_row({0: "1", 3: "44001", 2: "Anmeldung NN"})))]
    result = collect_pid_rows(iter(tables))
    assert result.form_recognized is True
    assert len(result.rows) == 1
    assert sum("fehlt in diesem Dokumentstand" in n for n in result.form_notes) == 4


def test_pages_without_a_heading_are_not_data():
    """Die Legendentabelle der Einleitung (S. 5) ist kein Datenbereich."""
    tables = [
        (5, None, [["Kürzel", "Bedeutung"], ["AS4", "Übertragungsweg …"]]),
        (7, _MAIN.heading, _main_table(_row({0: "1", 3: "44001", 2: "Anmeldung NN"}))),
    ]
    result = collect_pid_rows(iter(tables))
    assert len(result.rows) == 1
    assert result.rows[0].pi_number == "44001"


def test_header_fingerprint_keeps_rotated_cells_verbatim():
    """Die gedrehten Kopfzellen werden verglichen, nicht entziffert."""
    assert header_fingerprint([" Lfd. Nr. ", "m\no\nrtS\ne\ntra\np\nS", None]) == (
        "Lfd. Nr.", "mortSetrapS", "",
    )


def test_flatten_does_not_invent_word_boundaries():
    """Zerrissene Woerter bleiben zerrissen -- beide Reparaturen waeren geraten."""
    assert flatten("Marktraumumstell\nung") == "Marktraumumstell ung"
    assert flatten("Geschäftsprozesse\nfür EEG-") == "Geschäftsprozesse für EEG-"
