"""Tests der MIG-Extraktion (Issue #46).

Drei Sorten von Tests:

* Fixwert-Tests gegen die ECHTE MIG. Die Werte stammen aus der empirischen
  Strukturanalyse und sind damit ein belastbarer Regressionsanker -- kein Test
  prueft eine Annahme gegen sich selbst.
* Ein Negativtest, der belegt, dass der Parser STRUKTURELL arbeitet: das
  EDIFACT-Beispiel "RFF+Z13:44001'" auf S.53 steht ausserhalb des Blocks und
  darf nicht als PI 44001 gelesen werden. Ein dokumentweiter Volltext-Regex
  wuerde hier durchfallen.
* Einheitentests des Zustandsautomaten mit synthetischen Zeilen. Sie laufen ohne
  PDF und decken die Faelle ab, die im echten Dokument (noch) nicht vorkommen.

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
from app.regulatory_extraction_mig import (
    PiEntry,
    collect_pi_entries,
    extract_pi_entries,
    header_column_index,
    import_mig_process_identifiers,
    is_anchor_qualifier_row,
    is_anchor_row,
    is_page_banner,
)

_BACKEND = Path(__file__).resolve().parents[1]
_PDF = Path(os.getenv(
    "ATLAS_MIG_GAS_G11_PDF",
    _BACKEND / "data" / "regulatory" / "UTILMD_MIG_Gas_G1_1_20251001.pdf",
))

pytestmark = pytest.mark.skipif(
    not _PDF.exists(),
    reason=f"MIG Gas G1.1 nicht vorhanden ({_PDF}) -- siehe data/regulatory/README.md",
)

# Gemessen gegen UTILMD MIG Gas G1.1 (finale Fassung aus BNetzA-Mitteilung 54).
_SHA256 = "f5191a473b650dd6e5de2a673f97b6db685f57de8f6b8d2da7d6ccebb2bfe634"
# Harte Vollstaendigkeitsinvariante (Freigabe Punkt 6): die MIG fuehrt genau
# 91 formale PI -> Bezeichnung-Paare, alle im Pruefidentifikator-Block.
_EXPECTED_ENTRIES = 91
_EXPECTED_PAGES = [51, 52, 53]
_ANCHOR_PAGE = 51
# 52 der 91 Bezeichnungen sind ueber zwei Zeilen umbrochen.
_EXPECTED_MULTILINE = 52
# Reale Werte, unveraendert aus dem Dokument (Auftrag Abschnitt 8).
_REAL_EXAMPLES = {
    "44001": ("GeLi Gas / Anmeldung NN", 51),
    "44019": ("GeLi Gas / Bestandsliste zugeordnete Marktlokationen", 51),
    "44042": ("WiM Gas / Anmeldung MSB", 51),
    "44096": ("TSIMSG / Deklarationsliste an MGV", 52),
    "44103": ("NBW Gas / Stammdaten zur verbrauchenden Marktlokation", 52),
    "44168": ("WiM Gas / Verpflichtungsanfrage / Aufforderung", 53),
    "44182": ("SDÄ Gas / Ablehnung der Anfrage der komplexen Marktlokationsstruktur NB an LF", 53),
}
# Der Eintrag, der ueber den Seitenumbruch laeuft (Freigabe Punkt 8).
_PAGE_BREAK_PI = "44148"
_PAGE_BREAK_NAME = "SDÄ Gas / Anfrage an MSB mit Abhängigkeiten NB [Berechtigt] an MSB"
# Das EDIFACT-Beispiel unterhalb des Blockendes (Freigabe Punkt 9).
_NEGATIVE_EXAMPLE = "RFF+Z13:44001'"

# Kuratierte PIs aus seed_data.py, die in der MIG ebenfalls vorkommen.
_CURATED = {"44001": "Anmeldung Netznutzung", "44019": "Bestandsliste"}


@pytest.fixture(scope="module")
def extraction():
    """Ein Durchlauf ueber 168 Seiten dauert ~20 s -- den teilen sich die Tests."""
    return extract_pi_entries(str(_PDF))


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


def test_entries_carry_document_provenance(extraction):
    """Provenance haengt am Extraktionsdatensatz, nicht am ProcessIdentifier.

    Das Modell wird fuer diesen Schritt nicht erweitert (Freigabe Punkt 1);
    Dokument, Hash und Seite muessen aber schon jetzt mitlaufen, damit eine
    spaetere persistente Provenance den Parser nicht anfasst.
    """
    for entry in extraction.entries:
        assert entry.source_document == _PDF.name
        assert entry.source_document_hash == _SHA256
        assert entry.source_page in _EXPECTED_PAGES


# ---------------------------------------------------------------------------
# Formpruefung
# ---------------------------------------------------------------------------

def test_form_is_recognized_with_a_single_anchor(extraction):
    """Der Anker DE 1154 / "Prüfidentifikator" ist dokumentweit eindeutig.

    18 Zeilen des Dokuments tragen Bez 1154; nur diese eine steht in der
    Auspraegung "Prüfidentifikator".
    """
    assert extraction.form_recognized is True
    assert extraction.anchor_pages == [_ANCHOR_PAGE]
    assert extraction.form_notes == []
    # Der Spaltenindex wird aus der Kopfzeile abgeleitet, nicht angenommen.
    assert extraction.anchor_column_index is not None


def test_block_end_is_detected_at_bemerkung(extraction):
    """Das Blockende ist eine Zeile in einer ANDEREN Spalte, kein Seitenende."""
    assert "Bemerkung:" in extraction.block_end_marker
    assert "S.53" in extraction.block_end_marker


# ---------------------------------------------------------------------------
# Vollstaendigkeit -- harte Invariante 91/91
# ---------------------------------------------------------------------------

def test_all_entries_are_extracted(extraction):
    assert len(extraction.entries) == _EXPECTED_ENTRIES
    assert len({e.pi_number for e in extraction.entries}) == _EXPECTED_ENTRIES
    assert extraction.skipped == []


def test_entries_come_only_from_the_pi_block(extraction):
    """Keine Treffer ausserhalb des definierten Blocks."""
    assert extraction.pages == _EXPECTED_PAGES


def test_multiline_designations_are_merged(extraction):
    assert extraction.multiline_entries == _EXPECTED_MULTILINE
    assert max(e.source_lines for e in extraction.entries) == 2


@pytest.mark.parametrize("pi_number", sorted(_REAL_EXAMPLES))
def test_real_examples_are_extracted_verbatim(extraction, pi_number):
    """Originalbezeichnung, keine fachliche Interpretation (Auftrag Abschnitt 8)."""
    expected_name, expected_page = _REAL_EXAMPLES[pi_number]
    found = [e for e in extraction.entries if e.pi_number == pi_number]
    assert len(found) == 1, f"PI {pi_number} nicht genau einmal gefunden"
    assert found[0].process_name == expected_name
    assert found[0].source_page_start == expected_page


# ---------------------------------------------------------------------------
# Pflichtfall 1: Eintrag ueber den Seitenumbruch (Freigabe Punkt 8)
# ---------------------------------------------------------------------------

def test_entry_spanning_a_page_break_is_merged(extraction):
    """44148 beginnt auf S.52, die Fortsetzung steht auf S.53.

    Der Parser darf Seitenende nicht mit Eintragsende gleichsetzen. Faellt
    dieser Test, ist der Zustand ueber die Seitengrenze verlorengegangen.
    """
    found = [e for e in extraction.entries if e.pi_number == _PAGE_BREAK_PI]
    assert len(found) == 1
    entry = found[0]
    assert entry.process_name == _PAGE_BREAK_NAME
    assert entry.source_page_start == 52
    assert entry.source_page == 53
    assert entry.spans_page_break is True
    assert entry.source_lines == 2
    # Die Fortsetzungszeile darf nicht als eigener Eintrag aufgetaucht sein.
    assert not any(e.process_name.startswith("NB [Berechtigt]") for e in extraction.entries)


def test_exactly_one_entry_spans_a_page_break(extraction):
    spanning = [e.pi_number for e in extraction.entries if e.spans_page_break]
    assert spanning == [_PAGE_BREAK_PI]


# ---------------------------------------------------------------------------
# Pflichtfall 2: Negativtest RFF+Z13:44001' (Freigabe Punkt 9)
# ---------------------------------------------------------------------------

def test_edifact_example_is_not_read_as_a_pi(extraction):
    """Das Beispiel "RFF+Z13:44001'" steht unterhalb des Blockendes.

    Es enthaelt die Zeichenfolge 44001 und wuerde von einem dokumentweiten
    Volltext-Regex mitgenommen. Der Parser arbeitet strukturell: 44001 darf
    genau einmal vorkommen -- von S.51, mit der dortigen Bezeichnung.
    """
    matches = [e for e in extraction.entries if e.pi_number == "44001"]
    assert len(matches) == 1
    assert matches[0].source_page_start == _ANCHOR_PAGE
    assert matches[0].process_name == _REAL_EXAMPLES["44001"][0]
    # Gegenprobe: das Beispiel steht wirklich im Dokument, der Test ist also
    # nicht deshalb gruen, weil die Zeichenfolge gar nicht vorkommt.
    import pdfplumber
    with pdfplumber.open(str(_PDF)) as pdf:
        page_text = pdf.pages[52].extract_text() or ""
    assert _NEGATIVE_EXAMPLE in page_text


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def test_import_creates_new_and_preserves_curated_names(db):
    """Abschnitt 15, Fall C: bestehende Namen bleiben unveraendert.

    "44001" heisst in Atlas kuratiert "Anmeldung Netznutzung", in der MIG
    "GeLi Gas / Anmeldung NN". Das ist KEIN regulatorischer Konflikt -- die
    Herkunft des bestehenden Namens ist im heutigen Schema nicht feststellbar.
    """
    group = models.ProcessGroup(code="registration", name="Anmeldung")
    db.add(group)
    db.flush()
    for pi_number, name in _CURATED.items():
        db.add(models.ProcessIdentifier(
            pi_number=pi_number, name=name, process_group_id=group.id,
            sender_role="LF", receiver_role="NB", criticality="kritisch", weight=3.0,
        ))
    db.commit()
    version = db.query(models.RegulatoryVersion).first()

    report = import_mig_process_identifiers(db, str(_PDF), version.id)

    assert report.errors == []
    assert report.conflicts == []
    assert report.entries_detected == _EXPECTED_ENTRIES
    assert len(report.created) == _EXPECTED_ENTRIES - len(_CURATED)
    assert len(report.existing_name_preserved) == len(_CURATED)
    assert db.query(models.ProcessIdentifier).count() == _EXPECTED_ENTRIES

    # Kuratierte Datensaetze vollstaendig unveraendert -- Name UND Beiwerk.
    for pi_number, name in _CURATED.items():
        kept = db.query(models.ProcessIdentifier).filter_by(pi_number=pi_number).one()
        assert kept.name == name
        assert kept.process_group_id == group.id
        assert kept.sender_role == "LF"

    # Neue PIs tragen nur, was die MIG belegt (Freigabe Punkte 2 und 3).
    fresh = db.query(models.ProcessIdentifier).filter_by(pi_number="44148").one()
    assert fresh.name == _PAGE_BREAK_NAME
    assert fresh.process_group_id is None
    assert fresh.sender_role is None
    assert fresh.receiver_role is None
    assert fresh.criticality == "mittel"
    assert fresh.weight == 1.0


def test_import_is_idempotent(db):
    """Zweiter Lauf: keine Duplikate, keine Aenderung (Freigabe Punkt 10)."""
    version = db.query(models.RegulatoryVersion).first()

    first = import_mig_process_identifiers(db, str(_PDF), version.id)
    after_first = db.query(models.ProcessIdentifier).count()
    snapshot = {p.pi_number: p.name for p in db.query(models.ProcessIdentifier).all()}

    second = import_mig_process_identifiers(db, str(_PDF), version.id)
    after_second = db.query(models.ProcessIdentifier).count()

    assert len(first.created) == _EXPECTED_ENTRIES
    assert second.created == []
    assert len(second.existing_name_preserved) == _EXPECTED_ENTRIES
    assert after_first == after_second == _EXPECTED_ENTRIES
    assert {p.pi_number: p.name for p in db.query(models.ProcessIdentifier).all()} == snapshot
    assert second.conflicts == []


def test_import_skips_when_version_is_unknown(db):
    report = import_mig_process_identifiers(db, str(_PDF), 9999)
    assert report.errors
    assert db.query(models.ProcessIdentifier).count() == 0


# ---------------------------------------------------------------------------
# Zustandsautomat -- synthetische Zeilen, kein PDF noetig
# ---------------------------------------------------------------------------

_HEADER = ["Bez", "Name", "St", "Format", "St", "Format", "Anwendung / Bemerkung"]
_BANNER = ["Standard", None, None, None, "BDEW", None, None]
_Q1153 = ["1153", "Referenz, Qualifier", "M", "an..3", "M", "an..3", "Z13 Prüfidentifikator"]
_A1154 = ["1154", "Referenz, Identifikation", "C", "an..70", "R", "n5", "Prüfidentifikator"]


def _rows(*rows, page=1, table=1):
    return [(page, table, row) for row in rows]


def test_header_index_is_read_from_the_header_row():
    assert header_column_index(_HEADER) == 6
    wide = ["Bez", "Name", None, None, "St", "Format", "St", "Format", "Anwendung / Bemerkung", None]
    assert header_column_index(wide) == 8
    # Zielzelle allein genuegt nicht -- "Bez" und "Name" muessen dabei sein.
    assert header_column_index(["Anwendung / Bemerkung"]) is None
    assert header_column_index(_BANNER) is None


def test_row_classifiers():
    assert is_page_banner(_BANNER) is True
    assert is_page_banner(_HEADER) is False
    assert is_anchor_row(_A1154, 6) is True
    assert is_anchor_row(_Q1153, 6) is False
    assert is_anchor_qualifier_row(_Q1153, 6) is True


def test_anchor_without_qualifier_row_is_not_used():
    """Der Anker haengt an zwei Merkmalen, nicht an einer Zelle."""
    result = collect_pi_entries(iter(_rows(
        _HEADER, _A1154,
        [None] * 6 + ["44001 GeLi Gas / Anmeldung NN"],
    )))
    assert result.form_recognized is False
    assert result.entries == []
    assert any("ohne vorangehende" in note for note in result.form_notes)


def test_missing_anchor_leads_to_skip():
    result = collect_pi_entries(iter(_rows(
        _HEADER,
        ["1154", "Referenz, Identifikation", "C", "an..70", "R", "n5", "Vorgangsnummer"],
        [None] * 6 + ["44001 GeLi Gas / Anmeldung NN"],
    )))
    assert result.form_recognized is False
    assert result.entries == []
    assert any("nicht gefunden" in note for note in result.form_notes)


def test_second_anchor_leads_to_skip():
    """Zwei Anker = geaenderte Dokumentform -> nichts importieren, nicht raten."""
    result = collect_pi_entries(iter(
        _rows(_HEADER, _Q1153, _A1154, [None] * 6 + ["44001 GeLi Gas / Anmeldung NN"],
              ["C506", "Referenz", "M", "", "M", "", ""])
        + _rows(_HEADER, _Q1153, _A1154, [None] * 6 + ["44002 GeLi Gas / X"], page=9)
    ))
    assert result.form_recognized is False
    assert result.entries == []
    assert len(result.anchor_pages) == 2
    assert any("zweiter Anker" in note for note in result.form_notes)


def test_repeated_headers_do_not_end_the_block():
    """Banner und Kopfzeile auf der Folgeseite duerfen den Block nicht beenden."""
    result = collect_pi_entries(iter(
        _rows(_HEADER, _Q1153, _A1154,
              [None] * 6 + ["44001 GeLi Gas / Anmeldung NN"],
              [None] * 6 + ["44019 GeLi Gas / Bestandsliste zugeordnete"])
        + _rows(_BANNER, _HEADER,
                [None] * 6 + ["Marktlokationen"],
                [None] * 6 + ["44020 GeLi Gas / Änderung"],
                ["Bemerkung:", None, None, None, None, None, None], page=2)
    ))
    assert result.form_recognized is True
    assert [e.pi_number for e in result.entries] == ["44001", "44019", "44020"]
    merged = result.entries[1]
    assert merged.process_name == "GeLi Gas / Bestandsliste zugeordnete Marktlokationen"
    assert merged.spans_page_break is True


def test_hyphenated_designation_is_not_guessed():
    """Am Zeilenende getrenntes Wort -> nicht zusammenraten (Abschnitt 14)."""
    result = collect_pi_entries(iter(_rows(
        _HEADER, _Q1153, _A1154,
        [None] * 6 + ["44001 GeLi Gas / Anmeldung NN"],
        [None] * 6 + ["44002 GeLi Gas / Geschäftsdatenanfra-"],
        [None] * 6 + ["ge"],
        ["Bemerkung:", None, None, None, None, None, None],
    )))
    assert [e.pi_number for e in result.entries] == ["44001"]
    assert len(result.skipped) == 1
    assert "getrennt" in result.skipped[0].reason


def test_duplicate_pi_with_diverging_name_is_reported_not_decided(db):
    """Abschnitt 14: nicht ueberschreiben, nicht selbst entscheiden."""
    version = db.query(models.RegulatoryVersion).first()
    extraction_stub = [
        PiEntry(pi_number="44001", process_name="A", source_page=51),
        PiEntry(pi_number="44001", process_name="B", source_page=52),
    ]
    # Der Konfliktzweig wird ueber die Reportstruktur geprueft, ohne dafuer ein
    # zweites PDF zu erfinden.
    from app import regulatory_extraction_mig as mig

    original = mig.extract_pi_entries
    try:
        mig.extract_pi_entries = lambda path: mig.PiExtraction(
            form_recognized=True, anchor_pages=[51], anchor_column_index=6,
            entries=extraction_stub,
        )
        report = mig.import_mig_process_identifiers(db, str(_PDF), version.id)
    finally:
        mig.extract_pi_entries = original

    assert report.created == []
    assert len(report.conflicts) == 1
    assert "44001" in report.conflicts[0]
    assert db.query(models.ProcessIdentifier).count() == 0
