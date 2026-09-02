"""Deterministische Extraktionsschicht fuer regulatorische Dokumente (Issue #40).

Eingangsschicht des regulatorischen Gedaechtnisses von Atlas: liest ein
regulatorisches PDF zellbasiert aus und befuellt die Wissensbasis
(MessageDefinition / MessageSegment / MessageField) versioniert und mit
Provenance. Bewusst OHNE LLM -- die Architektur ist

    Dokument -> deterministische Extraktion -> Wissensbasis -> Delta -> KI

Die KI (ai_analysis.py) soll spaeter erklaeren, was eine Aenderung fuer ein EVU
bedeutet; sie darf aber nicht die Quelle dafuer sein, was im Dokument steht.

Leitprinzipien (Auftrag Abschnitt 1 und 13):

* Generisch, nicht anwendungsfallspezifisch. Es steht keine fachliche Annahme
  wie "das ist die Anmeldetabelle" im Parser -- die Spaltenaufteilung wird je
  Seite aus der Kopfzeile des Dokuments abgeleitet.
* Formpruefung vor Extraktion. Was nicht der erwarteten Form entspricht, wird
  nicht geraten, sondern mit Grund und Seite im ImportReport gemeldet.
* Keine Datenverluste. Rohwert, erkannte Referenzen und aufgeloester Wert
  werden nebeneinander gespeichert; unsichere Faelle werden markiert statt
  verworfen.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Sequence

import pdfplumber
from pdfplumber.utils import extract_words
from sqlalchemy.orm import Session

from . import models

# ---------------------------------------------------------------------------
# Konstanten der erwarteten Tabellenform
# ---------------------------------------------------------------------------

# Kopfzeile einer Anwendungsuebersicht: "EDIFACT Struktur | Beschreibung |
# <je PI eine Spalte> | Bedingung". Diese drei Marker definieren die Form, auf
# die sich der Parser stuetzt -- fehlt einer, wird nicht geparst.
_HEADER_LEFT = ("EDIFACT", "Struktur")
_HEADER_CONDITION = "Bedingung"
_HEADER_PI = "Prüfidentifikator"

# Zeilen werden ueber die y-Koordinate geclustert. 3.0 pt ist bewusst grosszuegig:
# im AHB stehen Zeichen derselben Tabellenzeile bis zu ~1.5 pt auseinander (z.B.
# das "∧" in "Muss [28] ∧ [64]" auf einer eigenen Grundlinie). Zu kleine Toleranz
# zerreisst genau solche Zellen.
_ROW_TOLERANCE = 3.0

# Unterspalten innerhalb der "EDIFACT Struktur"-Spalte, gemessen relativ zum
# linken Tabellenrand. Die Werte sind Offsets, keine absoluten x-Werte, damit ein
# anders positionierter Tabellenblock nicht sofort ausfaellt. Jede Zuordnung wird
# zusaetzlich per Regex validiert -- die Geometrie allein entscheidet nichts.
_SUBCOL_SEGMENTGROUP = (0.0, 26.0)     # "SG4"
_SUBCOL_SEGMENT = (26.0, 52.0)         # "DTM"
_SUBCOL_DATAELEMENT = (52.0, 78.0)     # "2005"
_SUBCOL_AHBLINE = (78.0, 110.0)        # "00022"

_RE_SEGMENTGROUP = re.compile(r"^SG\d+$")
_RE_SEGMENT = re.compile(r"^[A-Z]{3}$")
_RE_DATAELEMENT = re.compile(r"^[0-9A-Z]{4}$")
_RE_AHBLINE = re.compile(r"^\d{5}$")
_RE_PI = re.compile(r"^\d{5}$")

# Fussnotenreferenz im Bedingungstext: "[28]", "[1P0..1]", "[UB2]", "[2061]".
_RE_CONDITION_REF = re.compile(r"\[([^\[\]]+)\]")
# Beginn einer Fussnotendefinition in der Bedingungsspalte.
_RE_FOOTNOTE_START = re.compile(r"^\[([^\[\]]+)\]\s*(.*)$")
# Pflichtigkeit auf Segmentebene.
_RE_OBLIGATION = re.compile(r"\b(Muss|Soll|Kann)\b")

# Kapitelueberschrift. Der aus der Vorabanalyse bekannte Regex deckt nur x.y ab;
# hier zusaetzlich einstellige und dreistellige Nummern, weil im AHB Gas 1.1
# sowohl "5 Anwendungsuebersichten GeLi Gas" als auch "5.12.6.1 Anfrage vom LF"
# vorkommen. Die Nummer allein genuegt aber nicht als Erkennungsmerkmal (siehe
# _iter_headings): Tabelleninhalt wie "44020 GeLi Gas / ..." passt sonst ebenfalls.
_RE_HEADING = re.compile(r"^(\d+(?:\.\d+)*)\s+([A-ZÄÖÜ].*)$")
# Mindestzahl an Linien, ab der eine Seite ueberhaupt als Tabelle gilt (siehe
# _page_has_tabular_content).
_MIN_TABLE_EDGES = 20

# Echte Ueberschriften sind im AHB 12 pt gesetzt, Tabelleninhalt 9 pt.
_HEADING_MIN_FONTSIZE = 11.0
# Vorfilter fuer den Ueberschriften-Scan. Bewusst UNTER der Ueberschriftsgroesse:
# das Dokument setzt einzelne Kapitelnummern kleiner als ihren Titel (S.140 hat
# "5.11.4" in 10 pt neben einem 12-pt-Titel). Wer hier bei 11 pt abschneidet,
# verliert die Nummer und damit das ganze Kapitel. 9.5 laesst 9-pt-Tabelleninhalt
# (das Gros des Dokuments) weiterhin draussen -- der Scan bleibt schnell.
_HEADING_SCAN_MIN_FONTSIZE = 9.5
# Fuellpunkte und Seitenverweis am Ende einer Inhaltsverzeichniszeile.
_RE_TOC_TAIL = re.compile(r"\s*\.{2,}\s*\d*\s*$")


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class ChapterRef:
    """Eine im Dokument gefundene Kapitelueberschrift mit ihrem Seitenbereich."""
    number: str
    title: str
    page_from: int
    page_to: int = 0        # wird beim naechsten Kapitel nachgetragen

    @property
    def label(self) -> str:
        return f"{self.number} {self.title}"


@dataclass
class ColumnLayout:
    """Aus der Kopfzeile einer Seite abgeleitete Spaltenaufteilung.

    Wird je Seite neu bestimmt: die Anzahl der PI-Spalten schwankt im selben
    Dokument zwischen 1 und 6, und mit ihr die Breite und Lage aller Spalten.
    """
    left: tuple[float, float]                    # EDIFACT Struktur
    description: tuple[float, float]             # Beschreibung
    pi_columns: list[tuple[str, float, float]]   # (PI-Nummer, x0, x1)
    condition: tuple[float, float]               # Bedingung
    header_bottom: float                         # unterhalb davon beginnt der Tabellenkoerper

    @property
    def pi_numbers(self) -> list[str]:
        return [pi for pi, _, _ in self.pi_columns]


@dataclass
class TableRow:
    """Eine visuelle Textzeile, bereits in Spalten zerlegt."""
    top: float
    page: int
    left: str
    description: str
    pi_cells: dict[str, str]
    condition: str


@dataclass
class Footnote:
    """Eine Fussnotendefinition aus der Bedingungsspalte.

    Fussnoten sind im AHB mehrzeilig gesetzt und laufen ueber Seitengrenzen.
    ``page`` haelt die Seite fest, auf der die Definition beginnt.
    """
    ref: str
    text: str
    page: int
    # Anzahl der Quellzeilen, aus denen die Fussnote zusammengesetzt wurde.
    # Macht die Zusammenfuehrung messbar: "mehrzeilig" ist damit eine gezaehlte
    # Eigenschaft und keine Schaetzung ueber die Textlaenge.
    lines: int = 1

    def append(self, more: str) -> None:
        self.text = f"{self.text} {more}".strip()
        self.lines += 1

    @property
    def is_multiline(self) -> bool:
        return self.lines > 1


@dataclass
class ExtractedField:
    """Ein Datenelement-Zeile ("SG4 DTM 2005 | 92 Datum Vertragsbeginn | X")."""
    segmentgruppe: str
    segment_code: str
    dataelement: str
    code: str
    bezeichnung: str
    pflichtigkeit: str
    bedingung_raw: str
    refs: list[str]
    page: int


@dataclass
class ExtractedSegment:
    """Eine Segmentzeile ("SG4 DTM 00022 | Muss [28] ∧ [64]") samt Feldern."""
    segmentgruppe: str
    segment_code: str
    ahb_zeile: str
    bezeichnung: str
    pflichtigkeit: str
    bedingung_raw: str
    refs: list[str]
    page: int
    fields: list[ExtractedField] = field(default_factory=list)


@dataclass
class SkippedTable:
    """Eine erkannte, aber bewusst nicht importierte Tabelle."""
    chapter: str
    page: int
    designation: str
    reason: str
    status: str = "formprüfung_fehlgeschlagen"


@dataclass
class ChapterResult:
    """Zwischenstand nach einem Kapitel (Auftrag Abschnitt 2)."""
    chapter: ChapterRef
    message_definitions: int = 0
    message_segments: int = 0
    message_fields: int = 0
    skipped_tables: list[SkippedTable] = field(default_factory=list)
    pages: tuple[int, int] = (0, 0)
    warnings: list[str] = field(default_factory=list)

    def format_progress(self) -> str:
        pages = f"S. {self.pages[0]}-{self.pages[1]}" if self.pages[0] else "-"
        lines = [
            f"[Kapitel {self.chapter.number}] {self.chapter.title}",
            f"  Seiten:              {pages}",
            f"  MessageDefinitions:  {self.message_definitions}",
            f"  MessageSegments:     {self.message_segments}",
            f"  MessageFields:       {self.message_fields}",
            f"  Tabellen übersprungen: {len(self.skipped_tables)}",
        ]
        for skipped in self.skipped_tables:
            lines.append(f"    - S.{skipped.page} {skipped.designation}: {skipped.reason} [{skipped.status}]")
        for warning in self.warnings:
            lines.append(f"  ! {warning}")
        return "\n".join(lines)


@dataclass
class ImportReport:
    """Ergebnis eines Importlaufs (Auftrag Abschnitt 10)."""
    document: str
    file_hash: str
    regulatory_version_id: int
    regulatory_version_name: str
    chapters_processed: int = 0
    chapters_imported: int = 0
    chapters_skipped: int = 0
    tables_detected: int = 0
    tables_imported: int = 0
    tables_skipped: int = 0
    message_definitions: int = 0
    message_segments: int = 0
    message_fields: int = 0
    chapter_results: list[ChapterResult] = field(default_factory=list)
    skipped_tables: list[SkippedTable] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    already_imported: bool = False

    def format_report(self) -> str:
        lines = [
            "=" * 72,
            "IMPORTREPORT",
            "=" * 72,
            f"Dokument:             {self.document}",
            f"Hash (SHA-256):       {self.file_hash}",
            f"RegulatoryVersion:    [{self.regulatory_version_id}] {self.regulatory_version_name}",
            f"Kapitel verarbeitet:  {self.chapters_processed}",
            f"Kapitel erfolgreich:  {self.chapters_imported}",
            f"Kapitel übersprungen: {self.chapters_skipped}",
            f"Tabellen erkannt:     {self.tables_detected}",
            f"Tabellen importiert:  {self.tables_imported}",
            f"Tabellen übersprungen:{self.tables_skipped}",
            f"MessageDefinitions:   {self.message_definitions}",
            f"MessageSegments:      {self.message_segments}",
            f"MessageFields:        {self.message_fields}",
            f"Fehler:               {len(self.errors)}",
            f"Warnungen:            {len(self.warnings)}",
        ]
        if self.skipped_tables:
            lines.append("")
            lines.append("Übersprungene Tabellen:")
            lines.append(f"  {'Kapitel':<12} {'Seite':>5}  {'Bezeichnung':<44} Grund / Status")
            for skipped in self.skipped_tables:
                lines.append(
                    f"  {skipped.chapter:<12} {skipped.page:>5}  {skipped.designation[:44]:<44} "
                    f"{skipped.reason} [{skipped.status}]"
                )
        if self.errors:
            lines.append("")
            lines.append("Fehler:")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("")
            lines.append("Warnungen:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Datei-Hash
# ---------------------------------------------------------------------------

def compute_file_hash(path: str) -> str:
    """SHA-256 der Originaldatei -- Provenance und Re-Import-Erkennung.

    Blockweise gelesen, damit auch grosse Dokumentsammlungen (das AHB Gas 1.1
    hat allein ~10 MB) nicht komplett in den Speicher muessen.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Geometrie-Hilfen
# ---------------------------------------------------------------------------

def _cluster(items: Sequence[dict], key: str, tolerance: float) -> list[list[dict]]:
    """Elemente nach einer Koordinate in Zeilen gruppieren."""
    clusters: list[list[dict]] = []
    for item in sorted(items, key=lambda i: (i[key], i["x0"])):
        if clusters and abs(item[key] - clusters[-1][-1][key]) <= tolerance:
            clusters[-1].append(item)
        else:
            clusters.append([item])
    return clusters


def _center(item: dict) -> float:
    return (item["x0"] + item["x1"]) / 2.0


def _text_in_band(chars: Iterable[dict], x0: float, x1: float) -> str:
    """Text zwischen zwei x-Grenzen, zeichenweise zugeordnet.

    Bewusst ueber die Zeichen und nicht ueber ``extract_words()`` der ganzen
    Seite: im AHB stossen Zellen ohne Trennlinie und ohne Leerraum aneinander,
    pdfplumber verschmilzt sie dann zu einem Wort ("[2061]Muss" ueber zwei
    PI-Spalten hinweg). Ueber den Zeichenmittelpunkt zerfaellt das sauber,
    anschliessend baut die pdfplumber-eigene Wortlogik die Woerter je Spalte neu
    auf -- damit bleiben Abstandsregeln und Umlaute unveraendert.
    """
    selected = [c for c in chars if x0 <= _center(c) < x1]
    if not selected:
        return ""
    return " ".join(w["text"] for w in extract_words(selected))


# ---------------------------------------------------------------------------
# Kapitelerkennung
# ---------------------------------------------------------------------------

def _iter_headings(page) -> Iterator[tuple[str, str]]:
    """Kapitelueberschriften einer Seite.

    Die Nummer allein reicht als Merkmal nicht: Tabellenzeilen wie
    "44020 GeLi Gas / Antwort auf ..." erfuellen denselben Regex. Deshalb kommt
    die Schriftgroesse als zweites, unabhaengiges Kriterium dazu -- Ueberschriften
    sind 12 pt gesetzt, Tabelleninhalt 9 pt. Das Inhaltsverzeichnis faellt ueber
    die Fuellpunkte heraus.
    """
    # Zuerst nach Schriftgroesse filtern, dann Woerter bilden: auf einer
    # Tabellenseite sind ueber 2000 Zeichen in 9 pt gesetzt und nur die
    # Ueberschrift in 12 pt. Die Wortbildung nur auf dem Rest laufen zu lassen
    # verkuerzt einen Durchlauf ueber 329 Seiten von Minuten auf Sekunden.
    heading_chars = [
        c for c in page.chars if c.get("size", 0.0) >= _HEADING_SCAN_MIN_FONTSIZE
    ]
    if not heading_chars:
        return

    candidates: list[tuple[str, str]] = []
    toc_markers = 0
    for row in _cluster(extract_words(heading_chars, extra_attrs=["size"]), "top", _ROW_TOLERANCE):
        row = sorted(row, key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in row).strip()
        # Entscheidend ist die GROESSTE Schrift der Zeile: die Kapitelnummer kann
        # kleiner gesetzt sein als ihr Titel (siehe _HEADING_SCAN_MIN_FONTSIZE).
        if max(w.get("size", 0.0) for w in row) < _HEADING_MIN_FONTSIZE:
            continue
        # Merkmale eines Inhaltsverzeichniseintrags: Fuellpunkte oder ein
        # abschliessender Seitenverweis.
        if ".." in text or (len(row) > 1 and row[-1]["text"].isdigit()):
            toc_markers += 1
        match = _RE_HEADING.match(text)
        if match:
            title = _RE_TOC_TAIL.sub("", match.group(2)).strip()
            candidates.append((match.group(1), title))

    # Ein Inhaltsverzeichnis wird als ganze SEITE erkannt und uebersprungen, nicht
    # zeilenweise: umgebrochene Eintraege ("5.8 Anwendungsuebersicht Informations-
    # meldung ueber bestehende Zuordnung,") tragen selbst weder Fuellpunkte noch
    # Seitenverweis und rutschten sonst als echte Ueberschrift durch. Die Schwelle
    # von 3 verhindert, dass eine einzelne auffaellige Zeile eine Inhaltsseite
    # faelschlich ausschliesst.
    if toc_markers >= 3:
        return
    yield from candidates


# Der Kapitelscan liest alle Seiten und ist damit der teuerste Einzelschritt.
# Er haengt nur am Dokumentinhalt, deshalb wird er je Dateihash einmal gemacht --
# mehrere Importlaeufe derselben Datei (Kapitel 5, dann 6, dann 7) scannen sonst
# jedes Mal das komplette Dokument neu.
_CHAPTER_CACHE: dict[str, list[ChapterRef]] = {}


def extract_chapters(pdf, file_hash: str | None = None) -> list[ChapterRef]:
    """Alle Kapitel eines geoeffneten PDF in Dokumentreihenfolge.

    ``page_to`` wird aus dem Beginn des jeweils naechsten Kapitels abgeleitet;
    das letzte Kapitel laeuft bis zur letzten Seite. Doppelt vergebene
    Kapitelnummern werden NICHT zusammengefasst -- das AHB Gas 1.1 vergibt "4.1"
    zweimal, und eine stillschweigende Vereinheitlichung waere bereits eine
    Interpretation des Dokuments.
    """
    if file_hash is not None and file_hash in _CHAPTER_CACHE:
        # Kopien herausgeben, damit ein Aufrufer den Cache nicht veraendern kann.
        return [replace(c) for c in _CHAPTER_CACHE[file_hash]]

    chapters: list[ChapterRef] = []
    for page_number, page in enumerate(pdf.pages, start=1):
        for number, title in _iter_headings(page):
            chapters.append(ChapterRef(number=number, title=title, page_from=page_number))

    for index, chapter in enumerate(chapters):
        if index + 1 < len(chapters):
            following = chapters[index + 1].page_from
            # Die Startseite des Folgekapitels gehoert dem Folgekapitel. Steht die
            # naechste Ueberschrift auf derselben Seite (Kapitel und Unterkapitel
            # zusammen, z.B. "5" und "5.1" auf S.14), bleibt es bei dieser Seite --
            # sonst waere der Bereich leer.
            chapter.page_to = following - 1 if following > chapter.page_from else chapter.page_from
        else:
            chapter.page_to = len(pdf.pages)

    if file_hash is not None:
        _CHAPTER_CACHE[file_hash] = [replace(c) for c in chapters]
    return chapters


# ---------------------------------------------------------------------------
# Formpruefung
# ---------------------------------------------------------------------------

def detect_column_layout(page) -> ColumnLayout | None:
    """Spaltenaufteilung aus der Kopfzeile ableiten -- oder None.

    None bedeutet: die Seite traegt keine Tabelle der erwarteten Form. Der
    Aufrufer darf daraus keine "beste Vermutung" machen (Auftrag Abschnitt 13).
    """
    words = page.extract_words()
    rows = _cluster(words, "top", _ROW_TOLERANCE)

    header_row = None
    for row in rows:
        texts = {w["text"] for w in row}
        if all(marker in texts for marker in _HEADER_LEFT) and "Beschreibung" in texts:
            header_row = sorted(row, key=lambda w: w["x0"])
            break
    if header_row is None:
        return None

    description_x0 = [w for w in header_row if w["text"] == "Beschreibung"][0]["x0"]

    # Die Bedingungsspalte ist OPTIONAL. Anwendungsuebersichten ohne jede
    # Bedingung (z.B. 5.11.2 und 5.12.3) setzen sie gar nicht erst -- die Spalte
    # zur Pflicht zu machen wuerde diese Kapitel vollstaendig verwerfen, obwohl
    # sie die erwartete Form haben. Der Formanker ist laut Auftrag 1.2 die
    # Pruefidentifikator-Zeile, nicht die Bedingungsspalte.
    condition_words = [w for w in header_row if w["text"] == _HEADER_CONDITION]
    right_border = max(
        (e["x0"] for e in page.edges if e["orientation"] == "v"),
        default=float(page.width),
    )
    has_condition = bool(condition_words)
    # Bedingung ist immer die letzte Spalte.
    condition_x0 = condition_words[-1]["x0"] if has_condition else right_border

    # Die PI-Zeile ist der eigentliche Formanker. Sie muss unterhalb der
    # Kopfzeile stehen UND mit ihrem Beschriftungswort in der Beschreibungsspalte
    # beginnen. Ohne diese Lagepruefung wuerden Prosaseiten mitgenommen, auf
    # denen "Pruefidentifikator 44112" im Fliesstext vorkommt (z.B. S.107/187).
    pi_row = None
    header_top = header_row[0]["top"]
    for row in rows:
        row = sorted(row, key=lambda w: w["x0"])
        label = [w for w in row if w["text"].startswith(_HEADER_PI)]
        if not label or row[0]["top"] <= header_top:
            continue
        if not (description_x0 - 4.0 <= label[0]["x0"] < condition_x0):
            continue
        numbers = [w for w in row if _RE_PI.fullmatch(w["text"]) and w["x0"] > label[0]["x1"]]
        if numbers:
            pi_row = (row, numbers)
            break
    if pi_row is None:
        return None

    row, numbers = pi_row
    centers = [_center(w) for w in numbers]
    condition_left = condition_x0 - 3.0

    # Spaltenbreite: bei mehreren PI aus deren Rasterabstand -- das ist das
    # direkteste Mass und gilt unabhaengig davon, ob rechts eine Bedingungsspalte
    # folgt. Nur bei genau einem PI fehlt der Raster; dann bleibt der Abstand bis
    # zur naechsten Spaltengrenze.
    if len(centers) > 1:
        half = (centers[-1] - centers[0]) / (len(centers) - 1) / 2.0
    else:
        half = condition_left - centers[-1]
    if half <= 0:
        return None

    boundaries = [centers[0] - half]
    boundaries += [(centers[i] + centers[i + 1]) / 2.0 for i in range(len(centers) - 1)]
    boundaries.append(min(centers[-1] + half, condition_left) if has_condition else centers[-1] + half)

    pi_columns = [
        (numbers[i]["text"], boundaries[i], boundaries[i + 1])
        for i in range(len(numbers))
    ]
    # Linker Rand der Struktur-Spalte: am Kopfzeilenwort "EDIFACT" ausgerichtet.
    # Die Unterspalten-Offsets (_SUBCOL_*) rechnen relativ zu diesem Anker, damit
    # ein verschobener Tabellenblock sie nicht sofort ins Leere laufen laesst.
    left_x0 = min(w["x0"] for w in header_row if w["text"] in _HEADER_LEFT) - 4.0
    left_x1 = description_x0 - 3.0
    return ColumnLayout(
        left=(left_x0, left_x1),
        description=(left_x1, boundaries[0]),
        pi_columns=pi_columns,
        # Ohne Bedingungsspalte ein leerer Bereich -- so liefert die Zellenlesung
        # konsequent "" statt einer Sonderbehandlung an jeder Aufrufstelle.
        condition=(condition_left, float(page.width)) if has_condition else (right_border, right_border),
        header_bottom=max(w["bottom"] for w in row),
    )


def table_matches_expected_form(table) -> bool:
    """Formpruefung im Sinne von Auftrag Abschnitt 1.2.

    ``table`` ist eine pdfplumber-Seite oder ein bereits ermitteltes
    ColumnLayout. Erwartet wird die Anwendungsuebersichtsform
    "EDIFACT Struktur / Beschreibung / <PI-Spalten> / Bedingung" mit einer
    Pruefidentifikator-Zeile. Alles andere -- etwa die nach Marktrolle
    gegliederte Tabelle in 4.1.4 oder die Aenderungshistorie in Kapitel 8 --
    faellt hier durch und wird nicht geparst.
    """
    if isinstance(table, ColumnLayout):
        return bool(table.pi_columns)
    return detect_column_layout(table) is not None


# ---------------------------------------------------------------------------
# Zeilen- und Fussnotenverarbeitung
# ---------------------------------------------------------------------------

def _page_rows(page, layout: ColumnLayout) -> list[tuple[TableRow, list[dict]]]:
    """Tabellenkoerper einer Seite als spaltenweise zerlegte Textzeilen.

    Gibt zu jeder Zeile die zugehoerigen Zeichen mit zurueck: die Unterspalten
    der EDIFACT-Struktur-Spalte werden spaeter noch einmal geometrisch zerlegt,
    und ein zweiter Clusterlauf ueber gerundete y-Werte waere eine unnoetige
    Fehlerquelle.
    """
    body = [c for c in page.chars if c["top"] > layout.header_bottom]
    rows: list[tuple[TableRow, list[dict]]] = []
    for cluster in _cluster(body, "top", _ROW_TOLERANCE):
        row = TableRow(
            top=min(c["top"] for c in cluster),
            page=page.page_number,
            left=_text_in_band(cluster, *layout.left),
            description=_text_in_band(cluster, *layout.description),
            pi_cells={pi: _text_in_band(cluster, x0, x1) for pi, x0, x1 in layout.pi_columns},
            condition=_text_in_band(cluster, *layout.condition),
        )
        if row.left or row.description or row.condition or any(row.pi_cells.values()):
            rows.append((row, cluster))
    return rows


_RE_PAGE_FOOTER = re.compile(r"Seite\s+\d+\s+von\s+\d+")


def _is_page_footer(row: TableRow) -> bool:
    """Fusszeile "Version: 1.1 01.10.2025 Seite 49 von 329" ausblenden.

    Die Fusszeile liegt geometrisch im Tabellenkoerper und wuerde sonst als
    Datenzeile gelesen. Erkannt wird sie am Seitenzaehler, nicht an der
    Versionsangabe -- der Umbruch verteilt "Version: 1.1" je nach Seite
    unterschiedlich auf die Spalten.
    """
    joined = f"{row.left} {row.description} {row.condition} " + " ".join(row.pi_cells.values())
    return bool(_RE_PAGE_FOOTER.search(joined))


def _parse_left_cell(cell: str, chars: Sequence[dict], layout: ColumnLayout) -> dict[str, str]:
    """Die vier Unterspalten der EDIFACT-Struktur-Spalte auseinandernehmen.

    Geometrie UND Regex muessen zusammenpassen. Reine Geometrie wuerde
    Ueberschriften zerlegen ("Beginn der Nachricht" ragt in die Segmentspalte),
    reiner Regex wuerde die Spaltenzugehoerigkeit verlieren.
    """
    base = layout.left[0]
    parts = {"sg": "", "segment": "", "dataelement": "", "ahbline": ""}
    if not cell:
        return parts

    def band(offsets: tuple[float, float]) -> str:
        return _text_in_band(chars, base + offsets[0], base + offsets[1])

    candidate_sg = band(_SUBCOL_SEGMENTGROUP)
    candidate_segment = band(_SUBCOL_SEGMENT)
    candidate_de = band(_SUBCOL_DATAELEMENT)
    candidate_ahb = band(_SUBCOL_AHBLINE)

    if _RE_SEGMENTGROUP.fullmatch(candidate_sg):
        parts["sg"] = candidate_sg
    if _RE_SEGMENT.fullmatch(candidate_segment):
        parts["segment"] = candidate_segment
    if _RE_DATAELEMENT.fullmatch(candidate_de):
        parts["dataelement"] = candidate_de
    if _RE_AHBLINE.fullmatch(candidate_ahb):
        parts["ahbline"] = candidate_ahb
    return parts


def merge_footnotes(rows: Sequence[TableRow], carry: Footnote | None = None) -> tuple[dict[str, Footnote], list[str]]:
    """Fussnoten der Bedingungsspalte zusammenfuehren (Auftrag Abschnitt 4.4).

    Eine Fussnote beginnt mit "[id]" und laeuft ueber beliebig viele
    Folgezeilen. Eine Folgezeile erkennt man daran, dass sie
      * keine neue "[id]"-Referenz eroeffnet und
      * keine neue echte Datenzeile ist (linke Spalte leer).
    Der zweite Teil ist entscheidend: ohne ihn wuerde Text, der zufaellig neben
    einer neuen Segmentzeile steht, an die vorherige Fussnote angehaengt.

    Beispiel aus AHB Gas 1.1, S. 49:
        [10] Wenn SG4 STS+Z17
        (Transaktionsgrund für
        befristete Anmeldung)
        vorhanden
    ergibt EINE Fussnote [10].

    ``carry`` traegt eine an der Seitengrenze abgeschnittene Fussnote weiter.
    Rueckgabe ist (Fussnoten, Warnungen).
    """
    warnings: list[str] = []
    # Erst ALLE Definitionen in Lesereihenfolge vollstaendig zusammensetzen und
    # danach abgleichen. Wer schon beim Startzeichen vergleicht, meldet einen
    # Konflikt, sobald dieselbe Fussnote ein zweites Mal auftaucht -- verglichen
    # wuerde dann der fertige erste Text gegen die erste ZEILE des zweiten.
    # Das AHB wiederholt Fussnoten regelmaessig neben jeder Zeile, fuer die sie
    # gelten; solche Wiederholungen sind normal und kein Konflikt.
    collected: list[Footnote] = []
    current = carry
    if current is not None:
        collected.append(current)

    for row in rows:
        if _is_page_footer(row):
            continue
        text = row.condition.strip()
        is_data_row = bool(row.left.strip())

        if not text:
            # Eine neue Datenzeile ohne Bedingungstext beendet die laufende
            # Fussnote -- sonst saugt sie spaeteren, unzusammenhaengenden Text auf.
            if is_data_row:
                current = None
            continue

        match = _RE_FOOTNOTE_START.match(text)
        if match:
            current = Footnote(ref=match.group(1), text=match.group(2).strip(), page=row.page)
            collected.append(current)
            continue

        if current is not None and not is_data_row:
            current.append(text)
        elif is_data_row:
            # Bedingungstext auf einer Datenzeile, der nicht mit "[id]" beginnt:
            # unerwartete Form. Nicht raten -- melden und den Rohtext nicht an
            # eine fremde Fussnote haengen.
            warnings.append(
                f"Bedingungstext ohne Fußnoten-Referenz auf S.{row.page}: {text[:60]!r}"
            )
            current = None

    footnotes: dict[str, Footnote] = {}
    for footnote in collected:
        existing = footnotes.get(footnote.ref)
        if existing is None:
            footnotes[footnote.ref] = footnote
            continue
        if not footnote.text or existing.text == footnote.text:
            continue
        # Ist eine Fassung Praefix der anderen, wurde eine der beiden vom
        # Seitenumbruch abgeschnitten -- das ist dieselbe Fussnote, kein
        # Widerspruch. Die laengere (vollstaendige) Fassung gewinnt.
        if existing.text.startswith(footnote.text):
            continue
        if footnote.text.startswith(existing.text):
            footnotes[footnote.ref] = footnote
            continue
        # Gleiche ID, wirklich abweichender Text: nicht stillschweigend
        # ueberschreiben, sondern die erste Definition behalten und melden.
        warnings.append(
            f"Fußnote [{footnote.ref}] auf S.{footnote.page} weicht von der Definition "
            f"auf S.{existing.page} ab -- erste Definition beibehalten"
        )
    return footnotes, warnings


def extract_condition_refs(raw: str) -> list[str]:
    """Alle "[...]"-Referenzen eines Zellinhalts in Lesereihenfolge."""
    seen: list[str] = []
    for ref in _RE_CONDITION_REF.findall(raw or ""):
        if ref not in seen:
            seen.append(ref)
    return seen


def resolve_condition(raw: str, footnotes: dict[str, Footnote]) -> str:
    """Rohbedingung in lesbaren Text aufloesen.

    Die Aufloesung ersetzt den Rohwert NICHT, sie tritt daneben
    (Auftrag Abschnitt 8). Nicht auffindbare Referenzen werden als
    "[id] (nicht aufgelöst)" markiert statt weggelassen -- eine fehlende
    Fussnote ist eine Information, kein Grund zum Verschweigen.
    """
    refs = extract_condition_refs(raw)
    if not refs:
        return ""
    parts = []
    for ref in refs:
        footnote = footnotes.get(ref)
        if footnote is not None and footnote.text:
            parts.append(f"[{ref}] {footnote.text}")
        else:
            parts.append(f"[{ref}] (nicht aufgelöst)")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Aufbau der Segment-/Feldstruktur je PI
# ---------------------------------------------------------------------------

def _build_structure(
    rows: Sequence[TableRow],
    layout_by_page: dict[int, ColumnLayout],
    chars_by_row: Sequence[list[dict]],
    pi_numbers: Sequence[str],
) -> dict[str, list[ExtractedSegment]]:
    """Zeilen in Segmente und Felder je Pruefidentifikator ueberfuehren.

    Eine Segmentzeile traegt die AHB-Zeilennummer ("00022") und die
    Pflichtigkeit (Muss/Soll/Kann), eine Feldzeile das Datenelement ("2005") und
    ein "X" je PI, der das Feld nutzt. Zeilen ohne beides sind Ueberschriften
    (die den Segmentnamen liefern) oder Fortsetzungszeilen.

    Je PI entsteht eine eigene Struktur: dieselbe Tabellenzeile hat fuer 44001
    und 44002 unterschiedliche Auspraegungen, und genau diese Unterscheidung
    soll erhalten bleiben.
    """
    result: dict[str, list[ExtractedSegment]] = {pi: [] for pi in pi_numbers}
    heading = ""
    current_segment: dict[str, ExtractedSegment | None] = {pi: None for pi in pi_numbers}
    current_field: dict[str, ExtractedField | None] = {pi: None for pi in pi_numbers}

    for index, row in enumerate(rows):
        if _is_page_footer(row):
            continue
        layout = layout_by_page[row.page]
        parts = _parse_left_cell(row.left, chars_by_row[index], layout)

        is_segment_row = bool(parts["ahbline"])
        is_field_row = bool(parts["dataelement"])

        if is_segment_row:
            heading_text = heading
            for pi in pi_numbers:
                raw = row.pi_cells.get(pi, "").strip()
                current_field[pi] = None
                if not raw:
                    current_segment[pi] = None
                    continue
                obligation = _RE_OBLIGATION.search(raw)
                segment = ExtractedSegment(
                    segmentgruppe=parts["sg"],
                    segment_code=parts["segment"] or parts["sg"] or "?",
                    ahb_zeile=parts["ahbline"],
                    bezeichnung=heading_text,
                    pflichtigkeit=obligation.group(1) if obligation else "",
                    bedingung_raw=raw,
                    refs=extract_condition_refs(raw),
                    page=row.page,
                )
                result[pi].append(segment)
                current_segment[pi] = segment
            heading = ""
            continue

        if is_field_row:
            description = row.description.strip()
            code, _, label = description.partition(" ")
            # Erstes Token ist ein Qualifier, wenn es wie einer aussieht
            # ("92", "E01", "Z36", "303"); sonst gehoert es zur Bezeichnung.
            if not re.fullmatch(r"[0-9A-Z]{1,4}", code):
                code, label = "", description
            for pi in pi_numbers:
                raw = row.pi_cells.get(pi, "").strip()
                if not raw:
                    current_field[pi] = None
                    continue
                segment = current_segment[pi]
                if segment is None:
                    # Feld ohne zugehoerige Segmentzeile fuer diesen PI: kommt vor,
                    # wenn das Segment nur fuer andere PI gilt. Nicht erfinden.
                    current_field[pi] = None
                    continue
                extracted = ExtractedField(
                    segmentgruppe=parts["sg"],
                    segment_code=parts["segment"] or segment.segment_code,
                    dataelement=parts["dataelement"],
                    code=code,
                    bezeichnung=label.strip(),
                    pflichtigkeit="X" if raw.startswith("X") else raw.split(" ")[0],
                    bedingung_raw=raw,
                    refs=extract_condition_refs(raw),
                    page=row.page,
                )
                segment.fields.append(extracted)
                current_field[pi] = extracted
            continue

        # Weder Segment- noch Feldzeile: Segmentgruppe, Ueberschrift oder Fortsetzung.
        left = row.left.strip()
        description = row.description.strip()
        has_pi_content = any(row.pi_cells.get(pi, "").strip() for pi in pi_numbers)

        if _RE_SEGMENTGROUP.fullmatch(left):
            # Segmentgruppenzeile ("SG12 | Soll [165] | Muss"): traegt eine
            # EIGENE Pflichtigkeit fuer die ganze Gruppe. Sie darf weder verworfen
            # noch -- wie zuvor -- an das zuletzt gelesene Feld angehaengt werden;
            # beides waere eine Verfaelschung. Sie wird deshalb als eigenes Segment
            # ohne AHB-Zeilennummer gefuehrt.
            for pi in pi_numbers:
                raw = row.pi_cells.get(pi, "").strip()
                current_field[pi] = None
                if not raw:
                    # Leere Gruppenzelle heisst nicht, dass das folgende Segment
                    # fuer diesen PI entfaellt -- Segmentkontext unangetastet lassen.
                    continue
                obligation = _RE_OBLIGATION.search(raw)
                segment = ExtractedSegment(
                    segmentgruppe=left,
                    segment_code=left,
                    ahb_zeile="",
                    bezeichnung=heading,
                    pflichtigkeit=obligation.group(1) if obligation else "",
                    bedingung_raw=raw,
                    refs=extract_condition_refs(raw),
                    page=row.page,
                )
                result[pi].append(segment)
                current_segment[pi] = segment
            # heading bleibt stehen: sie gehoert zur folgenden Segmentzeile.
            continue

        if left:
            # Ueberschriftszeile -- liefert den Segmentnamen der naechsten
            # Segmentzeile. Mehrzeilige Ueberschriften werden angehaengt.
            heading = f"{heading} {left}".strip() if heading else left
            continue

        if description and not has_pi_content:
            # Fortsetzung einer Feldbezeichnung ("Datum oder Uhrzeit oder" /
            # "Zeitspanne, Wert").
            for pi in pi_numbers:
                extracted = current_field[pi]
                if extracted is not None:
                    extracted.bezeichnung = f"{extracted.bezeichnung} {description}".strip()
            continue

        if has_pi_content:
            # Fortsetzung eines Bedingungsausdrucks in der PI-Spalte, z.B.
            # "Muss [28] ∧" / "[64]" auf zwei Zeilen. Rohwert weiterfuehren.
            for pi in pi_numbers:
                addition = row.pi_cells.get(pi, "").strip()
                if not addition:
                    continue
                target = current_field[pi] or current_segment[pi]
                if target is None:
                    continue
                target.bedingung_raw = f"{target.bedingung_raw} {addition}".strip()
                target.refs = extract_condition_refs(target.bedingung_raw)
                if isinstance(target, ExtractedSegment) and not target.pflichtigkeit:
                    obligation = _RE_OBLIGATION.search(target.bedingung_raw)
                    if obligation:
                        target.pflichtigkeit = obligation.group(1)
            if description:
                for pi in pi_numbers:
                    extracted = current_field[pi]
                    if extracted is not None:
                        extracted.bezeichnung = f"{extracted.bezeichnung} {description}".strip()
    return result


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def resolve_active_regulatory_version(db: Session) -> models.RegulatoryVersion | None:
    """Aktive RegulatoryVersion ueber is_active aufloesen.

    Bewusst NICHT ueber den Namensstring: der Name ist kuratierter Freitext und
    aendert sich, die Aktiv-Markierung ist das fachliche Merkmal
    (Auftrag Abschnitt 3 und Rueckfrage 5).
    """
    return (
        db.query(models.RegulatoryVersion)
        .filter(models.RegulatoryVersion.is_active.is_(True))
        .order_by(models.RegulatoryVersion.id)
        .first()
    )


def _chapters_in_range(
    chapters: Sequence[ChapterRef], chapter_range: tuple[str, str] | None
) -> list[ChapterRef]:
    """Kapitelauswahl ueber Nummernpraefix, z.B. ("5", "7").

    Verglichen wird numerisch je Ebene, damit "5.10" hinter "5.9" einsortiert
    wird -- ein reiner Stringvergleich wuerde hier falsch sortieren.
    """
    if chapter_range is None:
        return list(chapters)

    def key(number: str) -> tuple[int, ...]:
        return tuple(int(part) for part in number.split(".") if part.isdigit())

    low, high = key(chapter_range[0]), key(chapter_range[1])
    selected = []
    for chapter in chapters:
        chapter_key = key(chapter.number)
        if not chapter_key:
            continue
        # Untergrenze auf voller Tiefe, Obergrenze nur auf der Tiefe der
        # Grenzangabe: ("5", "7") meint "Kapitel 5 bis einschliesslich alles
        # unterhalb von 7", nicht "bis zur Ueberschrift 7".
        if chapter_key >= low and chapter_key[: len(high)] <= high:
            selected.append(chapter)
    return selected


def _existing_import(db: Session, regulatory_version_id: int, file_hash: str) -> int:
    return (
        db.query(models.MessageDefinition)
        .filter(
            models.MessageDefinition.regulatory_version_id == regulatory_version_id,
            models.MessageDefinition.quelle_hash == file_hash,
        )
        .count()
    )


def _delete_previous_import(db: Session, regulatory_version_id: int, file_hash: str) -> None:
    """Vorigen Stand derselben Datei entfernen -- kontrollierter Re-Import."""
    definitions = (
        db.query(models.MessageDefinition)
        .filter(
            models.MessageDefinition.regulatory_version_id == regulatory_version_id,
            models.MessageDefinition.quelle_hash == file_hash,
        )
        .all()
    )
    definition_ids = [d.id for d in definitions]
    if not definition_ids:
        return
    segment_ids = [
        s.id
        for s in db.query(models.MessageSegment.id)
        .filter(models.MessageSegment.message_definition_id.in_(definition_ids))
        .all()
    ]
    if segment_ids:
        db.query(models.MessageField).filter(
            models.MessageField.segment_id.in_(segment_ids)
        ).delete(synchronize_session=False)
    db.query(models.MessageSegment).filter(
        models.MessageSegment.message_definition_id.in_(definition_ids)
    ).delete(synchronize_session=False)
    db.query(models.MessageDefinition).filter(
        models.MessageDefinition.id.in_(definition_ids)
    ).delete(synchronize_session=False)
    db.flush()


def import_ahb_document(
    db: Session,
    pdf_path: str,
    regulatory_version_id: int,
    chapter_range: tuple[str, str] | None = None,
    *,
    nachrichtentyp: str = "UTILMD",
    sparte: str = "gas",
    message_version: str | None = None,
    reimport: bool = False,
    progress=None,
) -> ImportReport:
    """Ein AHB kapitelweise in die Wissensbasis importieren.

    ``chapter_range`` waehlt ueber Kapitelnummern-Praefixe aus, z.B. ("5", "7")
    fuer GeLi Gas bis Netzbetreiberwechsel. ``progress`` wird nach jedem Kapitel
    mit dem ChapterResult gerufen -- der Fortschritt soll waehrend des Laufs
    sichtbar sein und nicht erst am Ende (Auftrag Abschnitt 2).

    ``reimport=False`` und ein bereits importierter Hash bedeuten: sauber
    ueberspringen. ``reimport=True`` loescht den vorigen Stand derselben Datei
    und baut ihn neu auf. Beides ist definiert -- ein unkontrolliertes
    Danebenschreiben gibt es nicht (Auftrag Abschnitt 15).
    """
    file_hash = compute_file_hash(pdf_path)
    document_name = pdf_path.rsplit("/", 1)[-1]

    version = db.get(models.RegulatoryVersion, regulatory_version_id)
    report = ImportReport(
        document=document_name,
        file_hash=file_hash,
        regulatory_version_id=regulatory_version_id,
        regulatory_version_name=version.name if version else "(unbekannt)",
    )
    if version is None:
        report.errors.append(f"RegulatoryVersion {regulatory_version_id} existiert nicht")
        return report

    already = _existing_import(db, regulatory_version_id, file_hash)
    if already and not reimport:
        report.already_imported = True
        report.warnings.append(
            f"Dokumentstand bereits importiert ({already} MessageDefinitions, Hash {file_hash[:12]}...) "
            f"-- übersprungen. Für einen kontrollierten Neuaufbau reimport=True setzen."
        )
        return report
    if already and reimport:
        _delete_previous_import(db, regulatory_version_id, file_hash)
        report.warnings.append(
            f"Kontrollierter Re-Import: {already} vorherige MessageDefinitions dieses Hashes entfernt"
        )

    pi_catalog = {
        pi.pi_number: pi.id for pi in db.query(models.ProcessIdentifier).all()
    }

    # Ganzes Dokument oeffnen, keine kuenstliche Seitenbegrenzung.
    with pdfplumber.open(pdf_path) as pdf:
        chapters = extract_chapters(pdf, file_hash=file_hash)
        selected = _chapters_in_range(chapters, chapter_range)
        report.chapters_processed = len(selected)

        for chapter in selected:
            result = _import_chapter(
                db=db,
                pdf=pdf,
                chapter=chapter,
                version=version,
                document_name=document_name,
                file_hash=file_hash,
                nachrichtentyp=nachrichtentyp,
                sparte=sparte,
                message_version=message_version,
                pi_catalog=pi_catalog,
                report=report,
            )
            report.chapter_results.append(result)
            report.message_definitions += result.message_definitions
            report.message_segments += result.message_segments
            report.message_fields += result.message_fields
            report.skipped_tables.extend(result.skipped_tables)
            report.tables_skipped += len(result.skipped_tables)
            report.warnings.extend(result.warnings)
            if result.message_definitions:
                report.chapters_imported += 1
            else:
                report.chapters_skipped += 1
            db.flush()
            if progress is not None:
                progress(result)

    db.commit()
    return report


def _import_chapter(
    *,
    db: Session,
    pdf,
    chapter: ChapterRef,
    version: models.RegulatoryVersion,
    document_name: str,
    file_hash: str,
    nachrichtentyp: str,
    sparte: str,
    message_version: str | None,
    pi_catalog: dict[str, int],
    report: ImportReport,
) -> ChapterResult:
    """Ein einzelnes Kapitel verarbeiten."""
    result = ChapterResult(chapter=chapter, pages=(chapter.page_from, chapter.page_to))

    rows: list[TableRow] = []
    chars_per_row: list[list[dict]] = []
    layout_by_page: dict[int, ColumnLayout] = {}
    pi_numbers: list[str] = []
    footnotes: dict[str, Footnote] = {}
    carry: Footnote | None = None
    failed_pages: list[int] = []

    for page_number in range(chapter.page_from, chapter.page_to + 1):
        page = pdf.pages[page_number - 1]
        layout = detect_column_layout(page)

        if layout is None:
            # Nicht raten. Eine Seite ohne Tabellenlinien ist reine Prosa (z.B.
            # ein Kapiteldeckblatt) und gar keine Tabelle -- die als
            # "uebersprungene Tabelle" zu melden waere genauso irrefuehrend wie
            # eine echte Tabelle zu verschweigen.
            if _page_has_tabular_content(page):
                report.tables_detected += 1
                failed_pages.append(page_number)
            continue

        report.tables_detected += 1
        report.tables_imported += 1
        layout_by_page[page_number] = layout
        for pi in layout.pi_numbers:
            if pi not in pi_numbers:
                pi_numbers.append(pi)

        page_rows = _page_rows(page, layout)
        page_footnotes, warnings = merge_footnotes([r for r, _ in page_rows], carry)
        for ref, footnote in page_footnotes.items():
            footnotes.setdefault(ref, footnote)
        result.warnings.extend(warnings)
        carry = None

        for row, cluster in page_rows:
            rows.append(row)
            chars_per_row.append(cluster)

    if failed_pages:
        # Aufeinanderfolgende Seiten derselben Tabelle zu einem Eintrag
        # zusammenfassen -- eine ueber fuenf Seiten laufende Tabelle ist EIN
        # uebersprungenes Objekt, nicht fuenf.
        for start, end in _page_ranges(failed_pages):
            result.skipped_tables.append(SkippedTable(
                chapter=chapter.number,
                page=start,
                designation=f"{chapter.title[:52]} (S.{start}-{end})" if end > start else chapter.title[:60],
                reason="erwartete Kopfstruktur (Prüfidentifikator-Zeile) nicht gefunden",
            ))

    if not rows or not pi_numbers:
        return result

    structure = _build_structure(
        rows=rows,
        layout_by_page=layout_by_page,
        chars_by_row=chars_per_row,
        pi_numbers=pi_numbers,
    )

    for pi in pi_numbers:
        segments = structure.get(pi) or []
        if not segments:
            continue
        pi_id = pi_catalog.get(pi)
        if pi_id is None:
            result.warnings.append(
                f"PI {pi} (Kapitel {chapter.number}) ist nicht im ProcessIdentifier-Katalog "
                f"-- pi_id bleibt NULL, pi_nummer ist gesetzt"
            )
        definition = models.MessageDefinition(
            regulatory_version_id=version.id,
            nachrichtentyp=nachrichtentyp,
            version=message_version,
            sparte=sparte,
            beschreibung=chapter.title,
            pi_nummer=pi,
            pi_id=pi_id,
            quelle_dokument=document_name,
            quelle_hash=file_hash,
            quelle_kapitel=chapter.number,
            quelle_kapitel_titel=chapter.title,
            quelle_seite_von=chapter.page_from,
            quelle_seite_bis=chapter.page_to,
        )
        db.add(definition)
        db.flush()
        result.message_definitions += 1

        for position, segment in enumerate(segments, start=1):
            db_segment = models.MessageSegment(
                message_definition_id=definition.id,
                segment_code=segment.segment_code,
                position=position,
                bezeichnung=segment.bezeichnung or None,
                pflicht=segment.pflichtigkeit == "Muss",
                pflichtigkeit=segment.pflichtigkeit or None,
                segmentgruppe=segment.segmentgruppe or None,
                ahb_zeile=segment.ahb_zeile,
                bedingung_raw=segment.bedingung_raw or None,
                bedingung=resolve_condition(segment.bedingung_raw, footnotes) or None,
                bedingung_referenzen=",".join(segment.refs) or None,
                quelle_seite=segment.page,
            )
            db.add(db_segment)
            db.flush()
            result.message_segments += 1

            for extracted in segment.fields:
                db.add(models.MessageField(
                    segment_id=db_segment.id,
                    position=extracted.dataelement,
                    bezeichnung=extracted.bezeichnung or None,
                    pflicht=extracted.pflichtigkeit == "X",
                    pflichtigkeit=extracted.pflichtigkeit or None,
                    segmentgruppe=extracted.segmentgruppe or None,
                    code=extracted.code or None,
                    bedingung_raw=extracted.bedingung_raw or None,
                    bedingung=resolve_condition(extracted.bedingung_raw, footnotes) or None,
                    bedingung_referenzen=",".join(extracted.refs) or None,
                    quelle_seite=extracted.page,
                ))
                result.message_fields += 1
    return result


def _page_ranges(pages: Sequence[int]) -> list[tuple[int, int]]:
    """Aufeinanderfolgende Seitenzahlen zu Bereichen zusammenfassen."""
    ranges: list[tuple[int, int]] = []
    for page in sorted(pages):
        if ranges and page == ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], page)
        else:
            ranges.append((page, page))
    return ranges


def _page_has_tabular_content(page) -> bool:
    """Unterscheidet "Seite trug eine Tabelle" von "reine Prosa-/Titelseite".

    Dient nur der Berichterstattung: eine Titelseite als uebersprungene Tabelle
    zu melden waere genauso irrefuehrend wie eine echte Tabelle zu verschweigen.

    Gemessen wird an den Zeilentrennern. Im AHB Gas 1.1 ist der Unterschied
    eindeutig: Prosa- und Titelseiten tragen 23 senkrechte und 4 waagerechte
    Kanten (reine Seitendekoration), echte Tabellenseiten mehrere hundert von
    beiden. Die Schwelle liegt bewusst weit dazwischen.
    """
    horizontal = sum(1 for e in page.edges if e["orientation"] == "h")
    vertical = sum(1 for e in page.edges if e["orientation"] == "v")
    return horizontal >= _MIN_TABLE_EDGES and vertical >= _MIN_TABLE_EDGES
