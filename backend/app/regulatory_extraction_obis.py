"""Deterministische Extraktion der Codeliste der OBIS-Kennzahlen und Medien (Issue #48).

Dritter Baustein der Regulatory-Extraktionspipeline neben der AHB-Extraktion in
``regulatory_extraction.py`` und der MIG-Extraktion in
``regulatory_extraction_mig.py``. Gleiche Architektur:

    Dokument -> Formpruefung -> deterministische Extraktion -> Wissensbasis

Bewusst OHNE LLM (Auftrag Abschnitt 13).

Eigenes Modul statt Erweiterung der beiden bestehenden: jene sind auf ihr
jeweiliges Dokument zugeschnitten (AHB: Spaltengeometrie/Kapitelscan/Fussnoten,
MIG: Datenelement-Anker). Gemeinsam genutzt wird nur, was wirklich generisch
ist -- ``compute_file_hash`` und ``resolve_active_regulatory_version``.

Die Formspezifikationen stammen aus der empirischen Strukturanalyse des echten
Dokuments 2.5c (Issue #48, Befund) und NICHT aus einer Annahme. Die Befunde,
die den Aufbau bestimmen:

* Das Dokument enthaelt **zehn** strukturell verschiedene Tabellenformen. Nur
  sieben davon sind Wertelisten; extrahiert werden die freigegebenen Formen
  1, 2, 3, 6, 7, 8, 9 (siehe ``TABLE_FORMS``).
* ``page.extract_tables()`` ohne Vorgaben zerlegt die Tabellen in bis zu 17
  Fragmentspalten fuer 6 logische. Die Spaltengrenzen werden deshalb zur
  Laufzeit aus den **Kopfzeilen-Wortpositionen** hergeleitet und pdfplumber als
  ``explicit_vertical_lines`` vorgegeben. Feste x-Koordinaten waeren nicht
  wiederverwendbar (Auftrag Abschnitt 14) -- das Dokument mischt Hoch- und
  Querformat.
* Die Bedeutung eines Codes steht in mehreren Formen NICHT als einzelne Zelle
  im Dokument, sondern entsteht aus Zeilen- und Spaltenkopf. Diese
  Zusammensetzung ist je Form explizit deklariert (``ColumnSpec.target``),
  nicht ad hoc zusammengeklebt.
* Mehrere Merkmale je Code (Werteart/Status/Richtung) wandern in eigene
  Spalten von ``CodeListEntry`` -- nicht in einen verketteten ``bedeutung``-
  String, der die Struktur zerstoeren wuerde.
* Kapitel 7 (Aenderungshistorie) enthaelt 14 OBIS-Kennzahlen und 4
  Messprodukt-Codes als Zitate frueherer Staende. Es ist ein expliziter
  Nicht-Datenbereich (``_CHANGELOG_HEADING``) und wird hart ausgeschlossen.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Sequence

import pdfplumber
from sqlalchemy.orm import Session

from . import models
from .regulatory_extraction import compute_file_hash, resolve_active_regulatory_version

# ---------------------------------------------------------------------------
# Konstanten der erwarteten Dokumentform
# ---------------------------------------------------------------------------

# Eine OBIS-Kennzahl in der Schreibweise des Dokuments, inklusive Platzhaltern.
# Wertegruppe B kennt b/bx, Wertegruppe E kennt e/ee/e1/e2 -- deshalb sind an
# beiden Stellen Buchstaben zugelassen. Die Platzhalter werden NICHT expandiert
# (Auftrag Abschnitt 8): ihr Wertebereich ist nicht einmal dokumentweit
# einheitlich (b = 0..65 fuer Strom, 0..64 fuer Gas).
_RE_OBIS = re.compile(r"^\d{1,2}-[0-9a-zA-Z]{1,3}:\d{1,3}\.\d{1,3}\.[0-9a-zA-Z]{1,3}$")
# Medien-Code aus Kapitel 5: drei Grossbuchstaben.
_RE_MEDIUM_CODE = re.compile(r"^[A-Z]{3}$")
# Schluesselwert aus Kapitel 2.2: fuehrende Ziffer, dann die Bedeutung.
_RE_KEY_VALUE = re.compile(r"^(\d{1,2})\s+(\S.*)$")
# Pruefidentifikator im Fliesstext der Nutzungseinschraenkungs-Spalte.
_RE_PI = re.compile(r"\b1\d{4}\b")

# "--" steht fuer "nicht anwendbar" und ist KEIN Code.
_NOT_APPLICABLE = {"--", "-", "—", "–"}

# Zeilen, die einen Tabellenkoerper beenden: Platzhalter-Legenden unter der
# Tabelle, Kapitelueberschriften, Seitenfuss.
_RE_LEGEND = re.compile(
    r"^\s*(Kanal|Tarif|bx|Stunden-?mittelwerte|Tages-?mittelwerte|Monats-?mittelwerte)\b.*[=…]"
)
_RE_CHAPTER = re.compile(r"^\s*\d(\.\d+)*\s+\S")
_RE_FOOTER = re.compile(r"^\s*Version:\s")
# Fussnotendefinition am Seitenfuss ("1 Nutzbar bis zum ...").
_RE_FOOTNOTE_DEF = re.compile(r"^\s*\d\s+[A-ZÄÖÜ]\S")

# Kapitel 7 -- expliziter Nicht-Datenbereich (Auftrag/Freigabe).
_CHANGELOG_HEADING = "Änderungshistorie"


# ---------------------------------------------------------------------------
# Deklarative Formspezifikation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ColumnSpec:
    """Eine logische Tabellenspalte.

    ``header`` ist der Text, ueber den die Spalte auf der Seite gefunden wird --
    der Spaltenindex ist im Dokument nicht stabil, die Kopfzelle schon.
    ``target`` benennt das Zielfeld in ``CodeListEntry``; ``"code"`` markiert
    eine Spalte, die selbst Codes traegt.
    """
    header: str
    target: str
    # Bei Code-Spalten: Wert, der zusaetzlich als Merkmal gespeichert wird
    # (z.B. Richtung "Ausspeisung" aus dem Unterspaltenkopf).
    facet_field: str = ""
    facet_value: str = ""


@dataclass(frozen=True)
class TableForm:
    """Eine im Dokument tatsaechlich vorgefundene Tabellenform."""
    key: str
    codelist_name: str
    chapter: str
    beschreibung: str
    columns: tuple[ColumnSpec, ...]
    pages: tuple[int, ...]
    nachrichtentyp: str | None = None
    # Kapitel 2.2: fuenf unabhaengige Listen nebeneinander statt einer
    # Zeilentabelle -- braucht einen eigenen Lesepfad.
    independent_columns: bool = False
    # Richtung aus einer Prosazeile ueber der Tabelle (Form 7).
    direction_from_prose: bool = False
    # Codes duerfen innerhalb einer Zelle durch Komma/Umbruch getrennt stehen.
    split_multi_codes: bool = True
    # Regex, dem ein gueltiger Code genuegen muss.
    code_pattern: re.Pattern[str] = _RE_OBIS


# ---------------------------------------------------------------------------
# Ergebnisstrukturen
# ---------------------------------------------------------------------------

@dataclass
class ObisEntry:
    """Ein extrahierter Codelisteneintrag, Rohwerte des Dokuments."""
    code: str
    bedeutung: str = ""
    werteart: str = ""
    status: str = ""
    richtung: str = ""
    hinweise: str = ""
    pruefidentifikatoren: str = ""
    source_page: int = 0
    form_key: str = ""
    codelist_name: str = ""
    # Index des Bezeichnungsblocks -- Eintraege desselben Blocks teilen sich
    # eine ueber mehrere Zeilen umbrochene Messgroesse (siehe _LabelBlock).
    label_block: int = -1


@dataclass
class SkippedRow:
    """Zeile, die keiner bestaetigten Form entspricht oder unklar ist."""
    page: int
    form_key: str
    reason: str
    raw: str


@dataclass
class ObisImportReport:
    document: str = ""
    file_hash: str = ""
    regulatory_version: str = ""
    codelists_created: int = 0
    entries_imported: int = 0
    forms_detected: list[str] = field(default_factory=list)
    forms_missing: list[str] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    reimported: bool = False
    entries_by_form: dict[str, int] = field(default_factory=dict)

    def format_report(self) -> str:
        out: list[str] = []
        out.append(f"Dokument:            {self.document}")
        out.append(f"SHA-256:             {self.file_hash}")
        out.append(f"RegulatoryVersion:   {self.regulatory_version}")
        out.append("")
        out.append(f"CodeLists angelegt:  {self.codelists_created}")
        out.append(f"CodeListEntries:     {self.entries_imported}")
        if self.reimported:
            out.append("Hinweis: voriger Stand derselben Datei wurde ersetzt (--reimport).")
        out.append("")
        out.append("Eintraege je Tabellenform:")
        for key in sorted(self.entries_by_form):
            out.append(f"  {key:<28} {self.entries_by_form[key]:>4}")
        if self.forms_missing:
            out.append("")
            out.append("NICHT erkannte Formen: " + ", ".join(self.forms_missing))
        if self.duplicates:
            out.append("")
            out.append(f"Sonderfaelle Duplikate ({len(self.duplicates)}):")
            for d in self.duplicates:
                out.append(f"  {d}")
        if self.skipped:
            out.append("")
            out.append(f"Uebersprungene Zeilen ({len(self.skipped)}):")
            for s in self.skipped[:40]:
                out.append(f"  S.{s.page:>2} [{s.form_key}] {s.reason}: {s.raw[:70]}")
            if len(self.skipped) > 40:
                out.append(f"  ... und {len(self.skipped) - 40} weitere")
        if self.errors:
            out.append("")
            out.append("FEHLER:")
            for e in self.errors:
                out.append(f"  {e}")
        return "\n".join(out)


# ---------------------------------------------------------------------------
# Die freigegebenen Tabellenformen (Issue #48, Freigabe)
#
# Zurueckgestellt und bewusst NICHT hier gelistet:
#   Form 4  Messprodukt-Code -> zulaessige OBIS (Kap. 3.3.1/3.3.3/3.3.5/3.3.6/4.6)
#           -- Zuordnungstabelle mit Bedingungen, keine Werteliste.
#   Form 5  Korrekturenergiemenge (Kap. 3.3.4) -- Merkmalskombination -> OBIS.
#   Form 10 Aenderungshistorie (Kap. 7) -- Dokumentationstabelle, Nicht-Datenbereich.
# ---------------------------------------------------------------------------

_PI_COL = ColumnSpec("Prüfidentifikator", "pruefidentifikatoren")

TABLE_FORMS: tuple[TableForm, ...] = (
    TableForm(
        key="form1-schluesselwerte",
        codelist_name="OBIS Schlüsselwerte elektrische Energie",
        chapter="2.2",
        beschreibung=(
            "Schlüsselwerte der OBIS-Wertegruppen für elektrische Energie. Vier "
            "unabhängige Wertelisten (Medium, Messgröße, Messart, Tarif) aus der "
            "nebeneinandergestellten Übersicht in Kapitel 2.2. Die Spalte "
            "Kanal (B) ist keine Codeliste, sondern eine Bereichsbeschreibung, "
            "und wird nicht importiert."
        ),
        columns=(
            ColumnSpec("Medium (A)", "code"),
            # Kanal (B) ist laut Befund KEINE Codeliste, sondern eine
            # Bereichsbeschreibung in Prosa ("Kanal 0-65", "Kanal 66 (nur bei
            # Angabe von Blindmehrarbeit ...)"). Die Spalte wird trotzdem
            # deklariert, weil sie als Bandgrenze gebraucht wird -- ohne sie
            # liefe ihr Text in die Bedeutung der Medium-Spalte.
            ColumnSpec("Kanal (B)", "ignore"),
            ColumnSpec("Messgröße (C)", "code"),
            ColumnSpec("Messart (D)", "code"),
            ColumnSpec("Tarif (E)", "code"),
        ),
        pages=(8,),
        independent_columns=True,
        code_pattern=re.compile(r"^\d{1,2}$"),
        split_multi_codes=False,
    ),
    TableForm(
        key="form2-obis-strom",
        codelist_name="OBIS-Kennzahlen elektrische Energie (verwendet)",
        chapter="3.1",
        beschreibung=(
            "In der Marktkommunikation verwendete OBIS-Kennzahlen für elektrische "
            "Energie. Die Richtung stammt aus dem Unterspaltenkopf der Spalte "
            "OBIS-Kennzahl."
        ),
        columns=(
            ColumnSpec("Messgröße", "bedeutung"),
            ColumnSpec("Werteart", "werteart"),
            ColumnSpec("Bezug (+)", "code", "richtung", "Bezug (+)"),
            ColumnSpec("Lieferung (-)", "code", "richtung", "Lieferung (-)"),
            ColumnSpec("Blind…", "code", "richtung", "Blind…"),
            _PI_COL,
        ),
        pages=(10, 11),
        nachrichtentyp="MSCONS",
    ),
    TableForm(
        key="form3-obis-strom-weitere",
        codelist_name="OBIS-Kennzahlen elektrische Energie (weitere definierte)",
        chapter="3.2",
        beschreibung=(
            "Weitere definierte OBIS-Kennzahlen zur Übertragung von Informationen "
            "zusätzlich zu Kapitel 3.1."
        ),
        columns=(
            ColumnSpec("Anwendung", "bedeutung"),
            ColumnSpec("Hinweise", "hinweise"),
            ColumnSpec("OBIS-Kennzahl", "code"),
            _PI_COL,
        ),
        pages=(12,),
        nachrichtentyp="MSCONS",
    ),
    TableForm(
        key="form6-obis-gas",
        codelist_name="OBIS-Kennzahlen thermische Energie (verwendet)",
        chapter="4.1",
        beschreibung=(
            "In der Marktkommunikation verwendete OBIS-Kennzahlen für thermische "
            "Energie, getrennt nach Ausspeisung und Einspeisung."
        ),
        columns=(
            ColumnSpec("Messgröße", "bedeutung"),
            ColumnSpec("Werteart", "werteart"),
            ColumnSpec("Status", "status"),
            ColumnSpec("Ausspeisung", "code", "richtung", "Ausspeisung"),
            ColumnSpec("Einspeisung", "code", "richtung", "Einspeisung"),
            _PI_COL,
        ),
        pages=(30, 31),
        nachrichtentyp="MSCONS",
    ),
    TableForm(
        key="form3-obis-gas-weitere",
        codelist_name="OBIS-Kennzahlen thermische Energie (weitere definierte)",
        chapter="4.2",
        beschreibung=(
            "Weitere definierte OBIS-Kennzahlen zur Übertragung von Informationen "
            "zusätzlich zu Kapitel 4.1."
        ),
        columns=(
            ColumnSpec("Anwendung", "bedeutung"),
            ColumnSpec("Hinweise", "hinweise"),
            ColumnSpec("OBIS-Kennzahl", "code"),
            _PI_COL,
        ),
        pages=(31,),
        nachrichtentyp="MSCONS",
    ),
    TableForm(
        key="form7-obis-gas-geraete",
        codelist_name="OBIS-Kennzahlen thermische Energie (gerätespezifisch)",
        chapter="4.3",
        beschreibung=(
            "Gerätespezifische OBIS-Kennzahlen (Zähler, Encoder, Umwerter). Die "
            "Richtung steht als Prosazeile über der Tabelle, die Werteart im "
            "Unterspaltenkopf, der Betriebsstatus in einer eigenen Spalte."
        ),
        columns=(
            ColumnSpec("Messgröße", "bedeutung"),
            ColumnSpec("Betriebsstatus", "status"),
            ColumnSpec("Zählerstand", "code", "werteart", "Einzelwerte Zählerstand"),
            ColumnSpec("Zählerstand#2", "code", "werteart", "Profilwerte Zählerstand"),
            ColumnSpec("Z.-St.-Differenz/h", "code", "werteart", "Profilwerte Z.-St.-Differenz/h"),
            _PI_COL,
        ),
        pages=(32, 33),
        nachrichtentyp="MSCONS",
        direction_from_prose=True,
    ),
    TableForm(
        key="form8-zustandsgroessen",
        codelist_name="OBIS-Kennzahlen für Zustandsgrößen",
        chapter="4.4",
        beschreibung="OBIS-Kennzahlen für Zustandsgrößen (thermische Energie).",
        columns=(
            ColumnSpec("Messgröße", "bedeutung"),
            ColumnSpec("OBIS-Kennzahl", "code"),
            _PI_COL,
        ),
        pages=(34,),
        nachrichtentyp="MSCONS",
    ),
    TableForm(
        key="form8-gasbeschaffenheit",
        codelist_name="OBIS-Kennzahlen zur Gasbeschaffenheitsanalyse",
        chapter="4.5",
        beschreibung=(
            "OBIS-Kennzahlen zur Gasbeschaffenheitsanalyse (Profilwerte, Mittelwerte)."
        ),
        columns=(
            ColumnSpec("Messgröße", "bedeutung"),
            ColumnSpec("OBIS-Kennzahl", "code"),
            _PI_COL,
        ),
        pages=(34, 35),
        nachrichtentyp="MSCONS",
    ),
    TableForm(
        key="form9-medien",
        codelist_name="Medien (Redispatch 2.0)",
        chapter="5",
        beschreibung=(
            "In der Marktkommunikation verwendete Medien im Rahmen der Prozesse "
            "des Redispatch 2.0."
        ),
        columns=(
            ColumnSpec("Medium", "bedeutung"),
            ColumnSpec("Code", "code"),
            _PI_COL,
        ),
        pages=(37,),
        nachrichtentyp="MSCONS",
        code_pattern=_RE_MEDIUM_CODE,
        split_multi_codes=False,
    ),
)


# ---------------------------------------------------------------------------
# Seitengeometrie: Zeilen, Kopfzeile, Tabellenkoerper
# ---------------------------------------------------------------------------

@dataclass
class _Line:
    top: float
    bottom: float
    words: list[dict]

    @property
    def text(self) -> str:
        return " ".join(w["text"] for w in sorted(self.words, key=lambda w: w["x0"]))


def _word_lines(page, tolerance: float = 2.5) -> list[_Line]:
    """Woerter zu visuellen Zeilen buendeln.

    pdfplumber liefert Woerter einzeln; ``extract_text`` wuerde die
    Spaltenzuordnung verlieren. Deshalb hier eigene Zeilenbildung ueber die
    ``top``-Koordinate -- dieselbe Technik wie in der AHB-Extraktion.
    """
    lines: list[_Line] = []
    words = page.extract_words(extra_attrs=["fontname", "size"])
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(w["top"] - lines[-1].top) <= tolerance:
            lines[-1].words.append(w)
            lines[-1].bottom = max(lines[-1].bottom, w["bottom"])
        else:
            lines.append(_Line(top=w["top"], bottom=w["bottom"], words=[w]))
    return lines


def _match_header_x0(words: Sequence[dict], header: str, occurrence: int = 1) -> float | None:
    """x0 der Kopfzelle ``header`` finden.

    Der Spaltenindex ist im Dokument nicht stabil (dieselbe Tabelle hat je nach
    Seite 8 bis 17 Fragmentspalten), die Kopfzelle schon. Mehrwortige Koepfe
    werden als zusammenhaengende Wortfolge gesucht.
    """
    tokens = header.split()
    ordered = sorted(words, key=lambda w: (w["top"], w["x0"]))
    hits = 0
    for i in range(len(ordered)):
        if all(
            i + k < len(ordered) and ordered[i + k]["text"] == tokens[k]
            for k in range(len(tokens))
        ):
            hits += 1
            if hits == occurrence:
                return ordered[i]["x0"]
    return None


def _locate_columns(form: TableForm, lines: Sequence[_Line], start: int) -> tuple[list[float], int] | None:
    """Spalten-x0 aus der Kopfzeile herleiten.

    Rueckgabe: (x0 je Spalte in Spaltenreihenfolge, Index der letzten Kopfzeile).
    ``None``, wenn nicht alle erwarteten Kopfzellen gefunden werden -- das ist
    die Formpruefung (Auftrag Abschnitt 6): was nicht passt, wird nicht gelesen.
    """
    # Kopfband: die Kopfzeile plus bis zu vier Folgezeilen (Unterspaltenkoepfe,
    # umbrochene Kopftexte wie "Nutzungseinschränkung in der MSCONS").
    for span in range(1, 6):
        band = [w for ln in lines[start:start + span] for w in ln.words]
        seen: dict[str, int] = {}
        xs: list[float] = []
        ok = True
        for col in form.columns:
            base = col.header.split("#")[0]
            seen[base] = seen.get(base, 0) + 1
            x0 = _match_header_x0(band, base, seen[base])
            if x0 is None:
                ok = False
                break
            xs.append(x0)
        if ok and xs == sorted(xs):
            # Spalten muessen streng von links nach rechts liegen -- sonst wurde
            # eine Kopfzelle im Datenbereich getroffen.
            return xs, start + span - 1
    return None


def _body_end(lines: Sequence[_Line], first_body: int) -> int:
    """Erste Zeile NACH dem Tabellenkoerper finden.

    Beendet wird der Koerper durch Platzhalter-Legende, Kapitelueberschrift,
    Fussnotendefinition oder Seitenfuss -- alles Zeilen, die keine Tabellen-
    daten mehr sind.
    """
    for i in range(first_body, len(lines)):
        line = lines[i]
        t = line.text.strip()
        first = min(line.words, key=lambda w: w["x0"])
        big = float(first.get("size") or 0) >= _HEADING_MIN_SIZE
        if _RE_LEGEND.match(t) or _RE_FOOTER.match(t):
            return i
        # Fussnotendefinition am Seitenfuss ("1 Nutzbar bis zum ..."). Sie ist
        # in Grad 12 gesetzt, Tabellendaten in Grad 9 -- ohne diese Bedingung
        # wuerde in Kapitel 2.2 schon die erste Datenzeile ("1 Elektrizität")
        # als Fussnote gelesen und der Tabellenkoerper waere leer.
        if _RE_FOOTNOTE_DEF.match(t) and big:
            return i
        # Naechste Kapitelueberschrift. Die Pruefung MUSS dieselbe Fettschrift-
        # Bedingung nutzen wie _scan_chapters: in Kapitel 2.2 beginnt jede
        # Datenzeile mit einer Ziffer ("1 Elektrizität", "8 Zeitintegral 1"),
        # ein reiner Textvergleich wuerde den Tabellenkoerper sofort beenden.
        if _RE_CHAPTER.match(t) and big and "Bold" in (first.get("fontname") or ""):
            return i
    return len(lines)


def _split_codes(raw: str, form: TableForm) -> list[str]:
    """Zellinhalt in einzelne Codes zerlegen.

    Eine Zelle kann mehrere Codes tragen ("1-b:1.8.e, 1-b:1.8.63") oder
    umbrochen sein. "--" bedeutet 'nicht anwendbar' und liefert keinen Code.
    """
    if not raw:
        return []
    parts = re.split(r"[,\n]", raw) if form.split_multi_codes else [raw]
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if not p or p in _NOT_APPLICABLE:
            continue
        if form.code_pattern.match(p):
            out.append(p)
    return out


def _clean(cell: str | None) -> str:
    """Zellwert normalisieren -- nur Layoutartefakte, kein inhaltlicher Eingriff.

    Zurueckgebaut wird ausschliesslich die Silbentrennung am Zellumbruch
    ("Lieferbe-\nginn" -> "Lieferbeginn"). Die Bedingung "Kleinbuchstabe nach
    dem Trennstrich" schuetzt echte Bindestriche: "VDE-AR-N\n4400" und
    "Z.-St.-Differenz/h" bleiben unangetastet.
    """
    if not cell:
        return ""
    cell = re.sub(r"-\n(?=[a-zäöüß])", "", cell)
    return re.sub(r"\s+", " ", cell.replace("\n", " ")).strip()


# ---------------------------------------------------------------------------
# Extraktion je Tabellenform
# ---------------------------------------------------------------------------

def _extract_independent_columns(
    page, form: TableForm, pageno: int, skipped: list[SkippedRow],
    top_min: float = 0.0, top_max: float = 10 ** 6,
) -> list[ObisEntry]:
    """Kapitel 2.2: fuenf unabhaengige Wertelisten nebeneinander.

    Keine Zeilentabelle -- die Spalten haben eigene, gegeneinander versetzte
    Zeilenpositionen (Kanal-Spalte auf top=170, Messgroesse-Spalte auf top=171).
    Deshalb wird jede Spalte fuer sich von oben nach unten gelesen.
    """
    lines = [ln for ln in _word_lines(page) if top_min <= ln.top <= top_max]
    located = None
    for i, ln in enumerate(lines):
        located = _locate_columns(form, lines, i)
        if located:
            header_end = located[1]
            break
    if not located:
        return []
    xs, header_end = located
    body = lines[header_end + 1:_body_end(lines, header_end + 1)]

    entries: list[ObisEntry] = []
    for ci, col in enumerate(form.columns):
        if col.target != "code":
            continue
        left = xs[ci] - 5
        right = (xs[ci + 1] - 5) if ci + 1 < len(xs) else page.width
        # Jede Spalte ist eine eigene Codeliste; ihr Name ergibt sich aus der
        # Kopfzelle, damit die vier Listen unterscheidbar bleiben.
        listname = f"{form.codelist_name} – {col.header}"
        for ln in body:
            cell = " ".join(
                w["text"] for w in sorted(ln.words, key=lambda w: w["x0"])
                if left <= w["x0"] < right
            ).strip()
            if not cell:
                continue
            m = _RE_KEY_VALUE.match(cell)
            if not m:
                # "…" (Auslassung) und aehnliche Zeilen sind keine Codes.
                skipped.append(SkippedRow(pageno, form.key, "kein Code/Bedeutung-Paar", cell))
                continue
            entries.append(ObisEntry(
                code=m.group(1),
                bedeutung=m.group(2).strip(),
                source_page=pageno,
                form_key=form.key,
                codelist_name=listname,
            ))
    return entries


def _prose_direction(lines: Sequence[_Line], header_idx: int) -> str:
    """Richtung aus der Prosazeile ueber der Tabelle (Form 7).

    Kapitel 4.3 enthaelt zwei Tabellen mit identischem Spaltenkopf; sie sind
    ausschliesslich durch die Zeile "OBIS-Kennzahlen für Ausspeisung" bzw.
    "... für Einspeisung" darueber unterscheidbar.
    """
    for i in range(header_idx, -1, -1):
        t = lines[i].text.strip()
        m = re.match(r"^OBIS-Kennzahlen für (Aus|Ein)speisung$", t)
        if m:
            return f"{m.group(1)}speisung"
    return ""


def _rows_from_table(page, form: TableForm, xs: Sequence[float], top: float, bottom: float):
    """Tabellenkoerper mit EXPLIZITEN Spaltengrenzen auslesen.

    Ohne Vorgabe zerlegt pdfplumber dieselbe Tabelle in bis zu 17
    Fragmentspalten. Mit den aus der Kopfzeile hergeleiteten Grenzen entsteht
    genau das logische Raster des Dokuments.
    """
    # Rechte Tabellenkante aus den Rahmenlinien herleiten, NICHT page.width
    # verwenden: pdfplumber verwirft eine Spalte, deren rechte Begrenzung keine
    # Linienkreuzung hat -- die letzte Spalte (Prüfidentifikator) fiele sonst weg.
    # Rechte Rahmenlinie der Tabelle: die aeusserste VERTIKALE Kante rechts der
    # letzten Spalte. Horizontale Kanten taugen dafuer nicht -- pdfplumber
    # liefert dort vereinzelt Werte jenseits der Seitenbreite (S.10: x1=1189
    # bei einer Seitenbreite von 595).
    verticals = [
        e["x0"] for e in page.edges
        if e["orientation"] == "v"
        and e["top"] < bottom and e["bottom"] > top
        and xs[-1] < e["x0"] <= page.width
    ]
    if verticals:
        right = max(verticals) + 2
    else:
        words = [w["x1"] for w in page.extract_words() if top <= w["top"] <= bottom]
        right = (max(words) + 8) if words else page.width
    right = min(right, page.width)
    bounds = [xs[0] - 5] + [x - 5 for x in xs[1:]] + [right]
    crop = page.crop((max(0, xs[0] - 8), top, right, bottom))
    table = crop.extract_table({
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": bounds,
        "horizontal_strategy": "lines",
        "intersection_tolerance": 6,
    })
    return table or []


def _extract_row_table(
    page, form: TableForm, pageno: int, skipped: list[SkippedRow], block_offset: int,
    top_min: float = 0.0, top_max: float = 10 ** 6, direction_carry: str = "",
    label_carry: str = "",
) -> tuple[list[ObisEntry], int, str, str]:
    """Zeilentabelle einer Form auf einer Seite lesen.

    Ein Eintrag wird durch eine Zeile mit Code ANGESTOSSEN; Folgezeilen ohne
    Code haengen sich an (umbrochene Prüfidentifikator-Texte). Zeilen VOR dem
    ersten Code gehoeren ebenfalls zum ersten Eintrag -- im Dokument steht die
    verbundene Zelle teils optisch mittig in ihrem Codeblock (Kapitel 5:
    "Ausfallarbeit AUA" sitzt zwischen 13022 und 13023).
    """
    lines = [ln for ln in _word_lines(page) if top_min <= ln.top <= top_max]
    entries: list[ObisEntry] = []
    blocks = block_offset
    pi_index = next(
        (i for i, c in enumerate(form.columns) if c.target == "pruefidentifikatoren"),
        None,
    )
    code_cols = [i for i, c in enumerate(form.columns) if c.target == "code"]

    idx = 0
    while idx < len(lines):
        located = _locate_columns(form, lines, idx)
        if not located:
            idx += 1
            continue
        xs, header_end = located
        first_body = header_end + 1
        end = _body_end(lines, first_body)
        if first_body >= end:
            idx = header_end + 1
            continue
        top = lines[header_end].bottom + 1
        bottom = lines[end].top - 1 if end < len(lines) else page.height
        if form.direction_from_prose:
            # Die Richtung steht als Prosazeile ueber der Tabelle. Laeuft die
            # Tabelle ueber einen Seitenumbruch (Kap. 4.3: S.31->32->33), fehlt
            # die Zeile auf der Folgeseite -- dann gilt die zuletzt gesehene.
            found = _prose_direction(lines, idx)
            if found:
                direction_carry = found
            richtung_prose = direction_carry
        else:
            richtung_prose = ""

        running: dict[str, str] = {}
        # Laeuft die Tabelle ueber einen Seitenumbruch, steht die Messgroesse
        # nur auf der ersten Seite (Kap. 4.3: "Masse [kg]" auf S.32, die Zeile
        # "gesamt" dazu auf S.33). Das Label wird deshalb mitgefuehrt.
        label = label_carry
        pending: list[ObisEntry] = []   # Eintraege des laufenden Bezeichnungsblocks
        current: list[ObisEntry] = []   # zuletzt erzeugte Eintraege (Anhaengeziel)
        leading: list[str] = []         # PI-Werte vor dem ersten Code der Tabelle

        def flush_block() -> None:
            nonlocal pending
            for e in pending:
                # Das ueber mehrere Zeilen umbrochene Label gilt fuer ALLE
                # Eintraege seines Blocks, nicht nur fuer die erste Zeile.
                e.bedeutung = label
            entries.extend(pending)
            pending = []

        for row in _rows_from_table(page, form, xs, top, bottom):
            cells = [_clean(c) for c in row]
            if len(cells) < len(form.columns):
                cells += [""] * (len(form.columns) - len(cells))

            codes_here: list[tuple[int, str]] = []
            malformed = False
            for ci in code_cols:
                found_codes = _split_codes(cells[ci], form)
                for code in found_codes:
                    codes_here.append((ci, code))
                # Zelle traegt etwas, das kein gueltiger Code ist und auch kein
                # "nicht anwendbar": nicht importieren, sondern ausweisen
                # (Auftrag Abschnitt 12). Betrifft im Stand 2.5c die Zelle
                # "1-1:2:29.0" auf S.12 -- ein Schreibfehler des Quelldokuments
                # (Doppelpunkt statt Punkt), der NICHT stillschweigend korrigiert
                # wird.
                raw = cells[ci].strip()
                if raw and not found_codes and raw not in _NOT_APPLICABLE:
                    malformed = True
                    skipped.append(SkippedRow(
                        pageno, form.key,
                        "Code nicht in erwarteter Schreibweise", raw,
                    ))

            # Merkmalsspalten fortschreiben (verbundene Zellen im Dokument)
            for ci, col in enumerate(form.columns):
                if col.target in ("code", "pruefidentifikatoren") or not cells[ci]:
                    continue
                if col.target == "bedeutung":
                    frag = cells[ci]
                    # Eine neue Bezeichnung beginnt NUR, wenn die Zeile auch
                    # einen Code traegt UND der Text gross/mit Ziffer anfaengt.
                    # Beide Bedingungen sind noetig:
                    #   * "temperaturkompensiert" (Kap. 4.1) steht in einer Zeile
                    #     MIT Code, ist aber klein geschrieben -> Fortsetzung.
                    #   * "Grundpreis / Arbeitspreis" (Kap. 3.2) ist gross
                    #     geschrieben, steht aber in einer Zeile OHNE Code
                    #     -> Fortsetzung.
                    if frag[:1].islower() or not codes_here:
                        if label.endswith("-"):
                            # Silbentrennung ueber die Zeilengrenze:
                            # "Lieferbe-" + "ginn" -> "Lieferbeginn".
                            label = label[:-1] + frag
                        else:
                            label = f"{label} {frag}".strip()
                    else:
                        flush_block()
                        blocks += 1
                        label = frag
                elif running.get(col.target, "").endswith("-"):
                    # Silbentrennung ueber die Zeilengrenze auch in den
                    # Merkmalsspalten ("größter Monatseinspeise-" + "brennwert").
                    # Nur bei einem offenen Trennstrich -- ein reiner
                    # Kleinbuchstaben-Test waere hier falsch, weil der
                    # Betriebsstatus in Kapitel 4.3 regulaer klein geschrieben
                    # ist ("ungestört", "gestört", "gesamt").
                    running[col.target] = running[col.target][:-1] + cells[ci]
                    # Der Eintrag der Vorzeile wurde bereits mit dem
                    # abgeschnittenen Wert angelegt -- vervollstaendigen.
                    for prev in current:
                        setattr(prev, col.target, running[col.target])
                else:
                    running[col.target] = cells[ci]

            pi_cell = cells[pi_index] if pi_index is not None else ""

            if not codes_here:
                if malformed:
                    # Die Zeile gehoert zu einem verworfenen Code -- ihre
                    # Prüfidentifikatoren duerfen nicht an den vorigen Eintrag
                    # wandern.
                    continue
                # Reine Fortsetzungszeile: PI-Text an den laufenden Eintrag haengen,
                # oder puffern, solange noch kein Eintrag existiert.
                if pi_cell:
                    if current:
                        for e in current:
                            e.pruefidentifikatoren = f"{e.pruefidentifikatoren} {pi_cell}".strip()
                    else:
                        leading.append(pi_cell)
                elif any(cells) and not any(
                    cells[ci] for ci, c in enumerate(form.columns) if c.target != "code"
                ):
                    skipped.append(SkippedRow(
                        pageno, form.key, "Zeile ohne verwertbaren Code", " | ".join(cells)
                    ))
                continue

            current = []
            for ci, code in codes_here:
                col = form.columns[ci]
                e = ObisEntry(
                    code=code,
                    werteart=running.get("werteart", ""),
                    status=running.get("status", ""),
                    richtung=richtung_prose,
                    hinweise=running.get("hinweise", ""),
                    pruefidentifikatoren=pi_cell,
                    source_page=pageno,
                    form_key=form.key,
                    codelist_name=form.codelist_name,
                    label_block=blocks,
                )
                if col.facet_field:
                    setattr(e, col.facet_field, col.facet_value)
                current.append(e)

            if leading:
                for e in current:
                    e.pruefidentifikatoren = " ".join([*leading, e.pruefidentifikatoren]).strip()
                leading = []
            pending.extend(current)

        flush_block()
        label_carry = label
        idx = end

    if form.direction_from_prose and not entries:
        # Seite ohne Tabellenkoerper: die Richtungszeile kann trotzdem hier
        # stehen und gilt fuer die Tabelle auf der Folgeseite. In Kapitel 4.3
        # steht "OBIS-Kennzahlen für Ausspeisung" als letzte Zeile auf S.31,
        # die zugehoerige Tabelle beginnt erst auf S.32.
        found = _prose_direction(lines, len(lines) - 1)
        if found:
            direction_carry = found
    return entries, blocks, direction_carry, label_carry


# ---------------------------------------------------------------------------
# Dokumentweite Steuerung
# ---------------------------------------------------------------------------

@dataclass
class _Chapter:
    number: str
    title: str
    start_page: int
    start_top: float
    end_page: int = 0
    end_top: float = 0.0


# Kapitelueberschriften sind im Dokument fett gesetzt und beginnen am linken
# Satzspiegelrand. Beides zusammen trennt sie zuverlaessig von
#   * Datenzeilen, die mit einer Zahl beginnen ("9991 00000 004 4", "13009 und
#     wenn BGM ...", "1 Elektrizität") -- Schriftgrad 9, nicht fett, eingerueckt,
#   * Inhaltsverzeichniszeilen -- gleicher Grad, aber NICHT fett und eingerueckt.
# Die Einrueckung wechselt mit der Gliederungstiefe (Kapitel 4.1 bei x0=69,5,
# 4.4/4.5 bei x0=85,1), traegt also nichts zur Unterscheidung bei. Sie grenzt
# nur den linken Satzspiegel gegen Tabelleninhalt ab; die eigentliche
# Unterscheidung leisten Fettschrift und Schriftgrad.
_HEADING_MAX_X0 = 110.0
_HEADING_MIN_SIZE = 11.0


def _scan_chapters(pdf) -> list[_Chapter]:
    """Kapitelgliederung aus den Ueberschriftenzeilen lesen.

    Die Formen werden ueber ihre KAPITELNUMMER lokalisiert, nicht ueber feste
    Seitenzahlen (Auftrag Abschnitt 14): eine spaetere Fassung darf Seiten
    verschieben, ohne den Parser zu brechen. Die Grenzen werden zeilengenau
    gefuehrt, weil zwei Kapitel auf derselben Seite beginnen koennen (4.4 und
    4.5 auf S.34).
    """
    chapters: list[_Chapter] = []
    for pageno, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        # Inhaltsverzeichnis ueberspringen: dort sind die Eintraege ebenfalls
        # fett und beginnen am linken Rand, sie sind also nicht am Schriftbild
        # von echten Ueberschriften zu unterscheiden. Merkmal der Seite sind die
        # Fuehrungspunkte -- ohne diesen Filter faende der Scan das Kapitel 7
        # bereits auf S.4 und wuerde das ganze Dokument abschneiden.
        if sum(1 for ln in text.split("\n") if "...." in ln) >= 3:
            continue
        for line in _word_lines(page):
            words = sorted(line.words, key=lambda w: w["x0"])
            first = words[0]
            if first["x0"] > _HEADING_MAX_X0:
                continue
            if "Bold" not in (first.get("fontname") or ""):
                continue
            if float(first.get("size") or 0) < _HEADING_MIN_SIZE:
                continue
            m = re.match(r"^\d+(?:\.\d+)*$", first["text"])
            if not m:
                continue
            title = " ".join(w["text"] for w in words[1:]).strip()
            if len(title) < 4:
                continue
            chapters.append(_Chapter(
                number=first["text"], title=title,
                start_page=pageno, start_top=line.top,
            ))
    for cur, nxt in zip(chapters, chapters[1:]):
        cur.end_page, cur.end_top = nxt.start_page, nxt.start_top
    if chapters:
        chapters[-1].end_page = len(pdf.pages)
        chapters[-1].end_top = 10 ** 6
    return chapters


def changelog_start_page(chapters: Sequence[_Chapter]) -> int | None:
    """Erste Seite der Aenderungshistorie -- expliziter Nicht-Datenbereich.

    Kapitel 7 zitiert 14 OBIS-Kennzahlen und 4 Messprodukt-Codes aus frueheren
    Staenden, teils solche, die inzwischen GELOESCHT sind. Eine dokumentweite
    Mustersuche wuerde sie als gueltige Codes einsammeln. Deshalb ist die Grenze
    hier hart gezogen und wird im Regressionstest dauerhaft abgesichert.
    """
    for ch in chapters:
        if ch.title.startswith(_CHANGELOG_HEADING):
            return ch.start_page
    return None


def _chapter_region(
    chapters: Sequence[_Chapter], number: str
) -> list[tuple[int, float, float]] | None:
    """Seiten eines Kapitels als (Seite, top_min, top_max).

    Zeilengenau, damit zwei Kapitel auf derselben Seite (4.4/4.5 auf S.34)
    nicht ineinanderlaufen -- sonst greift die Formpruefung beider Formen auf
    dieselben Zeilen zu, weil ihre Spaltenkoepfe identisch sind.
    """
    for ch in chapters:
        if ch.number != number:
            continue
        out: list[tuple[int, float, float]] = []
        for pageno in range(ch.start_page, ch.end_page + 1):
            lo = ch.start_top if pageno == ch.start_page else 0.0
            hi = ch.end_top if pageno == ch.end_page else 10 ** 6
            if hi > lo:
                out.append((pageno, lo, hi))
        return out
    return None


def extract_obis_codelists(
    pdf_path: str,
) -> tuple[list[ObisEntry], list[SkippedRow], list[str]]:
    """Alle freigegebenen Tabellenformen aus dem Dokument lesen."""
    entries: list[ObisEntry] = []
    skipped: list[SkippedRow] = []
    missing: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        chapters = _scan_chapters(pdf)
        cutoff = changelog_start_page(chapters) or (len(pdf.pages) + 1)
        blocks = 0
        for form in TABLE_FORMS:
            direction = ""
            label = ""
            region = _chapter_region(chapters, form.chapter)
            if not region:
                missing.append(f"{form.key} (Kapitel {form.chapter} nicht gefunden)")
                continue
            found = 0
            for pageno, lo, hi in region:
                if pageno >= cutoff:
                    break  # Aenderungshistorie: expliziter Nicht-Datenbereich
                page = pdf.pages[pageno - 1]
                if form.independent_columns:
                    got = _extract_independent_columns(page, form, pageno, skipped, lo, hi)
                else:
                    got, blocks, direction, label = _extract_row_table(
                        page, form, pageno, skipped, blocks, lo, hi, direction, label
                    )
                entries.extend(got)
                found += len(got)
            if not found:
                pages = ", ".join(str(p) for p, _, _ in region)
                missing.append(f"{form.key} (Formprüfung auf S.{pages} ohne Treffer)")
    return entries, skipped, missing


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


def import_obis_codelists(
    db: Session,
    pdf_path: str,
    regulatory_version_id: int,
    reimport: bool = False,
) -> ObisImportReport:
    """Codelisten aus der OBIS-Codeliste in CodeList/CodeListEntry uebernehmen."""
    report = ObisImportReport(document=pdf_path)
    report.file_hash = compute_file_hash(pdf_path)

    version = db.get(models.RegulatoryVersion, regulatory_version_id)
    if version is None:
        report.errors.append(f"RegulatoryVersion {regulatory_version_id} existiert nicht.")
        return report
    report.regulatory_version = f"[{version.id}] {version.name}"

    if _existing_import(db, regulatory_version_id, report.file_hash):
        if not reimport:
            # Idempotenz: derselbe Dateihash ist bereits importiert -- nichts tun.
            report.errors.append(
                "Diese Datei ist fuer diese RegulatoryVersion bereits importiert "
                "(gleicher SHA-256). Mit --reimport erzwingen."
            )
            return report
        _delete_previous_import(db, regulatory_version_id, report.file_hash)
        report.reimported = True

    entries, skipped, missing = extract_obis_codelists(pdf_path)
    report.skipped = skipped
    report.forms_missing = missing

    # gueltig_ab aus der RegulatoryVersion; das Dokument nennt kein Datum je Code
    # (Auftrag Abschnitt 9). gueltig_bis bleibt NULL = weiterhin gueltig.
    gueltig_ab: date | None = version.valid_from.date() if version.valid_from else None

    by_list: dict[str, list[ObisEntry]] = {}
    for e in entries:
        by_list.setdefault(e.codelist_name, []).append(e)

    form_by_name = {}
    for form in TABLE_FORMS:
        form_by_name.setdefault(form.codelist_name, form)
        if form.independent_columns:
            for col in form.columns:
                form_by_name[f"{form.codelist_name} – {col.header}"] = form

    for listname, items in by_list.items():
        form = form_by_name.get(listname)
        codelist = models.CodeList(
            regulatory_version_id=regulatory_version_id,
            name=listname,
            nachrichtentyp=form.nachrichtentyp if form else None,
            beschreibung=form.beschreibung if form else None,
            quelle_dokument=pdf_path,
            quelle_hash=report.file_hash,
            quelle_kapitel=form.chapter if form else None,
        )
        db.add(codelist)
        db.flush()
        report.codelists_created += 1

        # Doppelter Code innerhalb derselben CodeList: nicht ueberschreiben,
        # nicht eigenstaendig entscheiden -- als Sonderfall ausweisen
        # (Auftrag Abschnitt 12).
        seen: dict[tuple[str, str, str, str], ObisEntry] = {}
        for e in items:
            key = (e.code, e.richtung, e.werteart, e.status)
            if key in seen:
                prev = seen[key]
                if prev.bedeutung != e.bedeutung:
                    report.duplicates.append(
                        f"{listname}: Code {e.code!r} doppelt mit abweichender "
                        f"Bedeutung ({prev.bedeutung!r} S.{prev.source_page} vs "
                        f"{e.bedeutung!r} S.{e.source_page}) -- nicht importiert"
                    )
                    continue
                report.duplicates.append(
                    f"{listname}: Code {e.code!r} identisch doppelt "
                    f"(S.{prev.source_page}/S.{e.source_page}) -- einmal importiert"
                )
                continue
            seen[key] = e
            if not e.bedeutung:
                report.skipped.append(SkippedRow(
                    e.source_page, e.form_key, "Code ohne Bedeutung", e.code
                ))
                continue
            db.add(models.CodeListEntry(
                codelist_id=codelist.id,
                code=e.code,
                bedeutung=e.bedeutung,
                werteart=e.werteart or None,
                status=e.status or None,
                richtung=e.richtung or None,
                hinweise=e.hinweise or None,
                pruefidentifikatoren=e.pruefidentifikatoren or None,
                gueltig_ab=gueltig_ab,
                gueltig_bis=None,
                quelle_seite=e.source_page,
            ))
            report.entries_imported += 1
            report.entries_by_form[e.form_key] = report.entries_by_form.get(e.form_key, 0) + 1

    db.commit()
    return report
