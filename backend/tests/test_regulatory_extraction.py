"""Tests der Extraktionspipeline (Issue #40, Auftrag Abschnitt 14).

Zwei Sorten von Tests:

* Fixwert-Tests fuer die Fussnotenlogik. Die Werte stammen aus einer Messung
  gegen die echte Datei und sind damit ein belastbarer Regressionsanker.
* Ein SELBST-VERIFIZIERENDER Test fuer die Anmeldung. Er sucht die Zielzeile
  ueber ihren aufgeloesten Bedingungstext statt ueber eine fest angenommene
  Position und gibt die tatsaechlich gefundenen Werte aus -- ein falscher
  Fixwert soll nicht stillschweigend als "bestanden" durchgewunken werden.

Die Tests ueberspringen sich selbst, wenn die PDF-Datei nicht vorliegt; sie ist
aus Groessengruenden nicht im Repository (siehe data/regulatory/README.md).
"""
from __future__ import annotations

import os
from pathlib import Path

import pdfplumber
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.regulatory_extraction import (
    Footnote,
    TableRow,
    compute_file_hash,
    detect_column_layout,
    extract_chapters,
    extract_condition_refs,
    import_ahb_document,
    merge_footnotes,
    resolve_condition,
    table_matches_expected_form,
    _build_structure,
    _page_rows,
)

_BACKEND = Path(__file__).resolve().parents[1]
_PDF = Path(os.getenv(
    "ATLAS_AHB_GAS_11_PDF",
    _BACKEND / "data" / "regulatory" / "UTILMD_AHB_Gas_1_1_20251001.pdf",
))

pytestmark = pytest.mark.skipif(
    not _PDF.exists(),
    reason=f"AHB Gas 1.1 nicht vorhanden ({_PDF}) -- siehe data/regulatory/README.md",
)

# Gemessen gegen UTILMD AHB Gas 1.1 (SHA-256 b8950fb4..., 329 Seiten).
_SHA256 = "b8950fb45134dd0927c95e5b8f5f0bd98ce59bb2fc7911c5105f552d18c96ae0"
_CHAPTER_ANMELDUNG = "5.6"
_ANMELDUNG_PAGES = (47, 71)
_ANMELDUNG_FOOTNOTES = 77
_ANMELDUNG_MULTILINE_FOOTNOTES = 72
# 4.1.4 ist nach Marktrolle gegliedert und entspricht NICHT der Form
# "EDIFACT-Struktur / Beschreibung / PI-Spalten / Bedingung".
_WRONG_FORM_PAGES = (8, 9, 10, 11, 12)


@pytest.fixture(scope="module")
def pdf():
    with pdfplumber.open(_PDF) as handle:
        yield handle


@pytest.fixture(scope="module")
def anmeldung(pdf):
    """Kapitel 5.6 einmal extrahieren -- 25 Seiten, das lohnt sich nicht je Test."""
    rows, chars, layouts, pis = [], [], {}, []
    footnotes: dict[str, Footnote] = {}
    for page_number in range(_ANMELDUNG_PAGES[0], _ANMELDUNG_PAGES[1] + 1):
        page = pdf.pages[page_number - 1]
        layout = detect_column_layout(page)
        if layout is None:
            continue
        layouts[page_number] = layout
        for pi in layout.pi_numbers:
            if pi not in pis:
                pis.append(pi)
        page_rows = _page_rows(page, layout)
        found, _ = merge_footnotes([r for r, _ in page_rows])
        for ref, footnote in found.items():
            footnotes.setdefault(ref, footnote)
        for row, cluster in page_rows:
            rows.append(row)
            chars.append(cluster)
    structure = _build_structure(rows, layouts, chars, pis)
    return {"rows": rows, "pis": pis, "footnotes": footnotes, "structure": structure}


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def test_file_hash_is_stable():
    assert compute_file_hash(str(_PDF)) == _SHA256


# ---------------------------------------------------------------------------
# Kapitelerkennung
# ---------------------------------------------------------------------------

def test_chapters_are_detected_generically(pdf):
    chapters = extract_chapters(pdf)
    numbers = [c.number for c in chapters]

    # Ein- und mehrstufige Nummern werden gleichermassen erkannt.
    assert "5" in numbers and "5.6" in numbers and "5.12.6.1" in numbers
    # Das Inhaltsverzeichnis (S.3/4) darf keine Kapitel liefern.
    assert all(c.page_from > 4 for c in chapters)

    anmeldung = next(c for c in chapters if c.number == _CHAPTER_ANMELDUNG)
    assert anmeldung.title == "Anwendungsübersicht Anmeldung durch den LF"
    assert (anmeldung.page_from, anmeldung.page_to) == _ANMELDUNG_PAGES


def test_duplicate_chapter_numbers_are_preserved(pdf):
    """Das AHB Gas 1.1 vergibt "4.1" zweimal.

    Die Pipeline darf das nicht stillschweigend vereinheitlichen -- das waere
    bereits eine Interpretation des Dokuments.
    """
    chapters = extract_chapters(pdf)
    titles = [c.title for c in chapters if c.number == "4.1"]
    assert len(titles) == 2
    assert "Regeln bei Antwortnachrichten auf An- und Abmeldung" in titles
    assert "Regeln zu Stammdatenänderungen" in titles


# ---------------------------------------------------------------------------
# Formpruefung (Auftrag Abschnitt 1.2 / 13)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("page_number", _WRONG_FORM_PAGES)
def test_form_check_rejects_marktrollen_table(pdf, page_number):
    """4.1.4 "Tabelle der Verantwortlichen" hat eine andere Form -> nicht raten."""
    assert table_matches_expected_form(pdf.pages[page_number - 1]) is False


def test_form_check_rejects_prose_page_mentioning_pruefidentifikator(pdf):
    """S.107 nennt "Prüfidentifikator 44112" im Fliesstext.

    Ohne Lagepruefung wuerde die Seite als Tabelle durchgehen und PI-Spalten
    erfinden, die es nicht gibt.
    """
    assert table_matches_expected_form(pdf.pages[107 - 1]) is False


def test_form_check_rejects_change_history(pdf):
    """Kapitel 8 "Änderungshistorie" ist eine Vorher/Nachher-Tabelle."""
    assert table_matches_expected_form(pdf.pages[327 - 1]) is False


def test_form_check_accepts_anwendungsuebersicht(pdf):
    assert table_matches_expected_form(pdf.pages[48 - 1]) is True


def test_column_layout_adapts_to_pi_count(pdf):
    """Die Spaltenzahl schwankt im selben Dokument -- 3, 1 und 6 PI kommen vor."""
    assert detect_column_layout(pdf.pages[48 - 1]).pi_numbers == ["44001", "44002", "44003"]
    assert detect_column_layout(pdf.pages[240 - 1]).pi_numbers == ["44035"]
    assert detect_column_layout(pdf.pages[229 - 1]).pi_numbers == [
        "44162", "44163", "44164", "44165", "44166", "44167",
    ]


def test_table_without_condition_column_is_accepted(pdf):
    """Zweite Auspraegung derselben Form: Anwendungsuebersicht OHNE Bedingungsspalte.

    5.11.2 und 5.12.3 fuehren keine Bedingungen und setzen die Spalte gar nicht.
    Der Formanker ist die Pruefidentifikator-Zeile (Auftrag 1.2); die
    Bedingungsspalte zur Pflicht zu machen wuerde diese beiden Kapitel
    vollstaendig verwerfen, obwohl sie sauber lesbar sind.
    """
    layout = detect_column_layout(pdf.pages[131 - 1])
    assert layout is not None
    assert layout.pi_numbers == ["44175", "44176"]
    # Leerer Bedingungsbereich -> die Zellenlesung liefert konsequent "".
    assert layout.condition[0] == layout.condition[1]

    rows = [r for r, _ in _page_rows(pdf.pages[131 - 1], layout)]
    assert all(r.condition == "" for r in rows)
    # Und die Nutzdaten stehen trotzdem in den richtigen Spalten.
    unh = next(r for r in rows if r.left == "UNH 0062")
    assert unh.description.startswith("Nachrichten-Referenznummer")
    assert unh.pi_cells == {"44175": "X", "44176": "X"}


def test_chapters_without_condition_column_are_imported(db):
    """Regression: diese beiden Kapitel wurden zwischenzeitlich komplett
    uebersprungen, weil die Formpruefung eine Bedingungsspalte verlangte."""
    version = _seed_version(db)
    report = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("5.11.2", "5.11.2"),
    )
    assert report.skipped_tables == []
    assert report.message_definitions == 2      # 44175, 44176
    assert report.message_segments > 0
    assert report.message_fields > 0
    assert {d.pi_nummer for d in db.query(models.MessageDefinition).all()} == {"44175", "44176"}


# ---------------------------------------------------------------------------
# Mehrzeilige Fussnoten (Auftrag Abschnitt 4.4) -- Fixwert-Tests
# ---------------------------------------------------------------------------

def _row(page: int, left: str = "", condition: str = "") -> TableRow:
    return TableRow(top=0.0, page=page, left=left, description="",
                    pi_cells={"44001": ""}, condition=condition)


def test_merge_footnotes_joins_continuation_lines():
    """Der in Abschnitt 4.4 dokumentierte Fall, als Einheitstest ohne PDF."""
    rows = [
        _row(49, left="SG4 DTM 00017", condition="[10] Wenn SG4 STS+Z17"),
        _row(49, condition="(Transaktionsgrund für"),
        _row(49, condition="befristete Anmeldung)"),
        _row(49, condition="vorhanden"),
    ]
    footnotes, warnings = merge_footnotes(rows)
    assert warnings == []
    assert list(footnotes) == ["10"]
    assert footnotes["10"].text == (
        "Wenn SG4 STS+Z17 (Transaktionsgrund für befristete Anmeldung) vorhanden"
    )
    assert footnotes["10"].lines == 4
    assert footnotes["10"].is_multiline is True


def test_merge_footnotes_starts_new_footnote_on_new_reference():
    rows = [
        _row(49, condition="[28] Wenn SG4 DTM+93"),
        _row(49, condition="(Ende zum) vorhanden"),
        _row(49, condition="[29] Wenn eine"),
        _row(49, condition="Bilanzierung stattfindet"),
    ]
    footnotes, _ = merge_footnotes(rows)
    assert footnotes["28"].text == "Wenn SG4 DTM+93 (Ende zum) vorhanden"
    assert footnotes["29"].text == "Wenn eine Bilanzierung stattfindet"


def test_merge_footnotes_does_not_bridge_a_new_data_row():
    """Eine neue Datenzeile beendet die laufende Fussnote.

    Ohne diese Regel saugt eine Fussnote Text auf, der zu einer ganz anderen
    Tabellenzeile gehoert.
    """
    rows = [
        _row(49, condition="[10] Wenn SG4 STS+Z17"),
        _row(49, condition="vorhanden"),
        _row(49, left="SG4 DTM 2005"),                 # neue Datenzeile, Bedingung leer
        _row(49, condition="freistehender Text"),
    ]
    footnotes, warnings = merge_footnotes(rows)
    assert footnotes["10"].text == "Wenn SG4 STS+Z17 vorhanden"
    assert any("ohne Fußnoten-Referenz" in w for w in warnings) or "10" in footnotes


def test_repeated_footnote_is_not_a_conflict():
    """Das AHB wiederholt dieselbe Fussnote neben jeder Zeile, fuer die sie gilt.

    Verglichen werden muss der FERTIG zusammengesetzte Text -- wer schon die
    erste Zeile der Wiederholung gegen den fertigen ersten Text haelt, meldet
    reihenweise Konflikte, die keine sind.
    """
    rows = [
        _row(18, condition="[336] Wenn in"),
        _row(18, condition="Änderungsmeldung"),
        _row(18, condition="gefüllt"),
        _row(18, left="SG4 DTM 00021"),
        _row(18, condition="[336] Wenn in"),
        _row(18, condition="Änderungsmeldung"),
        _row(18, condition="gefüllt"),
    ]
    footnotes, warnings = merge_footnotes(rows)
    assert warnings == []
    assert footnotes["336"].text == "Wenn in Änderungsmeldung gefüllt"


def test_footnote_truncated_by_page_break_keeps_complete_version():
    """Wird eine Wiederholung vom Seitenumbruch abgeschnitten, ist das kein
    Widerspruch -- die vollstaendige Fassung gewinnt, ohne Warnung."""
    complete = [
        _row(66, condition="[274] Wenn in derselben"),
        _row(66, condition="SG8 SEQ+Z20 vorhanden"),
    ]
    truncated = [_row(66, condition="[274] Wenn in derselben")]

    footnotes, warnings = merge_footnotes(complete + truncated)
    assert warnings == []
    assert footnotes["274"].text == "Wenn in derselben SG8 SEQ+Z20 vorhanden"

    # Auch in umgekehrter Reihenfolge gewinnt die vollstaendige Fassung.
    footnotes, warnings = merge_footnotes(truncated + complete)
    assert warnings == []
    assert footnotes["274"].text == "Wenn in derselben SG8 SEQ+Z20 vorhanden"


def test_merge_footnotes_reports_conflicting_redefinition():
    rows = [
        _row(49, condition="[28] Wenn SG4 DTM+93"),
        _row(50, condition="[28] Etwas ganz anderes"),
    ]
    footnotes, warnings = merge_footnotes(rows)
    assert footnotes["28"].text == "Wenn SG4 DTM+93"   # erste Definition gewinnt
    assert any("weicht von der Definition" in w for w in warnings)


def test_chapter_5_6_import_is_free_of_footnote_warnings(pdf):
    """Ein sauberer Lauf ueber das Referenzkapitel meldet keine Fussnoten-
    Konflikte -- Warnungen sollen etwas bedeuten und nicht Rauschen sein."""
    warnings = []
    for page_number in range(_ANMELDUNG_PAGES[0], _ANMELDUNG_PAGES[1] + 1):
        page = pdf.pages[page_number - 1]
        layout = detect_column_layout(page)
        if layout is None:
            continue
        _, found = merge_footnotes([r for r, _ in _page_rows(page, layout)])
        warnings.extend(found)
    assert warnings == []


def test_chapter_5_6_footnotes_fixed_values(anmeldung):
    """Regressionsanker gegen die echte Datei, Kapitel 5.6 (25 Seiten)."""
    footnotes = anmeldung["footnotes"]
    assert len(footnotes) == _ANMELDUNG_FOOTNOTES
    multiline = [f for f in footnotes.values() if f.is_multiline]
    assert len(multiline) == _ANMELDUNG_MULTILINE_FOOTNOTES

    # Der dokumentierte Beispielfall aus Abschnitt 4.4, aus dem echten PDF.
    assert footnotes["10"].text == (
        "Wenn SG4 STS+Z17 (Transaktionsgrund für befristete Anmeldung) vorhanden"
    )


def test_every_numeric_reference_in_chapter_5_6_resolves(anmeldung):
    """Alle rein numerischen Referenzen des Kapitels sind auch definiert.

    [UB2] und [1P0..1] sind bewusst ausgenommen: das sind Paket- und
    Formatmarker aus den Allgemeinen Festlegungen, keine Kapitelfussnoten. Sie
    werden von resolve_condition als "(nicht aufgelöst)" markiert statt
    stillschweigend weggelassen.
    """
    footnotes = anmeldung["footnotes"]
    referenced = set()
    for row in anmeldung["rows"]:
        for cell in row.pi_cells.values():
            referenced.update(extract_condition_refs(cell))
    numeric = {ref for ref in referenced if ref.isdigit()}
    assert numeric, "keine numerischen Referenzen gefunden -- Extraktion kaputt?"
    assert numeric <= set(footnotes), f"nicht aufgelöst: {sorted(numeric - set(footnotes))}"


def test_unresolved_reference_is_marked_not_dropped():
    resolved = resolve_condition("X [UB2]", {})
    assert resolved == "[UB2] (nicht aufgelöst)"


# ---------------------------------------------------------------------------
# Selbst-verifizierender Regressionstest (Auftrag Abschnitt 14)
# ---------------------------------------------------------------------------

def test_anmeldung_bilanzierung_row_is_self_verifying(anmeldung, capsys):
    """Zielzeile ueber den aufgeloesten Bedingungstext suchen, nicht ueber eine
    angenommene Position.

    Gesucht ist die Zeile der Anwendungsuebersicht Anmeldung, deren aufgeloeste
    Fussnoten sowohl "Ende zum" als auch "Bilanzierungsbeginn" nennen. Die
    tatsaechlich gefundenen Werte werden ausgegeben, damit ein Mensch sie
    einmalig gegen das PDF gegenpruefen kann.
    """
    footnotes = anmeldung["footnotes"]
    hits = []
    for pi, segments in anmeldung["structure"].items():
        for segment in segments:
            candidates = [("MessageSegment", segment.ahb_zeile, segment)]
            candidates += [("MessageField", f.dataelement, f) for f in segment.fields]
            for kind, position, obj in candidates:
                resolved = resolve_condition(obj.bedingung_raw, footnotes)
                if "Ende zum" in resolved and "Bilanzierungsbeginn" in resolved:
                    hits.append((pi, kind, position, obj, resolved))

    assert hits, "keine Zeile mit aufgelöster Bedingung 'Ende zum' + 'Bilanzierungsbeginn' gefunden"

    with capsys.disabled():
        print("\n  --- Gefundene Werte zur manuellen Gegenprüfung (AHB Gas 1.1) ---")
        for pi, kind, position, obj, resolved in hits:
            print(f"    PI:             {pi}")
            print(f"    Objekt:         {kind}")
            print(f"    position:       {position!r}")
            print(f"    bezeichnung:    {getattr(obj, 'bezeichnung', '')!r}")
            print(f"    pflichtigkeit:  {obj.pflichtigkeit!r}")
            print(f"    bedingung_raw:  {obj.bedingung_raw!r}")
            print(f"    referenzen:     {obj.refs}")
            print(f"    bedingung:      {resolved!r}")
            print(f"    Quelle:         S.{obj.page}")

    for _pi, _kind, position, obj, resolved in hits:
        assert obj.pflichtigkeit in ("Muss", "Soll", "Kann", "M", "S", "K", "X")
        assert obj.bedingung_raw.strip(), "bedingung_raw ist leer"
        # Rohbedingung muss eckige Klammern mit Zahlen enthalten.
        assert [r for r in obj.refs if r.isdigit()], f"keine numerische Referenz in {obj.bedingung_raw!r}"
        assert resolved.strip(), "aufgelöste bedingung ist leer"
        assert position, "position ist leer"

    # Die Muss-Auspraegung dieser Zeile ist der eigentliche Regressionsanker.
    assert any(obj.pflichtigkeit == "Muss" for _p, _k, _pos, obj, _r in hits)


# ---------------------------------------------------------------------------
# Struktur je Pruefidentifikator (Auftrag Abschnitt 6.1)
# ---------------------------------------------------------------------------

def test_structure_is_built_per_pi(anmeldung):
    """Dieselbe Tabelle liefert je PI unterschiedliche Auspraegungen."""
    structure = anmeldung["structure"]
    assert anmeldung["pis"] == ["44001", "44002", "44003"]
    counts = {pi: len(segments) for pi, segments in structure.items()}
    assert all(count > 0 for count in counts.values())
    # Die Auspraegungen unterscheiden sich tatsaechlich -- sonst waere eine
    # MessageDefinition je Tabelle ausreichend gewesen.
    assert len(set(counts.values())) > 1


def test_no_duplicate_ahb_line_numbers_per_pi(anmeldung):
    for pi, segments in anmeldung["structure"].items():
        numbered = [s.ahb_zeile for s in segments if s.ahb_zeile]
        assert len(numbered) == len(set(numbered)), f"Duplikate bei PI {pi}"


def test_raw_condition_is_preserved_alongside_resolution(anmeldung):
    """bedingung_raw darf nie durch die Aufloesung ersetzt werden."""
    footnotes = anmeldung["footnotes"]
    checked = 0
    for segments in anmeldung["structure"].values():
        for segment in segments:
            if not segment.refs:
                continue
            resolved = resolve_condition(segment.bedingung_raw, footnotes)
            assert segment.bedingung_raw != resolved
            assert "[" in segment.bedingung_raw
            checked += 1
    assert checked > 0


# ---------------------------------------------------------------------------
# Import und Idempotenz (Auftrag Abschnitt 15)
# ---------------------------------------------------------------------------

def _seed_version(db) -> models.RegulatoryVersion:
    version = models.RegulatoryVersion(
        name="Testfassung", sector="gas", status="verbindlich", is_active=True,
    )
    db.add(version)
    db.add(models.ProcessIdentifier(pi_number="44001", name="Anmeldung"))
    db.commit()
    return version


def test_import_writes_provenance_and_pi_reference(db):
    version = _seed_version(db)
    report = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("5.6", "5.6"), message_version="D:11A:UN:G1.1",
    )
    assert not report.errors
    assert report.message_definitions == 3          # 44001, 44002, 44003
    assert report.message_segments > 0
    assert report.message_fields > 0

    definitions = db.query(models.MessageDefinition).all()
    by_pi = {d.pi_nummer: d for d in definitions}
    assert set(by_pi) == {"44001", "44002", "44003"}

    for definition in definitions:
        assert definition.quelle_hash == _SHA256
        assert definition.quelle_dokument == _PDF.name
        assert definition.quelle_kapitel == _CHAPTER_ANMELDUNG
        assert definition.regulatory_version_id == version.id

    # 44001 steht im Katalog -> FK gesetzt; 44002/44003 nicht -> NULL, aber die
    # Nummer bleibt erhalten (keine erfundenen Katalogeintraege).
    assert by_pi["44001"].pi_id is not None
    assert by_pi["44002"].pi_id is None
    assert by_pi["44002"].pi_nummer == "44002"

    segments = db.query(models.MessageSegment).all()
    assert all(s.quelle_seite for s in segments)
    fields = db.query(models.MessageField).all()
    assert all(f.quelle_seite for f in fields)
    assert any(f.bedingung_raw for f in fields)


def test_reimport_of_same_file_does_not_duplicate(db):
    version = _seed_version(db)
    first = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("5.6", "5.6"),
    )
    counts = (
        db.query(models.MessageDefinition).count(),
        db.query(models.MessageSegment).count(),
        db.query(models.MessageField).count(),
    )

    # Zweiter Lauf ohne reimport: sauber ueberspringen.
    second = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("5.6", "5.6"),
    )
    assert second.already_imported is True
    assert second.message_definitions == 0
    assert any("bereits importiert" in w for w in second.warnings)

    # Dritter Lauf mit reimport: kontrollierter Neuaufbau, gleiche Mengen.
    third = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("5.6", "5.6"), reimport=True,
    )
    assert third.message_definitions == first.message_definitions
    assert (
        db.query(models.MessageDefinition).count(),
        db.query(models.MessageSegment).count(),
        db.query(models.MessageField).count(),
    ) == counts


def test_skipped_tables_are_reported_not_silently_dropped(db):
    """4.1.4 muss im Report auftauchen -- nicht stillschweigend verschwinden."""
    version = _seed_version(db)
    report = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("4.1.4", "4.1.4"),
    )
    assert report.message_definitions == 0
    assert report.skipped_tables, "übersprungene Tabelle wurde nicht gemeldet"
    skipped = report.skipped_tables[0]
    assert skipped.chapter == "4.1.4"
    assert skipped.status == "formprüfung_fehlgeschlagen"
    assert "Prüfidentifikator" in skipped.reason
    assert skipped.page >= 8


def test_prose_pages_are_not_reported_as_skipped_tables(db):
    """Eine Kapitel-Titelseite ist keine Tabelle.

    Sie als "übersprungene Tabelle" zu melden waere genauso irrefuehrend wie
    eine echte Tabelle zu verschweigen -- der Report soll aussagekraeftig
    bleiben.
    """
    version = _seed_version(db)
    report = import_ahb_document(
        db=db, pdf_path=str(_PDF), regulatory_version_id=version.id,
        chapter_range=("5.6", "5.6"),
    )
    # S.47 ist die reine Titelseite von 5.6 und darf nicht auftauchen.
    assert not [s for s in report.skipped_tables if s.page == 47]
    assert report.skipped_tables == []
