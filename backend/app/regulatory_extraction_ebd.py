"""Deterministische Extraktion des Codelisten-Teils aus "Entscheidungsbaum-Diagramme
und Codelisten fuer die Antwortnachrichten" 4.2 (Issue #50).

Vierter Baustein der Regulatory-Extraktionspipeline neben AHB
(``regulatory_extraction.py``), MIG (``regulatory_extraction_mig.py``) und der
Codeliste der OBIS-Kennzahlen (``regulatory_extraction_obis.py``). Gleiche
Architektur, bewusst OHNE LLM:

    Dokument -> Formpruefung -> deterministische Extraktion -> Wissensbasis

WIEDERVERWENDUNG STATT NEUBAU (Auftrag Abschnitt 11/16)
-------------------------------------------------------
Dieses Modul implementiert die Tabellenerkennung NICHT neu. Es importiert die
Geometrie- und Formpruefungsschicht aus ``regulatory_extraction_obis`` und
nutzt sie unveraendert -- es sind buchstaeblich dieselben Codeobjekte, nicht
kopierte Logik:

    _word_lines · _match_header_x0 · _locate_columns · _rows_from_table
    · _clean · TableForm · ColumnSpec · SkippedRow

Die empirische Untersuchung zu Issue #50 hat auf allen 851 Seiten belegt, dass
``_locate_columns`` EBD-Tabelle und Codeliste ohne jede Aenderung trennscharf
unterscheidet (0 Fehltreffer). Neu deklariert werden hier nur ``TableForm``-
Instanzen, also Daten. Eigener Code entsteht ausschliesslich dort, wo der
Befund eine echte Luecke gezeigt hat -- Abschnittsscan, Regionsbildung,
Zeilenaufbau ueber Seitenumbrueche.

Das Modul liegt neben ``regulatory_extraction_obis`` und nicht darin, weil
jenes auf sein Dokument zugeschnitten ist (feste Kapitelnummer je Form,
OBIS-Codemuster, Platzhalter-Legenden). Ein gemeinsames Basismodul erst
herauszuziehen, wenn ein drittes Codelisten-Dokument es rechtfertigt --
vorsorgliche Generalisierung waere gegen Auftrag Abschnitt 9.

BEFUNDE, DIE DEN AUFBAU BESTIMMEN (Issue #50, empirisch, nicht angenommen)
--------------------------------------------------------------------------
* Das Dokument beschreibt seine Form selbst. Kapitel 5: eine Codeliste fuehrt
  ``Code``/``Nutzung``/``Name``, bei Bedarf zusaetzlich ``Bedingung``.
  Kapitel 4: eine EBD-Tabelle fuehrt ``Nr.``/``Prüfschritt``/``Prüfergebnis``/
  ``Code``/``Hinweis``. BEIDE haben eine Spalte ``Code`` mit gleich
  aussehenden Werten -- eine Volltextsuche nach Codes wuerde zwingend
  EBD-Codes einsammeln. Die Unterscheidung ist deshalb rein strukturell.
* Vier Kopfzeilen-Varianten kommen real vor (``TABLE_FORMS``). Die Variante
  ``Code``/``Nutzung``/``Hinweis``/``Name`` nennt Kapitel 5 nicht.
* Codelisten-Abschnitte tragen die Praefixe ``S_`` (Strom), ``G_`` (Gas) und
  ``GS_`` (beide); EBD-Abschnitte ``E_``. Das ist das zweite, unabhaengige
  Unterscheidungsmerkmal neben der Kopfzeile.
* Die Ueberschrift "6 GPKE" ist in Grad 9,0 gesetzt, alle anderen
  Top-Level-Ueberschriften in Grad 12,0 -- eine Typografie-Anomalie des
  Dokuments. Die Schwellwerte aus der OBIS-Extraktion tragen deshalb nicht
  (siehe ``_HEADING_MIN_SIZE``).
* Eine Codeliste laeuft ueber Seitenumbrueche, ohne die Kopfzeile
  zwingend zu wiederholen (S. 159). Die Spaltengeometrie wird deshalb
  innerhalb eines Abschnitts ueber Seiten hinweg mitgefuehrt.
* Kapitel 19 (Aenderungshistorie) ist ein Nicht-Datenbereich.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Sequence

import pdfplumber
from sqlalchemy.orm import Session

from . import models
from .regulatory_extraction import compute_file_hash, resolve_active_regulatory_version
# Unveraendert wiederverwendete Form- und Geometrieschicht aus Issue #48.
# Die fuehrenden Unterstriche markieren sie als modulintern; sie hier zu
# importieren statt zu kopieren ist der Punkt: es ist derselbe Code, nicht
# derselbe Algorithmus zweimal geschrieben.
from .regulatory_extraction_obis import (  # noqa: F401
    ColumnSpec,
    SkippedRow,
    TableForm,
    _clean,
    _locate_columns,
    _match_header_x0,
    _rows_from_table,
    _word_lines,
)

# ---------------------------------------------------------------------------
# Konstanten der erwarteten Dokumentform
# ---------------------------------------------------------------------------

# Antwortcode in der Schreibweise des Dokuments: entweder rein numerisch
# ("5", "9", "28", "53") oder ein bis zwei Buchstaben mit Ziffern ("Z01",
# "ZB5", "E17", "A01"). Bewusst eng gefasst -- die Spalte ``Code`` ist die
# erste Spalte, ein zu weites Muster wuerde umbrochenen Fliesstext greifen.
_RE_ANTWORTCODE = re.compile(r"^[A-Z]{0,2}\d{1,3}$")

# Abschnittspraefixe. E_ ist der Entscheidungsbaum und wird bewusst
# ausgeklammert (Auftrag Abschnitt 10), S_/G_/GS_ sind Codelisten.
_RE_SEC_CODELIST = re.compile(r"^(?:GS|S|G)_\d+")
_RE_SEC_EBD = re.compile(r"^E_\d+")

# Ueberschrift: fett, am linken Satzspiegel, Nummer als erstes Wort.
# Grad 8,5 statt der 11,0 aus der OBIS-Extraktion -- "6 GPKE" ist in Grad 9,0
# gesetzt und faellt sonst aus der Gliederung. Die Absenkung ist gefahrlos:
# die Kombination "fett UND erstes Wort ist eine Gliederungsnummer" trifft im
# ganzen Dokument ausschliesslich die 485 Abschnitts- und 19 Kapitel-
# ueberschriften, keine einzige Datenzeile (empirisch geprueft, Issue #50).
# x0-Grenze 130 statt 110: die Ebene-2-Ueberschriften (``AD:``/``SD:``) stehen
# bei x0 = 119,7.
_HEADING_MIN_SIZE = 8.5
_HEADING_MAX_X0 = 130.0
_RE_HEADING_NUM = re.compile(r"^\d{1,2}(?:\.\d+)*$")

# Schriftgrad, ab dem eine Zeile Tabelleninhalt sein kann. Die Kopfzeile des
# Dokuments steht in Grad 6,96, der Tabellenkoerper in Grad 12,0.
_BODY_MIN_SIZE = 8.0

# Seitenfuss des Dokuments ("Version: 4.2 01.10.2025 Seite 157 von 851").
_RE_FOOTER = re.compile(r"^\s*Version:\s")

# Kapitel 19 -- Nicht-Datenbereich, analog Kapitel 7 der OBIS-Codeliste.
_CHANGELOG_HEADING = "Änderungshistorie"

# Nachrichtentypen, die im Abschnittstitel woertlich vorkommen koennen. Nur
# dann wird ``CodeList.nachrichtentyp`` gefuellt -- der Befund hat gezeigt,
# dass die Mehrzahl der Codelisten keinen Nachrichtentyp nennt. Raten waere
# ein fachlicher Eingriff (Auftrag Abschnitt 14).
_MESSAGE_TYPES = (
    "UTILMD", "MSCONS", "APERAK", "COMDIS", "INVOIC", "ORDERS", "ORDRSP",
    "REMADV", "PARTIN", "IFTSTA", "CONTRL", "UTILTS",
)


# ---------------------------------------------------------------------------
# Die real vorgefundenen Kopfzeilen-Varianten (Issue #50, Befund)
#
# Reihenfolge ist bedeutsam: die vierspaltigen Formen zuerst. Eine
# vierspaltige Tabelle erfuellt auch die dreispaltige Form (Code/Nutzung/Name
# liegen ebenfalls aufsteigend), die dreispaltige wuerde die mittlere Spalte
# also stillschweigend in die Bedeutung ziehen.
# ---------------------------------------------------------------------------

TABLE_FORMS: tuple[TableForm, ...] = (
    TableForm(
        key="codeliste-bedingung",
        codelist_name="", chapter="",
        beschreibung="Codeliste mit Bedingungsspalte (Kapitel 5).",
        columns=(
            ColumnSpec("Code", "code"),
            ColumnSpec("Nutzung", "status"),
            ColumnSpec("Bedingung", "hinweise"),
            ColumnSpec("Name", "bedeutung"),
        ),
        pages=(), code_pattern=_RE_ANTWORTCODE, split_multi_codes=False,
    ),
    TableForm(
        key="codeliste-hinweis",
        codelist_name="", chapter="",
        beschreibung="Codeliste mit Hinweisspalte (von Kapitel 5 nicht genannt).",
        columns=(
            ColumnSpec("Code", "code"),
            ColumnSpec("Nutzung", "status"),
            ColumnSpec("Hinweis", "hinweise"),
            ColumnSpec("Name", "bedeutung"),
        ),
        pages=(), code_pattern=_RE_ANTWORTCODE, split_multi_codes=False,
    ),
    TableForm(
        key="codeliste-basis",
        codelist_name="", chapter="",
        beschreibung="Codeliste in der Grundform Code/Nutzung/Name (Kapitel 5).",
        columns=(
            ColumnSpec("Code", "code"),
            ColumnSpec("Nutzung", "status"),
            ColumnSpec("Name", "bedeutung"),
        ),
        pages=(), code_pattern=_RE_ANTWORTCODE, split_multi_codes=False,
    ),
)

# Gegenprobe, NICHT zum Import: die EBD-Tabelle aus Kapitel 4. Sie wird
# gebraucht, um einen EBD-Abschnitt positiv als "bewusst ausgeklammert"
# auszuweisen statt ihn nur stillschweigend nicht zu treffen
# (Auftrag Abschnitt 6).
EBD_FORM = TableForm(
    key="ebd-tabelle",
    codelist_name="", chapter="", beschreibung="",
    columns=(
        ColumnSpec("Nr.", "ignore"),
        ColumnSpec("Prüfschritt", "ignore"),
        ColumnSpec("Prüfergebnis", "ignore"),
        ColumnSpec("Code", "code"),
        ColumnSpec("Hinweis", "hinweise"),
    ),
    pages=(), code_pattern=_RE_ANTWORTCODE, split_multi_codes=False,
)


# ---------------------------------------------------------------------------
# Ergebnisstrukturen
# ---------------------------------------------------------------------------

@dataclass
class EbdEntry:
    """Ein extrahierter Codelisteneintrag, Rohwerte des Dokuments."""
    code: str
    bedeutung: str = ""
    nutzung: str = ""
    hinweise: str = ""
    source_page: int = 0
    section: str = ""          # "6.10.2"
    codelist_name: str = ""    # "S_0103_Netznutzungsrechnung prüfen"
    prozessfamilie: str = ""   # "6 GPKE"
    form_key: str = ""
    nachrichtentyp: str = ""


@dataclass
class DeferredCodeList:
    """Codeliste, die bewusst NICHT importiert wird (Auftrag Abschnitt 14)."""
    section: str
    name: str
    page: int
    reason: str


@dataclass
class EbdImportReport:
    document: str = ""
    file_hash: str = ""
    regulatory_version: str = ""
    codelist_sections: int = 0
    codelists_detected: int = 0
    codelists_created: int = 0
    entries_imported: int = 0
    ebd_sections: int = 0
    ebd_page_first: int = 0
    ebd_page_last: int = 0
    ebd_pages_with_table: int = 0
    deferred: list[DeferredCodeList] = field(default_factory=list)
    empty_sections: list[DeferredCodeList] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    reimported: bool = False
    entries_by_form: dict[str, int] = field(default_factory=dict)
    entries_by_family: dict[str, int] = field(default_factory=dict)

    def format_report(self) -> str:
        out: list[str] = []
        out.append(f"Dokument:            {self.document}")
        out.append(f"SHA-256:             {self.file_hash}")
        out.append(f"RegulatoryVersion:   {self.regulatory_version}")
        out.append("")
        out.append(f"Codelisten-Abschnitte (S_/G_/GS_): {self.codelist_sections:>5}")
        out.append(f"  ohne Tabelle (Prosa/Querverweis):{len(self.empty_sections):>5}")
        out.append(f"  zurückgestellt (Sonderfall):     {len(self.deferred):>5}")
        out.append(f"Codelisten importiert:             {self.codelists_created:>5}")
        out.append(f"CodeListEntries importiert:        {self.entries_imported:>5}")
        if self.reimported:
            out.append("Hinweis: voriger Stand derselben Datei wurde ersetzt (--reimport).")
        out.append("")
        out.append("EBD-Abschnitte (bewusst ausgeklammert, Auftrag Abschnitt 10):")
        out.append(f"  Abschnitte E_XXXX_:    {self.ebd_sections:>5}")
        out.append(f"  Seitenbereich:         S.{self.ebd_page_first}-{self.ebd_page_last}")
        out.append(f"  Seiten mit EBD-Tabelle:{self.ebd_pages_with_table:>5}")
        out.append("  Nicht extrahiert: weder als Bild noch in eine Tabellenstruktur"
                   " gepresst.")
        if self.entries_by_form:
            out.append("")
            out.append("Einträge je Tabellenform:")
            for key in sorted(self.entries_by_form):
                out.append(f"  {key:<26} {self.entries_by_form[key]:>5}")
        if self.entries_by_family:
            out.append("")
            out.append("Einträge je Prozessfamilie:")
            for key in sorted(self.entries_by_family, key=lambda k: int(k.split()[0])):
                out.append(f"  {key:<52} {self.entries_by_family[key]:>5}")
        if self.deferred:
            out.append("")
            out.append(f"Zurückgestellte Codelisten ({len(self.deferred)}):")
            for d in self.deferred:
                out.append(f"  {d.section} {d.name} (S.{d.page})")
                out.append(f"     Grund: {d.reason}")
        if self.empty_sections:
            out.append("")
            out.append(f"Abschnitte ohne Tabelle ({len(self.empty_sections)}) -- "
                       "Prosa/Querverweis, keine leere CodeList angelegt:")
            for d in self.empty_sections[:20]:
                out.append(f"  {d.section} {d.name} (S.{d.page})")
            if len(self.empty_sections) > 20:
                out.append(f"  ... und {len(self.empty_sections) - 20} weitere")
        if self.duplicates:
            out.append("")
            out.append(f"Sonderfälle Duplikate ({len(self.duplicates)}):")
            for d in self.duplicates:
                out.append(f"  {d}")
        if self.skipped:
            out.append("")
            out.append(f"Übersprungene Zeilen ({len(self.skipped)}):")
            for s in self.skipped[:40]:
                out.append(f"  S.{s.page} [{s.form_key}] {s.reason}: {s.raw[:60]}")
            if len(self.skipped) > 40:
                out.append(f"  ... und {len(self.skipped) - 40} weitere")
        if self.errors:
            out.append("")
            out.append("FEHLER:")
            for e in self.errors:
                out.append(f"  {e}")
        return "\n".join(out)


# ---------------------------------------------------------------------------
# Abschnittsgliederung
# ---------------------------------------------------------------------------

@dataclass
class Section:
    """Ein Abschnitt beliebiger Gliederungstiefe (bis 11.2.1.1.1)."""
    number: str
    title: str
    page: int
    top: float
    end_page: int = 0
    end_top: float = 0.0

    @property
    def level(self) -> int:
        return self.number.count(".") + 1

    @property
    def is_codelist(self) -> bool:
        return bool(_RE_SEC_CODELIST.match(self.title))

    @property
    def is_ebd(self) -> bool:
        return bool(_RE_SEC_EBD.match(self.title))


def _is_heading(line) -> bool:
    words = sorted(line.words, key=lambda w: w["x0"])
    if not words:
        return False
    first = words[0]
    if first["x0"] > _HEADING_MAX_X0:
        return False
    if "Bold" not in (first.get("fontname") or ""):
        return False
    if float(first.get("size") or 0) < _HEADING_MIN_SIZE:
        return False
    return bool(_RE_HEADING_NUM.match(first["text"]))


def scan_sections(pdf, toc_pages: int = 22) -> list[Section]:
    """Vollstaendige Gliederung aus den Ueberschriftenzeilen lesen.

    Die Abschnitte werden ueber ihr NAMENSMUSTER lokalisiert, nicht ueber
    feste Seitenzahlen -- 127 Codelisten in Abschnitten bis zur Tiefe
    ``11.2.1.1.1`` liessen sich sonst nicht fuehren, und eine spaetere Fassung
    duerfte keine Seite verschieben.

    ``toc_pages`` schneidet das Inhaltsverzeichnis ab. Dort sind die Eintraege
    ebenfalls fett und beginnen am linken Rand; ohne den Schnitt faende der
    Scan jedes Kapitel doppelt und wuerde die Regionen zerreissen.
    """
    sections: list[Section] = []
    for pageno, page in enumerate(pdf.pages, start=1):
        if pageno <= toc_pages:
            continue
        for line in _word_lines(page):
            if not _is_heading(line):
                continue
            words = sorted(line.words, key=lambda w: w["x0"])
            number = words[0]["text"]
            title = " ".join(w["text"] for w in words[1:]).strip()
            if len(title) < 3:
                continue
            sections.append(Section(number=number, title=title,
                                    page=pageno, top=line.top))
    for cur, nxt in zip(sections, sections[1:]):
        cur.end_page, cur.end_top = nxt.page, nxt.top
    if sections:
        sections[-1].end_page = len(pdf.pages)
        sections[-1].end_top = 10 ** 6
    return sections


def changelog_start_page(sections: Sequence[Section]) -> int | None:
    """Erste Seite der Aenderungshistorie -- expliziter Nicht-Datenbereich.

    Die Formpruefung schliesst Kapitel 19 bereits von selbst aus (seine
    Spalten sind ``Änd-ID``/``Ort``/``Änderungen``/``Grund``/``Status``).
    Die Grenze wird trotzdem hart gezogen und per Regressionstest gehalten:
    das Kapitel zitiert Codes und Prüfschritte frueherer Staende, und eine
    kuenftige Fassung koennte sie tabellarisch darstellen.
    """
    for s in sections:
        if s.level == 1 and s.title.startswith(_CHANGELOG_HEADING):
            return s.page
    return None


def _family_of(sections: Sequence[Section], target: Section) -> str:
    """Top-Level-Kapitel eines Abschnitts -- die Prozessfamilie.

    Der Nachrichtentyp ist laut Befund fuer die Mehrzahl der Codelisten nicht
    bestimmbar; die Prozessfamilie dagegen immer. Sie ist die verlaessliche
    fachliche Einordnung und geht in ``CodeList.beschreibung``.
    """
    family = ""
    for s in sections:
        if s.page > target.page or (s.page == target.page and s.top > target.top):
            break
        if s.level == 1:
            family = f"{s.number} {s.title}"
    return family


def _message_type_of(title: str) -> str:
    """Nachrichtentyp NUR, wenn er woertlich im Abschnittstitel steht."""
    for mt in _MESSAGE_TYPES:
        if mt in title:
            return mt
    return ""


def _section_region(section: Section, pages: int) -> list[tuple[int, float, float]]:
    """Seiten eines Abschnitts als (Seite, top_min, top_max).

    Zeilengenau, weil mehrere Abschnitte auf derselben Seite liegen koennen
    (S. 792 traegt 14.6.3, 14.6.4, 14.7.1 und 14.7.2).
    """
    out: list[tuple[int, float, float]] = []
    end_page = min(section.end_page or pages, pages)
    for pageno in range(section.page, end_page + 1):
        lo = section.top if pageno == section.page else 0.0
        hi = section.end_top if pageno == end_page else 10 ** 6
        if hi > lo:
            out.append((pageno, lo, hi))
    return out


# ---------------------------------------------------------------------------
# Tabellenlesen
# ---------------------------------------------------------------------------

def _table_bottom(lines, first_body: int, page_height: float, page=None,
                  xs: Sequence[float] | None = None, top: float = 0.0) -> float:
    """Untere Grenze des Tabellenkoerpers auf einer Seite.

    Eigene Funktion statt ``_body_end`` aus der OBIS-Extraktion: jene beendet
    den Koerper zusaetzlich an Platzhalter-Legenden und Fussnotendefinitionen,
    die es nur in der OBIS-Codeliste gibt. Hier beenden ihn die naechste
    Ueberschrift und der Seitenfuss.

    Danach wird zusaetzlich auf die letzte waagerechte RAHMENLINIE der Tabelle
    eingekuerzt. Das ist kein Schoenheitsschnitt: ``_rows_from_table`` leitet
    die rechte Tabellenkante aus den senkrechten Kanten im Schnittbereich ab.
    Reicht der Bereich ueber die Tabelle hinaus, geraet eine Seitenrahmenlinie
    (x = 794) hinein, die rechte Kante wandert weit nach rechts, pdfplumber
    findet fuer die letzte Spalte keine Kreuzung mehr und verwirft sie --
    die Spalte ``Name`` kaeme dann leer an (nachgewiesen an S. 771, G_0089).
    """
    limit = page_height
    for i in range(first_body, len(lines)):
        line = lines[i]
        if _RE_FOOTER.match(line.text.strip()) or _is_heading(line):
            limit = line.top - 1
            break
    if page is None or not xs:
        return limit
    rules = [
        e["top"] for e in page.edges
        if e["orientation"] == "h"
        and e["x0"] <= xs[-1] and e["x1"] >= xs[0]
        and top < e["top"] <= limit
    ]
    return max(rules) if rules else limit


def _table_top_from_edges(page, lines, xs: Sequence[float]) -> float | None:
    """Schnittkante oberhalb der ersten Datenzeile einer Fortsetzungsseite.

    Auf einer Seite ohne wiederholte Kopfzeile darf der Schnitt NICHT beim
    ersten Text der Seite beginnen: dort steht die Kopfzeile des Dokuments
    ("Entscheidungsbaum-Diagramme und Codelisten ..."). Nimmt man sie mit,
    verschiebt pdfplumber das Zeilenraster -- Code und Bedeutung landen dann in
    verschiedenen Zeilen (nachgewiesen an S. 770, G_0081: Z07 kam ohne
    Bedeutung an).

    Die Dokumentkopfzeile ist an ihrem Schriftgrad zu erkennen (6,96 gegen 12,0
    im Tabellenkoerper). Geschnitten wird an der letzten waagerechten
    Rahmenlinie oberhalb der ersten echten Datenzeile -- also genau auf der
    Zeilentrennlinie der Tabelle, damit das Raster deckungsgleich bleibt.
    """
    first = next(
        (ln for ln in lines
         if max((float(w.get("size") or 0) for w in ln.words), default=0) >= _BODY_MIN_SIZE),
        None,
    )
    if first is None:
        return None
    edges = [
        e["top"] for e in page.edges
        if e["orientation"] == "h"
        and e["x0"] <= xs[-1] and e["x1"] >= xs[0]
        and e["top"] < first.top
    ]
    return max(edges) if edges else first.top - 2


def _table_right_edge(page, xs: Sequence[float], top: float, bottom: float) -> float | None:
    """Rechte Rahmenlinie der Tabelle.

    ``_rows_from_table`` nimmt die AEUSSERSTE senkrechte Kante rechts der
    letzten Spalte. In diesem Dokument geraten dabei kurze Seitendekorations-
    kanten (x = 727 auf S. 771) in die Auswahl; die rechte Kante wandert
    dorthin, pdfplumber findet fuer die Spalte ``Name`` keine Kreuzung mehr und
    verwirft sie. Die echte Rahmenlinie ist die, die ueber die Tabellenhoehe
    laeuft -- gewaehlt wird deshalb die Kante mit der groessten Ueberdeckung
    des Zeilenbandes (S. 771: 152 Punkte gegen 0,9).

    Die Seite wird anschliessend auf diese Breite beschnitten, damit
    ``_rows_from_table`` unveraendert bleiben kann.
    """
    best_x: float | None = None
    best_overlap = 0.0
    for e in page.edges:
        if e["orientation"] != "v" or not (xs[-1] < e["x0"] <= page.width):
            continue
        overlap = min(e["bottom"], bottom) - max(e["top"], top)
        if overlap > best_overlap:
            best_overlap, best_x = overlap, e["x0"]
    return best_x


def _count_header_occurrences(lines, start: int, header: str, span: int = 5) -> int:
    """Wie oft eine Kopfzelle im Kopfband vorkommt.

    Traegt eine Tabelle ZWEI ``Bedingung``-Spalten, sind es zwei fachlich
    verschiedene Bedingungen je Code (S_0109: eine fuer Codes aus S_0103, eine
    fuer Codes aus dem EBD E_0406). ``CodeListEntry`` hat dafuer ein Feld;
    die vierspaltige Form wuerde beide in eine Zelle ziehen und die Zuordnung
    "welche Bedingung gilt wann" vernichten. Solche Listen werden deshalb
    zurueckgestellt statt verfaelscht importiert (Auftrag Abschnitt 14,
    Entscheidung zu Issue #50).
    """
    band = [w for ln in lines[start:start + span] for w in ln.words]
    return sum(1 for w in band if w["text"] == header)


def _read_section(
    pdf, section: Section, family: str, skipped: list[SkippedRow]
) -> tuple[list[EbdEntry], str, DeferredCodeList | None]:
    """Alle Codelisteneintraege eines Abschnitts lesen.

    Rueckgabe: (Eintraege, Formschluessel, Zurueckstellung oder None).
    """
    entries: list[EbdEntry] = []
    form_key = ""
    nachrichtentyp = _message_type_of(section.title)
    # Spaltengeometrie wird ueber Seitengrenzen mitgefuehrt: eine Codeliste
    # wiederholt die Kopfzeile auf der Folgeseite NICHT zwingend (S. 159).
    carry: tuple[TableForm, list[float]] | None = None

    for pageno, lo, hi in _section_region(section, len(pdf.pages)):
        page = pdf.pages[pageno - 1]
        lines = [ln for ln in _word_lines(page) if lo <= ln.top <= hi]
        if not lines:
            continue

        header_idx = None
        found: tuple[TableForm, list[float], int] | None = None
        for idx in range(len(lines)):
            for form in TABLE_FORMS:
                located = _locate_columns(form, lines, idx)
                if located:
                    xs, header_end = located
                    found = (form, xs, header_end)
                    header_idx = idx
                    break
            if found:
                break

        if found:
            form, xs, header_end = found
            # Zwei Bedingungsspalten -> ganzer Abschnitt zurueckgestellt.
            if _count_header_occurrences(lines, header_idx, "Bedingung") > 1:
                return [], "", DeferredCodeList(
                    section=section.number, name=section.title, page=pageno,
                    reason=("Tabelle führt zwei fachlich unterschiedliche "
                            "Bedingungsspalten je Code; das bestehende Feld "
                            "hinweise kann die Zuordnung nicht abbilden."),
                )
            carry = (form, xs)
            form_key = form.key
            top = lines[header_end].bottom + 1
            body_start = header_end + 1
        elif carry is not None:
            # Fortsetzung ohne wiederholte Kopfzeile.
            form, xs = carry
            edge_top = _table_top_from_edges(page, lines, xs)
            if edge_top is None:
                continue
            top = edge_top
            body_start = 0
        else:
            continue

        bottom = _table_bottom(lines, body_start, page.height, page, xs, top)
        if bottom <= top:
            continue
        right_edge = _table_right_edge(page, xs, top, bottom)
        surface = page
        if right_edge is not None:
            surface = page.crop((0, 0, min(right_edge + 2, page.width), page.height))
        table = _rows_from_table(surface, form, xs, top, bottom)
        code_col = next(i for i, c in enumerate(form.columns) if c.target == "code")

        for row in table:
            cells = [_clean(c) for c in row]
            if len(cells) != len(form.columns):
                # Nicht stillschweigend auffuellen: eine fehlende Spalte ist
                # ein Geometriefehler und wuerde sonst als leere Bedeutung
                # durchgehen statt aufzufallen (Auftrag Abschnitt 14).
                skipped.append(SkippedRow(
                    pageno, form.key,
                    f"Zeile mit {len(cells)} statt {len(form.columns)} Spalten",
                    " ".join(c for c in cells if c)[:120],
                ))
                continue
            raw_code = cells[code_col]
            if raw_code and form.code_pattern.match(raw_code):
                e = EbdEntry(
                    code=raw_code, source_page=pageno, section=section.number,
                    codelist_name=section.title, prozessfamilie=family,
                    form_key=form.key, nachrichtentyp=nachrichtentyp,
                )
                for i, col in enumerate(form.columns):
                    if col.target == "bedeutung":
                        e.bedeutung = cells[i]
                    elif col.target == "status":
                        e.nutzung = cells[i]
                    elif col.target == "hinweise":
                        e.hinweise = cells[i]
                entries.append(e)
                continue
            if raw_code:
                # Etwas steht in der Code-Spalte, ist aber kein Code.
                skipped.append(SkippedRow(
                    pageno, form.key, "Code-Spalte ohne gültigen Code",
                    " ".join(c for c in cells if c)[:120],
                ))
                continue
            # Zeile ohne Code: Fortsetzung des VORIGEN Eintrags. Ueber einen
            # Seitenumbruch hinweg ist das der letzte Eintrag der Vorseite --
            # nicht der erste der neuen Seite (Befund zu Issue #50).
            if not entries:
                continue
            prev = entries[-1]
            for i, col in enumerate(form.columns):
                if not cells[i]:
                    continue
                if col.target == "bedeutung":
                    prev.bedeutung = f"{prev.bedeutung} {cells[i]}".strip()
                elif col.target == "hinweise":
                    prev.hinweise = f"{prev.hinweise} {cells[i]}".strip()

    return entries, form_key, None


def extract_ebd_codelists(pdf_path: str):
    """Codelisten-Teil des Dokuments lesen; EBD-Abschnitte ausklammern."""
    entries: list[EbdEntry] = []
    skipped: list[SkippedRow] = []
    deferred: list[DeferredCodeList] = []
    empty: list[DeferredCodeList] = []
    stats: dict[str, int] = {}

    with pdfplumber.open(pdf_path) as pdf:
        sections = scan_sections(pdf)
        cutoff = changelog_start_page(sections) or (len(pdf.pages) + 1)

        ebd_sections = [s for s in sections if s.is_ebd and s.page < cutoff]
        stats["ebd_sections"] = len(ebd_sections)
        stats["ebd_page_first"] = min((s.page for s in ebd_sections), default=0)
        stats["ebd_page_last"] = max((s.page for s in ebd_sections), default=0)

        # EBD-Seiten positiv ausweisen: die EBD-Form wird gesucht, um sie als
        # "bewusst ausgeklammert" zaehlen zu koennen -- nicht, um sie zu lesen.
        ebd_pages: set[int] = set()
        for s in ebd_sections:
            for pageno, lo, hi in _section_region(s, len(pdf.pages)):
                if pageno >= cutoff or pageno in ebd_pages:
                    continue
                lines = [ln for ln in _word_lines(pdf.pages[pageno - 1])
                         if lo <= ln.top <= hi]
                cand = [i for i, ln in enumerate(lines)
                        if any(w["text"] == "Nr." for w in ln.words)]
                if any(_locate_columns(EBD_FORM, lines, i) for i in cand):
                    ebd_pages.add(pageno)
        stats["ebd_pages_with_table"] = len(ebd_pages)

        detected = 0
        stats["codelist_sections"] = sum(
            1 for s in sections if s.is_codelist and s.page < cutoff)
        for section in sections:
            if not section.is_codelist or section.page >= cutoff:
                continue
            family = _family_of(sections, section)
            got, _form_key, defer = _read_section(pdf, section, family, skipped)
            if defer is not None:
                detected += 1
                deferred.append(defer)
                continue
            if not got:
                # Abschnitt ohne Tabelle: Prosa-Platzhalter oder Querverweis
                # ("Es ist die Codeliste G_0079 zu nutzen."). Keine leere
                # CodeList anlegen.
                empty.append(DeferredCodeList(
                    section=section.number, name=section.title, page=section.page,
                    reason="Abschnitt enthält keine Codelisten-Tabelle.",
                ))
                continue
            detected += 1
            entries.extend(got)
        stats["codelists_detected"] = detected

    return entries, skipped, deferred, empty, stats


# ---------------------------------------------------------------------------
# Import in die Wissensbasis
# ---------------------------------------------------------------------------

def _existing_import(db: Session, regulatory_version_id: int, file_hash: str) -> int:
    return (
        db.query(models.CodeList)
        .filter(
            models.CodeList.regulatory_version_id == regulatory_version_id,
            models.CodeList.quelle_hash == file_hash,
        )
        .count()
    )


def _delete_previous_import(db: Session, regulatory_version_id: int, file_hash: str) -> None:
    """Vorigen Stand derselben Datei entfernen -- kontrollierter Re-Import."""
    lists = (
        db.query(models.CodeList)
        .filter(
            models.CodeList.regulatory_version_id == regulatory_version_id,
            models.CodeList.quelle_hash == file_hash,
        )
        .all()
    )
    ids = [c.id for c in lists]
    if not ids:
        return
    db.query(models.CodeListEntry).filter(
        models.CodeListEntry.codelist_id.in_(ids)
    ).delete(synchronize_session=False)
    db.query(models.CodeList).filter(
        models.CodeList.id.in_(ids)
    ).delete(synchronize_session=False)
    db.flush()


def import_ebd_codelists(
    db: Session,
    pdf_path: str,
    regulatory_version_id: int,
    reimport: bool = False,
) -> EbdImportReport:
    """Codelisten-Teil des EBD-Dokuments in CodeList/CodeListEntry uebernehmen.

    KEINE globale Deduplizierung ueber den Codewert. Die fachliche Identitaet
    eines Antwortcodes entsteht erst aus RegulatoryVersion + CodeList + Code:
    ``Z07`` heisst in ``S_0103`` "Netznutzungsmesswerte / -energiemengen
    fehlen" und in ``G_0060`` "Ablehnung (Keine Berechtigung)". Das Dokument
    sagt das in Kapitel 3 selbst ("Die Antwortcodes haben eine
    unterschiedliche Bedeutung je EBD."). Zusammengefuehrt wird deshalb
    ausschliesslich INNERHALB einer CodeList.
    """
    report = EbdImportReport(document=pdf_path)
    report.file_hash = compute_file_hash(pdf_path)

    version = db.get(models.RegulatoryVersion, regulatory_version_id)
    if version is None:
        report.errors.append(f"RegulatoryVersion {regulatory_version_id} existiert nicht.")
        return report
    report.regulatory_version = f"[{version.id}] {version.name}"

    if _existing_import(db, regulatory_version_id, report.file_hash):
        if not reimport:
            report.errors.append(
                "Diese Datei ist fuer diese RegulatoryVersion bereits importiert "
                "(gleicher SHA-256). Mit --reimport erzwingen."
            )
            return report
        _delete_previous_import(db, regulatory_version_id, report.file_hash)
        report.reimported = True

    entries, skipped, deferred, empty, stats = extract_ebd_codelists(pdf_path)
    report.skipped = skipped
    report.deferred = deferred
    report.empty_sections = empty
    report.codelists_detected = stats.get("codelists_detected", 0)
    report.codelist_sections = stats.get("codelist_sections", 0)
    report.ebd_sections = stats.get("ebd_sections", 0)
    report.ebd_page_first = stats.get("ebd_page_first", 0)
    report.ebd_page_last = stats.get("ebd_page_last", 0)
    report.ebd_pages_with_table = stats.get("ebd_pages_with_table", 0)

    gueltig_ab: date | None = version.valid_from.date() if version.valid_from else None

    # Gruppierung ueber (Abschnittsnummer, Abschnittstitel): der Titel allein
    # traegt nicht -- "G_0016_Antwort auf Änderung vom NB" kommt in Kapitel 13
    # viermal in verschiedenen Abschnitten vor. Jedes Vorkommen ist eine
    # eigene Codeliste in ihrem eigenen fachlichen Kontext.
    by_list: dict[tuple[str, str], list[EbdEntry]] = {}
    for e in entries:
        by_list.setdefault((e.section, e.codelist_name), []).append(e)

    for (section, name), items in by_list.items():
        first = items[0]
        beschreibung = (
            f"Codeliste der Antwortcodes zum Anwendungsfall „{name}“ "
            f"(Abschnitt {section}). Prozessfamilie: {first.prozessfamilie}."
        )
        codelist = models.CodeList(
            regulatory_version_id=regulatory_version_id,
            name=name,
            nachrichtentyp=first.nachrichtentyp or None,
            beschreibung=beschreibung,
            quelle_dokument=pdf_path,
            quelle_hash=report.file_hash,
            quelle_kapitel=section,
        )
        db.add(codelist)
        db.flush()
        report.codelists_created += 1

        # Zusammenfuehrung NUR innerhalb dieser CodeList.
        seen: dict[str, EbdEntry] = {}
        for e in items:
            if e.code in seen:
                prev = seen[e.code]
                if prev.bedeutung != e.bedeutung:
                    report.duplicates.append(
                        f"{section} {name}: Code {e.code!r} doppelt mit abweichender "
                        f"Bedeutung ({prev.bedeutung[:40]!r} S.{prev.source_page} vs "
                        f"{e.bedeutung[:40]!r} S.{e.source_page}) -- nicht importiert"
                    )
                else:
                    report.duplicates.append(
                        f"{section} {name}: Code {e.code!r} identisch doppelt "
                        f"(S.{prev.source_page}/S.{e.source_page}) -- einmal importiert"
                    )
                continue
            seen[e.code] = e
            if not e.bedeutung:
                report.skipped.append(SkippedRow(
                    e.source_page, e.form_key, "Code ohne Bedeutung", e.code
                ))
                continue
            db.add(models.CodeListEntry(
                codelist_id=codelist.id,
                code=e.code,
                bedeutung=e.bedeutung,
                # "Nutzung" (X/O) ist die Nutzungswiederholbarkeit aus Kapitel 5.
                # Sie geht in das bestehende Feld status -- ein eigenes Feld
                # waere eine Schemaaenderung ohne zwingenden Befund.
                status=e.nutzung or None,
                hinweise=e.hinweise or None,
                gueltig_ab=gueltig_ab,
                gueltig_bis=None,
                quelle_seite=e.source_page,
            ))
            report.entries_imported += 1
            report.entries_by_form[e.form_key] = report.entries_by_form.get(e.form_key, 0) + 1
            fam = e.prozessfamilie or "(ohne Kapitel)"
            report.entries_by_family[fam] = report.entries_by_family.get(fam, 0) + 1

    db.commit()
    return report
