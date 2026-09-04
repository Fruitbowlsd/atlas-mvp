"""Deterministische MIG-Extraktion: vollstaendiges Segmentlayout (Issue #52).

Vierter Baustein der Regulatory-Extraktionspipeline neben AHB-Extraktion
(``regulatory_extraction.py``), MIG-PI-Namen (``regulatory_extraction_mig.py``)
und den Codelisten-Modulen. Wie dort: bewusst OHNE LLM, vollstaendig
deterministisch.

Waehrend die AHB beschreibt, welche Felder fuer EINEN Pruefidentifikator
Muss/Soll/Kann sind, beschreibt die MIG die PI-unabhaengige Grundstruktur der
Nachricht. Beide Sichten teilen sich MessageDefinition/MessageSegment/
MessageField; die generische Sicht ist an ``grammatik_quelle = "MIG"`` und
``pi_nummer IS NULL`` erkennbar.

Der Aufbau folgt ADR-001 (``docs/adr_001_mig_nachrichtengrammatik.md``) und der
empirischen Strukturanalyse (``docs/befund_mig_segmentlayout.md``). Die vier
Befunde, die die Form dieses Moduls bestimmen:

* **Zwei Tabellenarten, zwei Lesewege.** Die Nachrichtenstruktur-Uebersicht ist
  fuer pdfplumber keine Tabelle -- ``extract_tables()`` liefert dort die
  komplette Textzeile in einer Zelle. Sie wird per Regex gelesen. Die
  Segmentlayout-Detailtabellen sind echte Tabellen mit Zellstruktur.
* **Die Uebersicht ist redundant.** Der Segmentkopfblock jeder Detailtabelle
  fuehrt die umschliessenden Segmentgruppenzeilen mit. Ueber das ganze Dokument
  gemessen: 0 Abweichungen. Sie wird deshalb als GEGENPROBE gelesen, nicht als
  zweite Datenquelle.
* **Nur ``Nr`` ist eindeutig.** Segmentcode allein trifft 19 von 148, Pfad+Code
  25 von 148 (SG4/SG8/SG10 enthaelt 28 CCI). Zur Tragweite und zur Grenze von
  ``Nr`` siehe ``models.MessageSegment.mig_nr``.
* **Zwei Status-, Format- und MaxWdh-Spalten.** Standard (EDIFACT) und BDEW
  weichen regelmaessig ab -- beim Status in 536 von 755 Datenelementen. Beide
  werden als Rohwert gespeichert.

Keine Logik in diesem Modul haengt an einer Seitenzahl oder an der Segmentanzahl
dieser einen Fassung: gesteuert wird ausschliesslich ueber Zeilenformen. Damit
ist es auf kuenftige MIG-Staende (Gas wie Strom) anwendbar, ohne neu geschrieben
zu werden.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator, Sequence

import pdfplumber
from sqlalchemy.orm import Session

from . import models
from .regulatory_extraction import compute_file_hash, resolve_active_regulatory_version
from .regulatory_extraction_mig import iter_table_rows

# ---------------------------------------------------------------------------
# Konstanten der erwarteten Dokumentform
# ---------------------------------------------------------------------------

# Kopfzeile ueber dem Segmentkopfblock einer Detailtabelle. Unterscheidet sich
# von der Kopfzeile der Uebersicht ("... Sta BDEW Sta BDEW Ebene Inhalt") und ist
# damit das Merkmal, an dem beide Tabellenarten auseinandergehalten werden --
# ohne Seitenzahlen.
_HEAD_SEGMENTLAYOUT = "Zähler Nr Bez St MaxWdh St MaxWdh Ebene Name"
_HEAD_STRUKTUR = "Zähler Nr Bez Sta BDEW Sta BDEW Ebene Inhalt"

# Kopfzellen der Datenelementtabelle. Der Spaltenindex ist NICHT stabil (7, 10
# und 11 Spalten kommen vor), die Spaltenrollen schon -- deshalb wird der Index
# je Tabelle aus der Kopfzeile bestimmt, wie schon in Prompt 1.
_HEADER_BEZ = "Bez"
_HEADER_NAME = "Name"
_HEADER_ANWENDUNG = "Anwendung / Bemerkung"
_HEADER_STATUS = "St"
_HEADER_FORMAT = "Format"

_MARKER_BEMERKUNG = "Bemerkung:"
_MARKER_BEISPIEL = "Beispiel:"

# Abschnittsueberschrift, die auf JEDER Seite des jeweiligen Abschnitts im
# Seitenkopf mitgedruckt wird. Sie ist die Abschnittsgrenze: ohne sie laeuft der
# Zustandsautomat ueber das Ende des Segmentlayouts hinaus weiter und zieht die
# Aenderungshistorie in den Beispielblock des letzten Segments (nachgemessen an
# G1.1: UNT Nr 00150 bekam 23 Fremdzeilen).
_SECTION_SEGMENTLAYOUT = "Segmentlayout"
_SECTION_TITLES = frozenset({
    _SECTION_SEGMENTLAYOUT, "Nachrichtenstruktur", "Diagramm", "Änderungshistorie",
})

# Seitendekoration: Kopf-, Fuss- und Legendenzeilen, die in JEDER Tabelle
# auftauchen und keine Nutzdaten sind.
_FURNITURE_PREFIXES = (
    "Bez = ", "Nr = ", "MaxWdh = ", "Zähler = ", "Version: ", "Seite: ",
    "Standard BDEW", "Status MaxWdh",
)
# Der Seitenkopf wird von pdfplumber am Rand beschnitten ("UTILMD- MIG",
# "TILMD- MIG", "UTILMD-Ga MIG", "as", "Gas"). Ueber eine feste Liste waere das
# nicht zu fassen, deshalb ein Muster auf den stabilen Teil.
_RE_FURNITURE = re.compile(
    r"^(U?TILMD[- ]|Ga?s$|as$|Segmentlayout$|Nachrichtenstruktur$|Diagramm$|Änderungshistorie$)"
)

# "0360 00039" -- Zähler und laufende Segmentnummer in einer Zelle.
_RE_ZAEHLER_NR = re.compile(r"^(\d{4})\s+(\d{5})$")
# "0180" allein -- Zähler einer Segmentgruppenzeile (die traegt keine Nr).
_RE_ZAEHLER = re.compile(r"^(\d{4})$")
_RE_SEGMENTGRUPPE = re.compile(r"^SG\d+$")
# "M 1 M 1 2" = Status(Std) MaxWdh(Std) Status(BDEW) MaxWdh(BDEW) Ebene
_RE_STATUSZELLE = re.compile(r"^([A-Z])\s+(\d+)\s+([A-Z])\s+(\d+)\s+(\d+)$")
# Datenelement- bzw. Kompositkennung: "1154", "C506", "S009".
_RE_DATENELEMENT = re.compile(r"^(?:[A-Z]\d{3}|\d{4})$")
# Zeile der Nachrichtenstruktur-Uebersicht (Segment bzw. Segmentgruppe).
_RE_STRUKTUR_SEGMENT = re.compile(
    r"^(\d{4})\s+(\d{5})\s+([A-Z]{3})\s+([A-Z])\s+([A-Z])\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)$"
)
_RE_STRUKTUR_GRUPPE = re.compile(
    r"^(\d{4})\s+(SG\d+)\s+([A-Z])\s+([A-Z])\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)$"
)
# "G_0002 Codeliste Gas Nr. G_0002" / "GS_001 Codeliste Gas und Strom Nr. GS_001"
_RE_CODELISTE = re.compile(r"^([A-Z]{1,2}_\d{3,4})\s+Codeliste\b")

# Zulaessige Statuswerte laut der Legende, die auf jeder Seite mitgedruckt ist:
#   "EDIFACT: M=Muss/Mandatory, C=Conditional"
#   "Anwendung: R=Erforderlich/Required, O=Optional, D=Abhängig von/Dependent,
#    N=Nicht benutzt/Not used"
# O ist in G1.1 nicht belegt, wird aber akzeptiert -- die Legende fuehrt es, und
# eine kuenftige Fassung darf es verwenden, ohne dass der Parser bricht.
_STATUS_STANDARD = frozenset({"M", "C"})
_STATUS_BDEW = frozenset({"M", "R", "D", "N", "O"})

# Ableitung der Kompatibilitaetsspalte `pflicht` aus dem BDEW-Status.
# ADR-001: eine ATLAS-Konvention, keine Dokumentaussage. D (bedingt erlaubt) und
# N (verboten) fallen hier zusammen, obwohl sie fachlich gegensaetzlich sind --
# genau deshalb ist `pflicht` nicht die regulatorische Wahrheit und ein
# Validator muss `status_bdew_raw` lesen.
_PFLICHT_AUS_BDEW = {"M": True, "R": True, "D": False, "N": False, "O": False}


def pflicht_aus_status(status_bdew: str) -> bool:
    """Kompatibilitaetswert fuer `pflicht`. Siehe `_PFLICHT_AUS_BDEW`."""
    return _PFLICHT_AUS_BDEW.get(status_bdew, False)


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class LayoutField:
    """Ein Datenelement einer Segment-Detailtabelle -- Rohwerte, unverwandelt."""
    bez: str                       # "1154", "C506"
    name: str = ""
    status_standard: str = ""
    format_standard: str = ""
    status_bdew: str = ""
    format_bdew: str = ""
    anwendung: list[str] = field(default_factory=list)
    source_page: int = 0
    source_page_end: int = 0
    name_lines: int = 1

    def __post_init__(self) -> None:
        if not self.source_page_end:
            self.source_page_end = self.source_page

    @property
    def anwendung_text(self) -> str:
        return "\n".join(self.anwendung)

    @property
    def codelist_referenzen(self) -> list[tuple[str, str]]:
        """(Kennung, Rohzeile) je Codelisten-Verweis im Anwendungstext."""
        out: list[tuple[str, str]] = []
        seen: set[str] = set()
        for line in self.anwendung:
            match = _RE_CODELISTE.match(line)
            if match and match.group(1) not in seen:
                seen.add(match.group(1))
                out.append((match.group(1), line))
        return out


@dataclass
class LayoutGroup:
    """Eine Segmentgruppenzeile im Kopfblock ("0180 SG4 C 99999 R 99999 1")."""
    zaehler: str
    bez: str
    status_standard: str = ""
    max_wdh_standard: str = ""
    status_bdew: str = ""
    max_wdh_bdew: str = ""
    ebene: int = 0
    name: str = ""


@dataclass
class LayoutSegment:
    """Ein Segment des Segmentlayouts samt seiner Datenelemente."""
    zaehler: str
    nr: str
    segment_code: str
    status_standard: str = ""
    max_wdh_standard: str = ""
    status_bdew: str = ""
    max_wdh_bdew: str = ""
    ebene: int = 0
    name: str = ""
    groups: list[LayoutGroup] = field(default_factory=list)
    fields: list[LayoutField] = field(default_factory=list)
    bemerkung: list[str] = field(default_factory=list)
    beispiel: list[str] = field(default_factory=list)
    source_page: int = 0
    source_page_end: int = 0

    @property
    def segmentgruppen_pfad(self) -> str:
        return "/".join(g.bez for g in self.groups)

    @property
    def segmentgruppe(self) -> str:
        """Innerste Gruppe -- fuer das bestehende Feld `segmentgruppe`."""
        return self.groups[-1].bez if self.groups else ""


@dataclass
class StructureRow:
    """Eine Segmentzeile der Nachrichtenstruktur-Uebersicht (Gegenprobe)."""
    zaehler: str
    nr: str
    bez: str
    status_standard: str
    status_bdew: str
    max_wdh_standard: str
    max_wdh_bdew: str
    ebene: int
    inhalt: str
    segmentgruppen_pfad: str = ""


@dataclass
class SkippedRow:
    """Eine erkannte, aber bewusst nicht uebernommene Zeile (Auftrag §14)."""
    reason: str
    source_page: int
    raw: str


@dataclass
class LayoutExtraction:
    """Ergebnis des Lesevorgangs, noch ohne Datenbankbezug.

    ``form_recognized = False`` heisst SKIP: dann bleibt ``segments`` leer und
    ``form_notes`` sagt, welches Merkmal gefehlt hat. Es wird nichts geraten.
    """
    form_recognized: bool = False
    segments: list[LayoutSegment] = field(default_factory=list)
    structure: list[StructureRow] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)
    form_notes: list[str] = field(default_factory=list)
    crosscheck_notes: list[str] = field(default_factory=list)
    header_forms: dict[int, int] = field(default_factory=dict)
    unclassified: list[SkippedRow] = field(default_factory=list)

    @property
    def field_count(self) -> int:
        return sum(len(s.fields) for s in self.segments)

    @property
    def pages(self) -> list[int]:
        return sorted({s.source_page for s in self.segments})

    @property
    def crosscheck_ok(self) -> bool:
        return not self.crosscheck_notes


@dataclass
class LayoutImportReport:
    """Ergebnis eines Importlaufs (Auftrag §20)."""
    document: str
    file_hash: str
    regulatory_version_id: int
    regulatory_version_name: str
    nachrichtentyp: str = "UTILMD"
    sparte: str = "gas"
    message_version: str | None = None
    extraction: LayoutExtraction = field(default_factory=LayoutExtraction)
    definition_id: int | None = None
    segments_written: int = 0
    fields_written: int = 0
    codelist_links_resolved: int = 0
    codelist_links_open: list[str] = field(default_factory=list)
    removed_previous: int = 0
    ahb_definitions_untouched: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def format_report(self) -> str:
        ex = self.extraction
        pages = ex.pages
        span = f"{pages[0]}-{pages[-1]}" if pages else "-"
        lines = [
            "=" * 72,
            "IMPORTREPORT MIG -- Segmentlayout (generische Nachrichtengrammatik)",
            "=" * 72,
            f"Dokument:             {self.document}",
            f"Hash (SHA-256):       {self.file_hash}",
            f"RegulatoryVersion:    [{self.regulatory_version_id}] {self.regulatory_version_name}",
            f"Nachrichtentyp:       {self.nachrichtentyp} / {self.sparte} / {self.message_version or '-'}",
            "",
            f"Form erkannt:         {'ja' if ex.form_recognized else 'NEIN -- SKIP'}",
            f"Kopfzeilenformen:     {ex.header_forms or '-'} (Spaltenzahl: Vorkommen)",
            f"Quellseiten:          {span}",
            "",
            f"Segmente erkannt:     {len(ex.segments)}",
            f"Datenelemente:        {ex.field_count}",
            f"Übersichtszeilen:     {len(ex.structure)}",
            f"Gegenprobe:           {'bestanden' if ex.crosscheck_ok else 'ABWEICHUNGEN'}",
            "",
            f"MessageDefinition:    {self.definition_id if self.definition_id else '-'} "
            f"(pi_nummer NULL, grammatik_quelle 'MIG')",
            f"MessageSegments:      {self.segments_written}",
            f"MessageFields:        {self.fields_written}",
            f"Codeliste-Verweise:   {self.codelist_links_resolved} verknüpft, "
            f"{len(self.codelist_links_open)} offen",
            f"Vorheriger Stand:     {self.removed_previous} Zeilen ersetzt (idempotenter Re-Import)",
            f"AHB-Definitionen:     {self.ahb_definitions_untouched} unverändert",
            f"Übersprungen:         {len(ex.skipped)}",
            f"Nicht klassifiziert:  {len(ex.unclassified)}",
        ]
        if ex.form_notes:
            lines += ["", "Formprüfung:"] + [f"  - {n}" for n in ex.form_notes]
        if ex.crosscheck_notes:
            lines += ["", "Gegenprobe gegen die Nachrichtenstruktur-Übersicht:"]
            lines += [f"  - {n}" for n in ex.crosscheck_notes[:20]]
        if self.codelist_links_open:
            lines += ["", "Codeliste-Verweise ohne importierte Codeliste (Referenz erhalten):"]
            lines += [f"  - {c}" for c in self.codelist_links_open]
        if ex.skipped:
            lines += ["", "Übersprungen:"]
            lines += [f"  - S.{s.source_page} {s.raw[:60]!r}: {s.reason}" for s in ex.skipped[:20]]
        if ex.unclassified:
            lines += ["", "Nicht klassifizierte Zeilen:"]
            lines += [f"  - S.{s.source_page} {s.raw[:60]!r}" for s in ex.unclassified[:20]]
        if self.errors:
            lines += ["", "Fehler:"] + [f"  - {e}" for e in self.errors]
        if self.warnings:
            lines += ["", "Warnungen:"] + [f"  - {w}" for w in self.warnings]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Zeilenklassifikation
# ---------------------------------------------------------------------------

def _cells(row: Sequence) -> list[str]:
    return [c.strip().replace("\n", " ") if isinstance(c, str) else "" for c in row]


def _nonempty(values: Sequence[str]) -> list[str]:
    return [v for v in values if v]


def section_title(values: Sequence[str]) -> str:
    """Abschnittsueberschrift dieser Zeile, sonst "".

    Wird vor der Seitendekorations-Pruefung ausgewertet: die Ueberschrift IST
    Seitendekoration, traegt aber die einzige Abschnittsgrenze des Dokuments.
    """
    joined = " ".join(_nonempty(values))
    return joined if joined in _SECTION_TITLES else ""


def is_furniture(values: Sequence[str]) -> bool:
    """Seitenkopf, Fusszeile oder Legende -- keine Nutzdaten."""
    joined = " ".join(_nonempty(values))
    if not joined:
        return False
    if any(joined.startswith(prefix) for prefix in _FURNITURE_PREFIXES):
        return True
    return bool(_RE_FURNITURE.match(joined))


def detail_header_index(values: Sequence[str]) -> dict[str, int] | None:
    """Spaltenindizes der Datenelement-Kopfzeile, oder None.

    Verlangt werden alle Kopfzellen UND genau zwei Status- und zwei
    Formatspalten -- an genau dieser Doppelung haengt die verlustfreie
    Speicherung von Standard und BDEW. Fehlt eine davon, ist die Tabelle nicht
    die erwartete und der Aufrufer setzt SKIP, statt Spalten zu erraten.
    """
    if _HEADER_ANWENDUNG not in values:
        return None
    if _HEADER_BEZ not in values or _HEADER_NAME not in values:
        return None
    status = [i for i, v in enumerate(values) if v == _HEADER_STATUS]
    formats = [i for i, v in enumerate(values) if v == _HEADER_FORMAT]
    if len(status) != 2 or len(formats) != 2:
        return None
    return {
        "bez": values.index(_HEADER_BEZ),
        "name": values.index(_HEADER_NAME),
        "status_standard": status[0],
        "format_standard": formats[0],
        "status_bdew": status[1],
        "format_bdew": formats[1],
        "anwendung": values.index(_HEADER_ANWENDUNG),
    }


def _split_statuszelle(cell: str) -> tuple[str, str, str, str, int] | None:
    """"M 1 M 1 2" -> (Status-Std, MaxWdh-Std, Status-BDEW, MaxWdh-BDEW, Ebene)."""
    match = _RE_STATUSZELLE.match(cell)
    if not match:
        return None
    return (match.group(1), match.group(2), match.group(3), match.group(4), int(match.group(5)))


# ---------------------------------------------------------------------------
# Nachrichtenstruktur-Uebersicht (Gegenprobe)
# ---------------------------------------------------------------------------

def collect_structure(rows: Iterator[tuple[int, int, list]]) -> list[StructureRow]:
    """Die Nachrichtenstruktur-Uebersicht als Liste von Segmentzeilen.

    Fuer pdfplumber ist diese Tabelle keine Tabelle -- die komplette Textzeile
    steht in einer Zelle. Gelesen wird deshalb per Regex.

    Der Segmentgruppenpfad wird ueber einen Stack auf der Spalte `Ebene`
    rekonstruiert: eine Segmentgruppe auf Ebene e umschliesst alles, was danach
    auf Ebene >= e folgt.
    """
    out: list[StructureRow] = []
    stack: list[tuple[int, str]] = []
    active = False
    for _page, _table, row in rows:
        for cell in _cells(row):
            if not cell:
                continue
            if cell == _HEAD_STRUKTUR:
                active = True
                continue
            if not active:
                continue
            match = _RE_STRUKTUR_GRUPPE.match(cell)
            if match:
                ebene = int(match.group(7))
                while stack and stack[-1][0] >= ebene:
                    stack.pop()
                stack.append((ebene, match.group(2)))
                continue
            match = _RE_STRUKTUR_SEGMENT.match(cell)
            if match:
                ebene = int(match.group(8))
                while stack and stack[-1][0] > ebene:
                    stack.pop()
                out.append(StructureRow(
                    zaehler=match.group(1), nr=match.group(2), bez=match.group(3),
                    status_standard=match.group(4), status_bdew=match.group(5),
                    max_wdh_standard=match.group(6), max_wdh_bdew=match.group(7),
                    ebene=ebene, inhalt=match.group(9).strip(),
                    segmentgruppen_pfad="/".join(b for _, b in stack),
                ))
                continue
            # Umbrochene Fortsetzung der Spalte `Inhalt`.
            if out and not is_furniture([cell]) and not cell.startswith(_HEAD_SEGMENTLAYOUT):
                out[-1].inhalt = f"{out[-1].inhalt} {cell}".strip()
    return out


# ---------------------------------------------------------------------------
# Segmentlayout
# ---------------------------------------------------------------------------

def collect_segment_layout(rows: Iterator[tuple[int, int, list]]) -> LayoutExtraction:
    """Zustandsautomat ueber die Tabellenzeilen des Segmentlayouts.

    Ablauf je Segment (empirisch belegt, siehe Modul-Docstring):

        "Zähler Nr Bez St MaxWdh ..."  -> Kopfblock beginnt, Gruppenstack leeren
        "0180" | "SG4" | "C 99999 ..." -> umschliessende Segmentgruppe
        "0360 00039" | "RFF" | "M 1 ..."-> das Segment selbst
        "Bez | Name | St | Format ..." -> Datenelementtabelle beginnt
        "1154" | "Referenz, ..." | ...  -> Datenelement
        Zeile ohne Bez                  -> Fortsetzung des letzten Datenelements
        "Bemerkung:" / "Beispiel:"      -> Freitextbloecke bis zum Blockende

    Der Zustand laeuft ueber Tabellen- und Seitengrenzen hinweg: 9 Seiten der
    G1.1 sind reine Fortsetzungsseiten ohne eigenen Segmentkopf.
    """
    result = LayoutExtraction()
    state = ""            # "" | "head" | "detail"
    mode = ""             # innerhalb "detail": "fields" | "bemerkung" | "beispiel"
    index: dict[str, int] | None = None
    groups: list[LayoutGroup] = []
    segment: LayoutSegment | None = None
    last_head: object | None = None
    section = ""

    for page, _table, raw_row in rows:
        values = _cells(raw_row)
        if not _nonempty(values):
            continue

        title = section_title(values)
        if title:
            section = title
            # Ein erneutes "Segmentlayout" ist der Seitenkopf einer
            # Fortsetzungsseite und darf den laufenden Block NICHT beenden --
            # 9 Seiten der G1.1 tragen kein eigenes Segment.
            if title != _SECTION_SEGMENTLAYOUT:
                state, mode, index, segment, last_head = "", "", None, None, None
                groups = []
            continue
        if section != _SECTION_SEGMENTLAYOUT:
            continue
        if is_furniture(values):
            continue

        first = values[0]
        if first == _HEAD_SEGMENTLAYOUT:
            state, mode, groups, last_head = "head", "", [], None
            continue

        header = detail_header_index(values)
        if header is not None:
            index = header
            result.header_forms[len(values)] = result.header_forms.get(len(values), 0) + 1
            state, mode, last_head = "detail", "fields", None
            continue

        if state == "head":
            _read_head_row(result, page, values, groups, last_head)
            if result.segments and result.segments[-1] is not segment:
                segment = result.segments[-1]
                last_head = segment
            elif groups and (last_head is None or last_head is not groups[-1]):
                last_head = groups[-1]
            continue

        if state == "detail" and segment is not None and index is not None:
            mode = _read_detail_row(result, page, values, index, segment, mode)
            continue

        result.unclassified.append(SkippedRow(
            reason="Zeile ausserhalb eines erkannten Blocks",
            source_page=page, raw=" | ".join(_nonempty(values)),
        ))

    _check_form(result)
    return result


def _read_head_row(
    result: LayoutExtraction,
    page: int,
    values: list[str],
    groups: list[LayoutGroup],
    last_head: object | None,
) -> None:
    """Eine Zeile des Segmentkopfblocks lesen (Segment, Gruppe oder Umbruch)."""
    rest = _nonempty(values[1:])
    first = values[0]

    match = _RE_ZAEHLER_NR.match(first) if first else None
    if match and len(rest) >= 2:
        parsed = _split_statuszelle(rest[1])
        if parsed is None:
            result.skipped.append(SkippedRow(
                reason="Statuszelle des Segments nicht in der Form 'St MaxWdh St MaxWdh Ebene'",
                source_page=page, raw=" | ".join(rest),
            ))
            return
        st_std, mw_std, st_bdew, mw_bdew, ebene = parsed
        segment = LayoutSegment(
            zaehler=match.group(1), nr=match.group(2), segment_code=rest[0],
            status_standard=st_std, max_wdh_standard=mw_std,
            status_bdew=st_bdew, max_wdh_bdew=mw_bdew, ebene=ebene,
            name=rest[2] if len(rest) > 2 else "",
            groups=list(groups), source_page=page, source_page_end=page,
        )
        result.segments.append(segment)
        return

    match = _RE_ZAEHLER.match(first) if first else None
    if match and rest and _RE_SEGMENTGRUPPE.match(rest[0]):
        parsed = _split_statuszelle(rest[1]) if len(rest) > 1 else None
        if parsed is None:
            result.skipped.append(SkippedRow(
                reason="Statuszelle der Segmentgruppe nicht in der erwarteten Form",
                source_page=page, raw=" | ".join(rest),
            ))
            return
        st_std, mw_std, st_bdew, mw_bdew, ebene = parsed
        groups.append(LayoutGroup(
            zaehler=match.group(1), bez=rest[0],
            status_standard=st_std, max_wdh_standard=mw_std,
            status_bdew=st_bdew, max_wdh_bdew=mw_bdew, ebene=ebene,
            name=rest[2] if len(rest) > 2 else "",
        ))
        return

    # Umbrochener Name: erste Zelle leer, Rest ist die Fortsetzung. 6 Segmente
    # der G1.1 sind so umbrochen; ohne Zusammenfuehrung waere ihr Name gekuerzt.
    if not first and rest and last_head is not None:
        last_head.name = f"{last_head.name} {rest[-1]}".strip()  # type: ignore[attr-defined]
        return

    result.unclassified.append(SkippedRow(
        reason="Zeile im Segmentkopfblock nicht klassifizierbar",
        source_page=page, raw=" | ".join(_nonempty(values)),
    ))


def _read_detail_row(
    result: LayoutExtraction,
    page: int,
    values: list[str],
    index: dict[str, int],
    segment: LayoutSegment,
    mode: str,
) -> str:
    """Eine Zeile der Datenelementtabelle lesen. Gibt den neuen Modus zurueck."""
    bez = values[index["bez"]]
    joined = " ".join(_nonempty(values))

    if bez == _MARKER_BEMERKUNG:
        return "bemerkung"
    if bez == _MARKER_BEISPIEL:
        return "beispiel"

    # Zeile mit dem blossen Segmentcode ueber der Datenelementliste.
    if bez == segment.segment_code and not _nonempty(
        [values[index[k]] for k in ("status_standard", "status_bdew", "anwendung")]
    ):
        return mode

    if mode == "bemerkung":
        segment.bemerkung.append(joined)
        segment.source_page_end = page
        return mode
    if mode == "beispiel":
        segment.beispiel.append(joined)
        segment.source_page_end = page
        return mode

    if bez and _RE_DATENELEMENT.match(bez):
        status_standard = values[index["status_standard"]]
        status_bdew = values[index["status_bdew"]]
        # Statuswerte nicht raten: ein unbekannter Wert waere eine
        # Formaenderung, keine Variante (Auftrag §14).
        if status_standard and status_standard not in _STATUS_STANDARD:
            result.skipped.append(SkippedRow(
                reason=f"unbekannter Standard-Status {status_standard!r} "
                       f"(erwartet: {sorted(_STATUS_STANDARD)})",
                source_page=page, raw=joined,
            ))
            return mode
        if status_bdew and status_bdew not in _STATUS_BDEW:
            result.skipped.append(SkippedRow(
                reason=f"unbekannter BDEW-Status {status_bdew!r} "
                       f"(erwartet: {sorted(_STATUS_BDEW)})",
                source_page=page, raw=joined,
            ))
            return mode
        anwendung = values[index["anwendung"]]
        segment.fields.append(LayoutField(
            bez=bez, name=values[index["name"]],
            status_standard=status_standard,
            format_standard=values[index["format_standard"]],
            status_bdew=status_bdew,
            format_bdew=values[index["format_bdew"]],
            anwendung=[anwendung] if anwendung else [],
            source_page=page, source_page_end=page,
        ))
        segment.source_page_end = page
        return mode

    # Fortsetzungszeile: keine Bez-Zelle. Name und Anwendung koennen unabhaengig
    # voneinander umbrechen, deshalb spaltenweise anhaengen -- nicht wie in
    # Prompt 1 nur fuer eine Zielspalte.
    if not bez and segment.fields:
        current = segment.fields[-1]
        if values[index["name"]]:
            current.name = f"{current.name} {values[index['name']]}".strip()
            current.name_lines += 1
        if values[index["anwendung"]]:
            current.anwendung.append(values[index["anwendung"]])
        current.source_page_end = page
        segment.source_page_end = page
        return mode

    result.unclassified.append(SkippedRow(
        reason="Zeile der Datenelementtabelle nicht klassifizierbar",
        source_page=page, raw=joined,
    ))
    return mode


def _check_form(result: LayoutExtraction) -> None:
    """Formpruefung (Auftrag §7): passt das Gelesene zur bestaetigten Struktur?"""
    if not result.segments:
        result.form_notes.append(
            f"Keine Segmentkopfzeile {_HEAD_SEGMENTLAYOUT!r} mit nachfolgender "
            "Datenelementtabelle gefunden -- SKIP"
        )
        return
    if not result.header_forms:
        result.form_notes.append("Keine Datenelement-Kopfzeile gefunden -- SKIP")
        result.segments.clear()
        return

    ohne_felder = [s.nr for s in result.segments if not s.fields]
    if ohne_felder:
        result.form_notes.append(
            f"{len(ohne_felder)} Segment(e) ohne Datenelemente: {ohne_felder[:10]}"
        )
    doppelte = [nr for nr in {s.nr for s in result.segments}
                if sum(1 for s in result.segments if s.nr == nr) > 1]
    if doppelte:
        result.form_notes.append(
            f"Laufende Segmentnummer mehrfach vergeben: {sorted(doppelte)[:10]} -- SKIP"
        )
        result.segments.clear()
        return
    if result.unclassified:
        result.form_notes.append(
            f"{len(result.unclassified)} Zeile(n) nicht klassifizierbar -- "
            "im Report ausgewiesen, nicht importiert"
        )
    result.form_recognized = True


def crosscheck(result: LayoutExtraction) -> None:
    """Segmentlayout gegen die Nachrichtenstruktur-Uebersicht pruefen (ADR-001).

    Die Uebersicht ist keine zweite Datenquelle, sondern eine unabhaengige
    Gegenprobe: sie enthaelt dieselben Angaben ein zweites Mal. Fuer G1.1 sind
    beide deckungsgleich; jede kuenftige Abweichung ist damit ein belastbares
    Signal und keine Rauschmeldung.

    Verglichen wird ueber `Nr` -- `Bez` waere mehrdeutig (19 Segmentcodes fuer
    148 Segmente). Der Name wird bewusst NICHT verglichen: in der Uebersicht ist
    er in 6 Faellen umbruchbedingt gekuerzt, die Detailtabelle ist massgeblich.
    """
    if not result.structure:
        result.crosscheck_notes.append(
            "Nachrichtenstruktur-Übersicht nicht gefunden -- Gegenprobe nicht möglich"
        )
        return
    by_nr = {row.nr: row for row in result.structure}
    if len(by_nr) != len(result.structure):
        result.crosscheck_notes.append(
            "Laufende Segmentnummer in der Übersicht nicht eindeutig"
        )
    for segment in result.segments:
        row = by_nr.get(segment.nr)
        if row is None:
            result.crosscheck_notes.append(
                f"Nr {segment.nr} ({segment.segment_code}) fehlt in der Übersicht"
            )
            continue
        vergleich = [
            ("Zähler", segment.zaehler, row.zaehler),
            ("Segmentcode", segment.segment_code, row.bez),
            ("Status Standard", segment.status_standard, row.status_standard),
            ("Status BDEW", segment.status_bdew, row.status_bdew),
            ("MaxWdh Standard", segment.max_wdh_standard, row.max_wdh_standard),
            ("MaxWdh BDEW", segment.max_wdh_bdew, row.max_wdh_bdew),
            ("Ebene", str(segment.ebene), str(row.ebene)),
            ("Segmentgruppenpfad", segment.segmentgruppen_pfad, row.segmentgruppen_pfad),
        ]
        for label, mine, theirs in vergleich:
            if mine != theirs:
                result.crosscheck_notes.append(
                    f"Nr {segment.nr}: {label} Detailtabelle {mine!r} != Übersicht {theirs!r}"
                )
    fehlend = sorted(set(by_nr) - {s.nr for s in result.segments})
    if fehlend:
        result.crosscheck_notes.append(
            f"{len(fehlend)} Segment(e) der Übersicht ohne Detailtabelle: {fehlend[:10]}"
        )
    reihenfolge_mine = [s.nr for s in result.segments]
    reihenfolge_ov = [r.nr for r in result.structure]
    if reihenfolge_mine != reihenfolge_ov:
        result.crosscheck_notes.append(
            "Reihenfolge von Segmentlayout und Übersicht stimmt nicht überein"
        )


def extract_segment_layout(pdf_path: str) -> LayoutExtraction:
    """Formpruefung, Extraktion und Gegenprobe fuer eine MIG-Datei."""
    with pdfplumber.open(pdf_path) as pdf:
        structure = collect_structure(iter_table_rows(pdf))
        result = collect_segment_layout(iter_table_rows(pdf))
    result.structure = structure
    if result.form_recognized:
        crosscheck(result)
    return result


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def _resolve_codelist(
    db: Session, regulatory_version_id: int, referenz_id: str
) -> tuple[int | None, str]:
    """Codeliste zu einer Referenzkennung suchen (ADR-001, Entscheidung 5).

    Die EBD-Codelisten heissen "G_0002_Antwort auf ...", die MIG referenziert
    "G_0002". Verglichen wird deshalb ueber das Praefix. Treffen mehrere
    Codelisten zu, wird NICHT geraten -- die Referenz bleibt offen.
    """
    matches = (
        db.query(models.CodeList)
        .filter(
            models.CodeList.regulatory_version_id == regulatory_version_id,
            models.CodeList.name.like(f"{referenz_id}\\_%", escape="\\"),
        )
        .all()
    )
    if len(matches) == 1:
        return matches[0].id, ""
    if not matches:
        return None, "keine importierte Codeliste mit dieser Kennung"
    return None, f"mehrdeutig -- {len(matches)} Codelisten mit dieser Kennung, nicht geraten"


def _delete_previous_generic_import(
    db: Session, regulatory_version_id: int, file_hash: str
) -> int:
    """Vorigen generischen Stand derselben Datei entfernen.

    Streng auf ``grammatik_quelle = "MIG"`` UND ``pi_nummer IS NULL``
    eingeschraenkt: PI-spezifische Zeilen der AHB-Extraktion koennen dadurch
    auch dann nicht getroffen werden, wenn sie zufaellig denselben Hash traegen.
    """
    definitions = (
        db.query(models.MessageDefinition)
        .filter(
            models.MessageDefinition.regulatory_version_id == regulatory_version_id,
            models.MessageDefinition.quelle_hash == file_hash,
            models.MessageDefinition.grammatik_quelle == "MIG",
            models.MessageDefinition.pi_nummer.is_(None),
        )
        .all()
    )
    definition_ids = [d.id for d in definitions]
    if not definition_ids:
        return 0
    segment_ids = [
        s.id for s in db.query(models.MessageSegment.id).filter(
            models.MessageSegment.message_definition_id.in_(definition_ids)
        ).all()
    ]
    if segment_ids:
        field_ids = [
            f.id for f in db.query(models.MessageField.id).filter(
                models.MessageField.segment_id.in_(segment_ids)
            ).all()
        ]
        if field_ids:
            db.query(models.MessageFieldCodeList).filter(
                models.MessageFieldCodeList.message_field_id.in_(field_ids)
            ).delete(synchronize_session=False)
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
    return len(definition_ids)


def import_mig_segment_layout(
    db: Session,
    pdf_path: str,
    regulatory_version_id: int,
    *,
    nachrichtentyp: str = "UTILMD",
    sparte: str = "gas",
    message_version: str | None = None,
    beschreibung: str | None = None,
    extraction: LayoutExtraction | None = None,
) -> LayoutImportReport:
    """Das Segmentlayout einer MIG als generische Nachrichtengrammatik uebernehmen.

    Legt GENAU EINE ``MessageDefinition`` an -- die generische Struktur der
    Nachricht, nicht an einen Pruefidentifikator gebunden:

        pi_nummer = NULL, pi_id = NULL, grammatik_quelle = "MIG"

    Der Lauf ist von sich aus idempotent: ein voriger generischer Stand
    derselben Datei wird ersetzt, nicht ergaenzt. Bestehende PI-spezifische
    Zeilen der AHB-Extraktion bleiben unberuehrt -- sie sind ueber
    ``pi_nummer IS NOT NULL`` von der Loeschung ausgeschlossen und werden zur
    Kontrolle vor und nach dem Schreiben gezaehlt.

    ``extraction`` erlaubt es, einen bereits gelesenen Stand wiederzuverwenden,
    statt die Datei erneut zu oeffnen. Ein Durchlauf ueber 168 Seiten dauert
    rund 40 Sekunden; wer erst pruefen und dann importieren will -- oder wie die
    Testsuite mehrfach importiert -- soll dafuer nicht mehrfach zahlen. Der
    Hash wird trotzdem immer frisch aus der Datei berechnet, damit die
    Provenienz nicht aus einem mitgereichten Objekt stammt.
    """
    file_hash = compute_file_hash(pdf_path)
    document_name = pdf_path.rsplit("/", 1)[-1]
    version = db.get(models.RegulatoryVersion, regulatory_version_id)

    report = LayoutImportReport(
        document=document_name,
        file_hash=file_hash,
        regulatory_version_id=regulatory_version_id,
        regulatory_version_name=version.name if version else "(unbekannt)",
        nachrichtentyp=nachrichtentyp,
        sparte=sparte,
        message_version=message_version,
    )
    if version is None:
        report.errors.append(f"RegulatoryVersion {regulatory_version_id} existiert nicht")
        return report

    ahb_before = (
        db.query(models.MessageDefinition)
        .filter(models.MessageDefinition.pi_nummer.isnot(None))
        .count()
    )

    report.extraction = extraction if extraction is not None else extract_segment_layout(pdf_path)
    if not report.extraction.form_recognized:
        report.warnings.append(
            "Erwartete Dokumentform nicht erkannt -- kein Import (Auftrag §7)"
        )
        return report
    if not report.extraction.crosscheck_ok:
        report.warnings.append(
            f"Gegenprobe gegen die Nachrichtenstruktur-Übersicht meldet "
            f"{len(report.extraction.crosscheck_notes)} Abweichung(en) -- "
            "importiert wird die Detailtabelle, die Abweichungen stehen im Report"
        )

    report.removed_previous = _delete_previous_generic_import(
        db, regulatory_version_id, file_hash
    )

    pages = report.extraction.pages
    definition = models.MessageDefinition(
        regulatory_version_id=regulatory_version_id,
        nachrichtentyp=nachrichtentyp,
        version=message_version,
        sparte=sparte,
        beschreibung=beschreibung or f"Generische Nachrichtenstruktur laut MIG ({document_name})",
        # Kein Pruefidentifikator: das ist der Kern der generischen Sicht.
        pi_nummer=None,
        pi_id=None,
        grammatik_quelle="MIG",
        quelle_dokument=document_name,
        quelle_hash=file_hash,
        # Die MIG hat keine nummerierte Kapitelstruktur (Befund aus Prompt 1).
        quelle_kapitel=None,
        quelle_kapitel_titel="Segmentlayout",
        quelle_seite_von=pages[0] if pages else None,
        quelle_seite_bis=max(s.source_page_end for s in report.extraction.segments)
        if report.extraction.segments else None,
    )
    db.add(definition)
    db.flush()
    report.definition_id = definition.id

    for position, segment in enumerate(report.extraction.segments, start=1):
        db_segment = models.MessageSegment(
            message_definition_id=definition.id,
            segment_code=segment.segment_code,
            position=position,
            bezeichnung=segment.name or None,
            # Abgeleitete Kompatibilitaetsspalte, nicht die Wahrheit -- siehe
            # pflicht_aus_status.
            pflicht=pflicht_aus_status(segment.status_bdew),
            # pflichtigkeit traegt AHB-Semantik (Muss/Soll/Kann) und bleibt leer.
            segmentgruppe=segment.segmentgruppe or None,
            mig_nr=segment.nr,
            mig_zaehler=segment.zaehler,
            segmentgruppen_pfad=segment.segmentgruppen_pfad or None,
            ebene=segment.ebene,
            status_standard_raw=segment.status_standard or None,
            status_bdew_raw=segment.status_bdew or None,
            max_wdh_standard=segment.max_wdh_standard or None,
            max_wdh_bdew=segment.max_wdh_bdew or None,
            anwendungshinweis="\n".join(segment.bemerkung) or None,
            beispiel_edifact="\n".join(segment.beispiel) or None,
            quelle_seite=segment.source_page,
        )
        db.add(db_segment)
        db.flush()
        report.segments_written += 1

        for extracted in segment.fields:
            db_field = models.MessageField(
                segment_id=db_segment.id,
                position=extracted.bez,
                bezeichnung=extracted.name or None,
                pflicht=pflicht_aus_status(extracted.status_bdew),
                status_standard_raw=extracted.status_standard or None,
                status_bdew_raw=extracted.status_bdew or None,
                format_standard_raw=extracted.format_standard or None,
                format_bdew_raw=extracted.format_bdew or None,
                anwendung_raw=extracted.anwendung_text or None,
                # datentyp/laenge bleiben leer: eine Zerlegung von "n5" bzw.
                # "n..6" verloere fest gegen variabel. codelist_id bleibt leer:
                # ein Feld referenziert bis zu 50 Codelisten, die Zuordnung
                # steht in message_field_code_lists.
                quelle_seite=extracted.source_page,
            )
            db.add(db_field)
            db.flush()
            report.fields_written += 1

            for referenz_id, referenz_raw in extracted.codelist_referenzen:
                codelist_id, note = _resolve_codelist(db, regulatory_version_id, referenz_id)
                db.add(models.MessageFieldCodeList(
                    message_field_id=db_field.id,
                    codelist_id=codelist_id,
                    referenz_id=referenz_id,
                    referenz_raw=referenz_raw,
                    quelle_seite=extracted.source_page,
                ))
                if codelist_id is not None:
                    report.codelist_links_resolved += 1
                else:
                    report.codelist_links_open.append(
                        f"{referenz_id} (S.{extracted.source_page}, "
                        f"{segment.segment_code} DE{extracted.bez}): {note}"
                    )

    db.commit()

    report.ahb_definitions_untouched = (
        db.query(models.MessageDefinition)
        .filter(models.MessageDefinition.pi_nummer.isnot(None))
        .count()
    )
    if report.ahb_definitions_untouched != ahb_before:
        report.errors.append(
            f"PI-spezifische MessageDefinitions haben sich veraendert: "
            f"{ahb_before} -> {report.ahb_definitions_untouched}"
        )
    return report


__all__ = [
    "LayoutExtraction",
    "LayoutField",
    "LayoutGroup",
    "LayoutImportReport",
    "LayoutSegment",
    "SkippedRow",
    "StructureRow",
    "collect_segment_layout",
    "collect_structure",
    "crosscheck",
    "detail_header_index",
    "extract_segment_layout",
    "import_mig_segment_layout",
    "is_furniture",
    "pflicht_aus_status",
    "resolve_active_regulatory_version",
]
