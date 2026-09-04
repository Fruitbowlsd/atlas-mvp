"""Tests der MIG-Segmentlayout-Extraktion (Issue #52, ADR-001).

Vier Sorten von Tests:

* Fixwert-Tests gegen die ECHTE MIG. Die Werte stammen aus der empirischen
  Strukturanalyse (docs/befund_mig_segmentlayout.md) und sind damit ein
  belastbarer Regressionsanker -- kein Test prueft eine Annahme gegen sich selbst.
* Ein Konsistenztest gegen Prompt 1 (Issue #46): dasselbe RFF-Segment muss ueber
  beide Extraktoren dieselben 91 Pruefidentifikatoren liefern. Widersprechen sich
  die Module, faellt der Test.
* Tests der Architekturentscheidungen aus ADR-001 -- insbesondere, dass die
  Standard-/BDEW-Rohwerte verlustfrei ankommen und `pflicht` nur eine
  abgeleitete Groesse ist.
* Einheitentests des Zustandsautomaten mit synthetischen Zeilen. Sie laufen ohne
  PDF und decken Faelle ab, die im echten Dokument (noch) nicht vorkommen.

Die PDF-abhaengigen Tests ueberspringen sich selbst, wenn die Datei nicht
vorliegt; sie ist aus Groessengruenden nicht im Repository.
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
from app.regulatory_extraction_mig import extract_pi_entries
from app.regulatory_extraction_mig_layout import (
    LayoutField,
    collect_segment_layout,
    detail_header_index,
    extract_segment_layout,
    import_mig_segment_layout,
    is_furniture,
    pflicht_aus_status,
    section_title,
)

_BACKEND = Path(__file__).resolve().parents[1]
_PDF = Path(os.getenv(
    "ATLAS_MIG_GAS_G11_PDF",
    _BACKEND / "data" / "regulatory" / "UTILMD_MIG_Gas_G1_1_20251001.pdf",
))

pytestmark = pytest.mark.skipif(
    not _PDF.exists(),
    reason=f"MIG Gas G1.1 nicht vorhanden ({_PDF})",
)

# Dieselbe Datei wie in Prompt 1 (Issue #46) -- der Hash ist dort ebenfalls
# festgeschrieben. Weichen beide Konstanten auseinander, ist ein Dokumentwechsel
# passiert, der nicht stillschweigend durchgehen darf.
_SHA256 = "f5191a473b650dd6e5de2a673f97b6db685f57de8f6b8d2da7d6ccebb2bfe634"

# Harte Vollstaendigkeitsinvarianten, gemessen an UTILMD MIG Gas G1.1.
_EXPECTED_SEGMENTS = 148
_EXPECTED_FIELDS = 755
# Die Detailtabelle kommt in drei Spaltenbreiten vor; die Spaltenrollen sind
# konstant. Bricht diese Verteilung, hat sich das Layout geaendert.
_EXPECTED_HEADER_FORMS = {10: 147, 7: 6, 11: 1}
# Der Regressionsanker aus Prompt 1.
_RFF_PI_NR = "00038"
_EXPECTED_PI_ENTRIES = 91


@pytest.fixture(scope="module")
def extraction():
    """Ein Durchlauf ueber 168 Seiten dauert ~40 s -- den teilen sich die Tests."""
    return extract_segment_layout(str(_PDF))


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


def _import(db, extraction, **kwargs):
    """Import mit dem bereits gelesenen Stand -- spart je Aufruf einen
    kompletten Durchlauf ueber 168 Seiten."""
    kwargs.setdefault("message_version", "D:11A:UN:G1.1")
    return import_mig_segment_layout(
        db, str(_PDF), 1, extraction=extraction, **kwargs
    )


def _segment(extraction, nr):
    found = [s for s in extraction.segments if s.nr == nr]
    assert found, f"Segment Nr {nr} nicht gefunden"
    return found[0]


def _field(segment, bez):
    found = [f for f in segment.fields if f.bez == bez]
    assert found, f"Datenelement {bez} in Segment {segment.nr} nicht gefunden"
    return found[0]


# ---------------------------------------------------------------------------
# Provenance und Vollstaendigkeit
# ---------------------------------------------------------------------------

def test_file_hash_matches_prompt_1():
    """Dieselbe Datei wie bei der PI-Namen-Extraktion (Auftrag §3)."""
    assert compute_file_hash(str(_PDF)) == _SHA256


def test_form_is_recognized(extraction):
    assert extraction.form_recognized
    assert extraction.form_notes == []


def test_all_segments_and_fields_are_read(extraction):
    """Vollstaendigkeit (§15): alle Segmente, keine Relevanzfilterung."""
    assert len(extraction.segments) == _EXPECTED_SEGMENTS
    assert extraction.field_count == _EXPECTED_FIELDS


def test_nothing_is_left_unclassified(extraction):
    """Kein Rest: jede Zeile des Segmentlayouts ist eingeordnet oder gemeldet."""
    assert extraction.unclassified == []
    assert extraction.skipped == []


def test_header_forms_are_stable(extraction):
    assert extraction.header_forms == _EXPECTED_HEADER_FORMS


def test_crosscheck_against_message_structure_passes(extraction):
    """Gegenprobe (ADR-001, Entscheidung 4): beide Tabellen sind deckungsgleich."""
    assert len(extraction.structure) == _EXPECTED_SEGMENTS
    assert extraction.crosscheck_notes == []
    assert extraction.crosscheck_ok


def test_running_number_is_unique_within_the_document(extraction):
    """`Nr` ist der einzige eindeutige Positionsschluessel (ADR-001)."""
    nummern = [s.nr for s in extraction.segments]
    assert len(set(nummern)) == len(nummern) == _EXPECTED_SEGMENTS


def test_segment_code_alone_is_not_an_identity(extraction):
    """Der Befund, auf dem ADR-001 aufbaut -- als Test festgehalten.

    Weder der Segmentcode noch Code + Segmentgruppenpfad identifizieren ein
    Segment: SG4/SG8/SG10 enthaelt 28 CCI-Positionen. Faellt dieser Test, weil
    beides plotzlich eindeutig waere, ist die Grundannahme von ADR-001 hinfaellig
    und muss neu bewertet werden.
    """
    codes = {s.segment_code for s in extraction.segments}
    assert len(codes) < _EXPECTED_SEGMENTS

    cci = [s for s in extraction.segments
           if s.segment_code == "CCI" and s.segmentgruppen_pfad == "SG4/SG8/SG10"]
    assert len(cci) == 28
    assert len({s.nr for s in cci}) == 28


# ---------------------------------------------------------------------------
# Regressionstest gegen Prompt 1 (Auftrag §18)
# ---------------------------------------------------------------------------

def test_pruefidentifikator_segment_matches_prompt_1(extraction):
    """Dasselbe RFF-Segment, zwei Extraktoren, dasselbe Ergebnis.

    Prompt 1 liest den Pruefidentifikator-Block als Spezialfall, dieses Modul
    liest ihn als eine Zelle unter vielen (144 Zeilen, die groesste des
    Dokuments). Beide muessen dieselben 91 Paare liefern -- sonst widersprechen
    sich zwei Teile der Wissensbasis.
    """
    import re

    segment = _segment(extraction, _RFF_PI_NR)
    assert segment.segment_code == "RFF"
    assert segment.segmentgruppen_pfad == "SG4/SG6"
    assert segment.name == "Prüfidentifikator"

    zelle = _field(segment, "1154")
    aus_layout = {}
    letzte = None
    for zeile in zelle.anwendung:
        treffer = re.match(r"^(\d{5})\s+(\S.*)$", zeile)
        if treffer:
            aus_layout[treffer.group(1)] = treffer.group(2)
            letzte = treffer.group(1)
        elif letzte and zeile != "Prüfidentifikator":
            aus_layout[letzte] = f"{aus_layout[letzte]} {zeile}"

    aus_prompt_1 = {e.pi_number: e.process_name for e in extract_pi_entries(str(_PDF)).entries}
    assert len(aus_prompt_1) == _EXPECTED_PI_ENTRIES
    assert aus_layout == aus_prompt_1


# ---------------------------------------------------------------------------
# Weitere echte Segmente (Auftrag §18: mindestens zwei zusaetzliche)
# ---------------------------------------------------------------------------

def test_unh_segment_real_values(extraction):
    segment = _segment(extraction, "00003")
    assert (segment.segment_code, segment.zaehler, segment.ebene) == ("UNH", "0010", 0)
    assert segment.segmentgruppen_pfad == ""
    assert segment.name == "Nachrichten-Kopfsegment"
    assert (segment.status_standard, segment.status_bdew) == ("M", "M")
    assert (segment.max_wdh_standard, segment.max_wdh_bdew) == ("1", "1")

    feld = _field(segment, "0065")
    assert feld.name == "Nachrichtentyp-Kennung"
    assert (feld.status_standard, feld.status_bdew) == ("M", "M")
    assert (feld.format_standard, feld.format_bdew) == ("an..6", "an..6")
    assert feld.anwendung == ["UTILMD Netzanschluss-Stammdaten"]


def test_dtm_segment_real_values(extraction):
    """DTM Nr 00005 -- MaxWdh weicht zwischen Standard und BDEW ab (9 gegen 1)."""
    segment = _segment(extraction, "00005")
    assert (segment.segment_code, segment.zaehler, segment.ebene) == ("DTM", "0030", 1)
    assert segment.name == "Nachrichtendatum"
    assert (segment.max_wdh_standard, segment.max_wdh_bdew) == ("9", "1")
    assert segment.beispiel == ["DTM+137:199904081315?+00:303'"]
    assert segment.bemerkung == [
        "Dieses Segment wird zur Angabe des Dokumentendatums verwendet."
    ]

    feld = _field(segment, "2379")
    assert (feld.status_standard, feld.status_bdew) == ("C", "R")
    assert (feld.format_standard, feld.format_bdew) == ("an..3", "an..3")


def test_nad_segment_multiline_cells(extraction):
    """NAD Nr 00008 -- Name und Anwendung brechen unabhaengig voneinander um."""
    segment = _segment(extraction, "00008")
    assert segment.segmentgruppen_pfad == "SG2"
    assert segment.segmentgruppe == "SG2"

    # Anwendung ueber zwei Zeilen umbrochen.
    feld = _field(segment, "3035")
    assert feld.anwendung == [
        "MS Dokumenten-/Nachrichtenaussteller bzw. -", "absender",
    ]
    # Name ueber zwei Zeilen umbrochen.
    feld = _field(segment, "3055")
    assert feld.name == "Verantwortliche Stelle für die Codepflege, Code"
    assert feld.name_lines == 2


# ---------------------------------------------------------------------------
# Frage B: Standard- und BDEW-Status verlustfrei (ADR-001, Entscheidung 2)
# ---------------------------------------------------------------------------

def test_standard_and_bdew_status_are_both_preserved(extraction):
    """Das dokumentierte M/N-Beispiel: Standard fordert, BDEW verbietet.

    STS Nr 00027 DE4405 ist der Fall, an dem sich die Architekturentscheidung
    entscheidet. Wuerde nur EIN Statuswert gespeichert, ginge genau hier die
    jeweils andere regulatorische Aussage verloren.
    """
    feld = _field(_segment(extraction, "00027"), "4405")
    assert feld.name == "Status, Code"
    assert feld.status_standard == "M"      # EDIFACT: Muss
    assert feld.status_bdew == "N"          # BDEW: nicht benutzt
    assert feld.format_standard == "an..3"
    assert feld.format_bdew == ""           # BDEW gibt kein Format vor
    assert feld.anwendung == ["Nicht benutzt"]

    # Die Ableitung auf `pflicht` ist verlustbehaftet -- genau deshalb ist sie
    # nicht die Wahrheit.
    assert pflicht_aus_status("N") is False
    assert pflicht_aus_status("D") is False
    assert pflicht_aus_status("M") is True
    assert pflicht_aus_status("R") is True


def test_all_status_values_stay_within_the_documented_legend(extraction):
    """Vollstaendige Enumeration, gegen die Legende des Dokuments gehalten."""
    standard, bdew = set(), set()
    for segment in extraction.segments:
        for feld in segment.fields:
            standard.add(feld.status_standard)
            bdew.add(feld.status_bdew)
    assert standard == {"M", "C"}
    assert bdew == {"M", "R", "D", "N"}     # O ist in G1.1 nicht belegt


def test_format_is_kept_verbatim(extraction):
    """"n5" (genau 5) und "an..70" (bis zu 70) bleiben unterscheidbar.

    Eine Zerlegung in datentyp + laenge wuerde genau diese Unterscheidung
    einebnen -- deshalb speichert ADR-001 den Rohwert.
    """
    feld = _field(_segment(extraction, _RFF_PI_NR), "1154")
    assert feld.format_standard == "an..70"
    assert feld.format_bdew == "n5"


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def test_import_writes_one_generic_definition(db):
    """Einziger Importtest OHNE vorgelesenen Stand.

    Die uebrigen Importtests reichen den Modul-Fixture-Durchlauf herein, um
    nicht je 40 s erneut zu parsen. Dieser eine geht bewusst den vollen
    Produktionsweg -- sonst waere genau der ungetestet.
    """
    report = import_mig_segment_layout(
        db, str(_PDF), 1, message_version="D:11A:UN:G1.1", sparte="gas"
    )
    assert report.errors == []
    assert report.segments_written == _EXPECTED_SEGMENTS
    assert report.fields_written == _EXPECTED_FIELDS

    definitions = db.query(models.MessageDefinition).all()
    assert len(definitions) == 1
    definition = definitions[0]
    assert definition.pi_nummer is None
    assert definition.pi_id is None
    assert definition.grammatik_quelle == "MIG"
    assert definition.nachrichtentyp == "UTILMD"
    assert definition.sparte == "gas"
    assert definition.quelle_hash == _SHA256
    assert definition.quelle_dokument == _PDF.name


def test_import_preserves_position_and_path(db, extraction):
    _import(db, extraction)
    segment = (
        db.query(models.MessageSegment)
        .filter(models.MessageSegment.mig_nr == _RFF_PI_NR)
        .one()
    )
    assert segment.segment_code == "RFF"
    assert segment.mig_zaehler == "0360"
    assert segment.segmentgruppen_pfad == "SG4/SG6"
    assert segment.segmentgruppe == "SG6"        # innerste Gruppe, bestehendes Feld
    assert segment.ebene == 2
    assert segment.status_standard_raw == "M"
    assert segment.status_bdew_raw == "M"
    assert segment.quelle_seite == 51


def test_import_keeps_raw_values_on_fields(db, extraction):
    _import(db, extraction)
    segment = (
        db.query(models.MessageSegment)
        .filter(models.MessageSegment.mig_nr == "00027")
        .one()
    )
    feld = [f for f in segment.fields if f.position == "4405"][0]
    assert feld.status_standard_raw == "M"
    assert feld.status_bdew_raw == "N"
    assert feld.format_standard_raw == "an..3"
    assert feld.format_bdew_raw is None          # leere Zelle -> NULL, nicht ""
    assert feld.pflicht is False
    # Nicht befuellt, weil eine Ableitung Interpretation waere (ADR-001).
    assert feld.datentyp is None and feld.laenge is None
    assert feld.codelist_id is None


def test_import_records_remark_and_example(db, extraction):
    _import(db, extraction)
    segmente = db.query(models.MessageSegment).all()
    assert sum(1 for s in segmente if s.anwendungshinweis) == 131
    assert sum(1 for s in segmente if s.beispiel_edifact) == _EXPECTED_SEGMENTS

    dtm = [s for s in segmente if s.mig_nr == "00005"][0]
    assert dtm.beispiel_edifact == "DTM+137:199904081315?+00:303'"


def test_import_links_codelists_when_present(db, extraction):
    """Aufloesbare Referenz wird verknuepft, unaufloesbare bleibt erhalten."""
    db.add(models.CodeList(
        regulatory_version_id=1, name="G_0002_Antwort auf Änderungsmeldung",
    ))
    db.commit()

    report = _import(db, extraction)
    verweise = db.query(models.MessageFieldCodeList).all()
    assert len(verweise) >= 50

    aufgeloest = [v for v in verweise if v.referenz_id == "G_0002"]
    assert aufgeloest and all(v.codelist_id is not None for v in aufgeloest)
    assert report.codelist_links_resolved == len(aufgeloest)

    # Nicht importierte Codeliste: Referenz bleibt als Rohwert erhalten.
    offen = [v for v in verweise if v.referenz_id == "G_0018"]
    assert offen and offen[0].codelist_id is None
    assert offen[0].referenz_raw.startswith("G_0018 Codeliste")


def test_import_is_idempotent(db, extraction):
    """Zweiter Lauf ersetzt, ergaenzt nicht (Auftrag §19)."""
    first = _import(db, extraction)
    counts_first = (
        db.query(models.MessageDefinition).count(),
        db.query(models.MessageSegment).count(),
        db.query(models.MessageField).count(),
        db.query(models.MessageFieldCodeList).count(),
    )

    second = _import(db, extraction)
    counts_second = (
        db.query(models.MessageDefinition).count(),
        db.query(models.MessageSegment).count(),
        db.query(models.MessageField).count(),
        db.query(models.MessageFieldCodeList).count(),
    )

    assert counts_first == counts_second
    assert second.removed_previous == 1
    assert first.segments_written == second.segments_written
    assert second.errors == []


def test_import_leaves_ahb_rows_untouched(db, extraction):
    """PI-spezifische Zeilen sind von der generischen Sicht unterscheidbar."""
    ahb = models.MessageDefinition(
        regulatory_version_id=1, nachrichtentyp="UTILMD", sparte="gas",
        version="D:11A:UN:G1.1", pi_nummer="44001", quelle_kapitel="5.1",
        quelle_hash="ein-anderer-hash",
    )
    db.add(ahb)
    db.commit()
    ahb_id = ahb.id

    _import(db, extraction)
    _import(db, extraction)

    unveraendert = db.get(models.MessageDefinition, ahb_id)
    assert unveraendert is not None
    assert unveraendert.pi_nummer == "44001"
    assert unveraendert.grammatik_quelle is None
    assert db.query(models.MessageDefinition).filter(
        models.MessageDefinition.pi_nummer.isnot(None)
    ).count() == 1


# ---------------------------------------------------------------------------
# Einheitentests ohne PDF
# ---------------------------------------------------------------------------

@pytest.mark.skipif(False, reason="laeuft auch ohne PDF")
def test_detail_header_index_requires_two_status_and_format_columns():
    zehn = ["Bez", "Name", "", "", "St", "Format", "St", "Format", "Anwendung / Bemerkung", ""]
    assert detail_header_index(zehn) == {
        "bez": 0, "name": 1, "status_standard": 4, "format_standard": 5,
        "status_bdew": 6, "format_bdew": 7, "anwendung": 8,
    }
    sieben = ["Bez", "Name", "St", "Format", "St", "Format", "Anwendung / Bemerkung"]
    assert detail_header_index(sieben)["status_bdew"] == 4

    # Nur EINE Statusspalte -> nicht die erwartete Tabelle, kein Raten.
    assert detail_header_index(
        ["Bez", "Name", "St", "Format", "Anwendung / Bemerkung"]
    ) is None
    assert detail_header_index(["Bez", "Name", "St", "Format"]) is None


def test_section_title_and_furniture():
    assert section_title(["Segmentlayout"]) == "Segmentlayout"
    assert section_title(["Änderungshistorie"]) == "Änderungshistorie"
    assert section_title(["Bez", "Name"]) == ""
    assert is_furniture(["Version: G1.1 01.10.2025", "Seite: 51 / 168"])
    assert is_furniture(["Bez = Objekt-Bezeichner St = Status"])
    assert not is_furniture(["1154", "Referenz, Identifikation"])


def _rows(*rows):
    """Synthetische Tabellenzeilen als (Seite, Tabellenindex, Zeile)."""
    return iter((1, 0, row) for row in rows)


_HEAD = ["Zähler Nr Bez St MaxWdh St MaxWdh Ebene Name", "", "", "", "", "", ""]
_DETAIL = ["Bez", "Name", "St", "Format", "St", "Format", "Anwendung / Bemerkung"]


def test_state_machine_reads_a_minimal_segment():
    result = collect_segment_layout(_rows(
        ["Segmentlayout", "", "", "", "", "", ""],
        _HEAD,
        ["0100", "SG2", "C 99 R 1 1", "", "", "", "MP-ID Absender"],
        ["0110 00008", "NAD", "M 1 M 1 1", "", "", "", "MP-ID Absender"],
        _DETAIL,
        ["3035", "Beteiligter, Qualifier", "M", "an..3", "M", "an..3", "MS Absender"],
        ["", "", "", "", "", "", "zweite Zeile"],
        ["Bemerkung:", "", "", "", "", "", ""],
        ["Ein Hinweis.", "", "", "", "", "", ""],
        ["Beispiel:", "", "", "", "", "", ""],
        ["NAD+MS+9800123000007::332'", "", "", "", "", "", ""],
    ))
    assert result.form_recognized
    assert len(result.segments) == 1
    segment = result.segments[0]
    assert (segment.nr, segment.segment_code, segment.ebene) == ("00008", "NAD", 1)
    assert segment.segmentgruppen_pfad == "SG2"
    assert (segment.status_standard, segment.max_wdh_standard) == ("M", "1")
    assert (segment.status_bdew, segment.max_wdh_bdew) == ("M", "1")
    # Die umschliessende Segmentgruppe wird eigenstaendig gelesen.
    assert [(g.bez, g.status_bdew, g.max_wdh_standard) for g in segment.groups] == [
        ("SG2", "R", "99")
    ]
    assert segment.bemerkung == ["Ein Hinweis."]
    assert segment.beispiel == ["NAD+MS+9800123000007::332'"]
    assert segment.fields[0].anwendung == ["MS Absender", "zweite Zeile"]
    assert result.unclassified == []


def test_state_machine_stops_at_the_next_section():
    """Die Aenderungshistorie darf nicht im letzten Beispielblock landen."""
    result = collect_segment_layout(_rows(
        ["Segmentlayout", "", "", "", "", "", ""],
        _HEAD,
        ["0110 00008", "NAD", "M 1 M 1 1", "", "", "", "MP-ID Absender"],
        _DETAIL,
        ["3035", "Beteiligter, Qualifier", "M", "an..3", "M", "an..3", "MS Absender"],
        ["Beispiel:", "", "", "", "", "", ""],
        ["NAD+MS+123'", "", "", "", "", "", ""],
        ["Änderungshistorie", "", "", "", "", "", ""],
        ["26043 SG4 IMD++Z36 nicht vorhanden vorhanden", "", "", "", "", "", ""],
    ))
    assert result.segments[0].beispiel == ["NAD+MS+123'"]


def test_unknown_status_value_is_skipped_not_guessed():
    """Auftrag §14: nicht raten, sondern ausweisen."""
    result = collect_segment_layout(_rows(
        ["Segmentlayout", "", "", "", "", "", ""],
        _HEAD,
        ["0110 00008", "NAD", "M 1 M 1 1", "", "", "", "MP-ID Absender"],
        _DETAIL,
        ["3035", "Beteiligter, Qualifier", "M", "an..3", "Z", "an..3", "MS Absender"],
        ["3039", "Beteiligter, Identifikation", "M", "an..35", "M", "an..35", "MP-ID"],
    ))
    assert [f.bez for f in result.segments[0].fields] == ["3039"]
    assert len(result.skipped) == 1
    assert "unbekannter BDEW-Status 'Z'" in result.skipped[0].reason


def test_malformed_status_cell_is_skipped():
    result = collect_segment_layout(_rows(
        ["Segmentlayout", "", "", "", "", "", ""],
        _HEAD,
        ["0110 00008", "NAD", "M 1 M", "", "", "", "MP-ID Absender"],
        _DETAIL,
    ))
    assert result.segments == []
    assert not result.form_recognized
    assert len(result.skipped) == 1


def test_codelist_references_are_read_from_the_application_cell():
    feld = LayoutField(bez="1131", anwendung=[
        "GS_001 Codeliste Gas und Strom Nr. GS_001",
        "G_0002 Codeliste Gas Nr. G_0002",
        "Freitext, der keine Referenz ist",
        "G_0002 Codeliste Gas Nr. G_0002",     # Dublette -> nur einmal
    ])
    assert feld.codelist_referenzen == [
        ("GS_001", "GS_001 Codeliste Gas und Strom Nr. GS_001"),
        ("G_0002", "G_0002 Codeliste Gas Nr. G_0002"),
    ]
