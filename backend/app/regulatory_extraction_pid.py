"""Deterministische Extraktion aus der "Anwendungsuebersicht der Pruefidentifikatoren"
3.3 (Issue #54, Freigabe Scoping A).

Fuenfter Baustein der Regulatory-Extraktionspipeline neben AHB
(``regulatory_extraction.py``), MIG (``regulatory_extraction_mig.py``), der
Codeliste der OBIS-Kennzahlen (``regulatory_extraction_obis.py``) und den
EBD-Codelisten (``regulatory_extraction_ebd.py``). Gleiche Architektur, bewusst
OHNE LLM:

    Dokument -> Formpruefung -> deterministische Extraktion -> Wissensbasis

SCOPE DIESES MODULS (Freigabe zu Issue #54)
-------------------------------------------
Freigegeben ist ausschliesslich **Scoping A: PID -> ProcessIdentifier, sonst
nichts.** Uebernommen wird aus Tabelle 1 das Paar Pruefidentifikator ->
Beschreibung des Anwendungsfalls. Alles andere -- Prozessschritt,
Reaktionsbeziehung, Tupel-Uebersicht, Zuordnungslogik, Erweiterte Zuordnung,
Objekteigenschaften, Uebertragungsweg, API-Webservices -- wird **gelesen,
gezaehlt und im Report ausgewiesen**, aber nicht modelliert. Dafuer braucht es
neue Modelle, und die darf dieser Schritt nach Auftrag Abschnitt 10 nicht
eigenstaendig einfuehren.

Daraus folgt die harte Regel der Freigabe: **kein PID-Feld darf stillschweigend
verloren gehen.** ``PidRow`` haelt deshalb alle 21 Spalten im Rohwert, und
``PidImportReport`` fuehrt eine Verlustbilanz je Spalte -- was gelesen wurde,
was uebernommen wurde und was fuer eine spaetere Modellierung vorgemerkt ist.

BEFUNDE, DIE DEN AUFBAU BESTIMMEN (Issue #54, empirisch ueber alle 82 Seiten)
-----------------------------------------------------------------------------
* Das Dokument nennt seine Gliederung selbst: die Kopfzeile jeder Datenseite
  lautet "Anwendungsuebersicht der <Tabellenkonzept>". Das ist der Anker fuer
  die Abschnittstrennung -- verlaesslicher als Seitenbereiche, die sich mit
  jeder Version verschieben.
* Es gibt genau fuenf Tabellenkonzepte, uebereinstimmend mit dem eigenen
  Inhaltsverzeichnis auf S. 2. Die aus Version 3.1 vermuteten Einzeltabellen
  "API-Webservice zu Prozessschritt" und "Antwort auf Pruefidentifikator"
  existieren NICHT: beides steckt in Tabelle 1 (Spalte "Reaktion auf
  Pruefidentifikator" bzw. Zeilen mit Uebertragungsweg "API" ohne PI).
* ``extract_tables()`` liefert hier -- anders als bei MIG und AHB -- saubere
  Zellen. Alle 1370 Datenzeilen der Tabelle 1 haben exakt 21 Zellen,
  mehrzeilige Inhalte kommen als ``\\n`` INNERHALB der Zelle an, und keine
  Zeile laeuft ueber einen Seitenumbruch. Das Zusammenfuehren von
  Fortsetzungszeilen aus Prompt 1 entfaellt vollstaendig.
* Der Zeilenumbruch innerhalb einer Zelle zerreisst dafuer Woerter ohne
  Trennzeichen ("Marktraumumstell\\nung", "Netzbetreiberwech\\nsel"). Es gibt
  keine deterministische Regel, die "Prozesse zum\\nInformationsaustau\\nsch"
  richtig zusammensetzt UND echte Wortgrenzen erhaelt. Deshalb wird der Rohwert
  gespeichert (Auftrag Abschnitt 8) und nur fuer den Vergleich normalisiert.
* Die Kopfzeile der Tabelle 1 ist auf allen 71 Seiten byte-identisch. Drei
  Kopfzellen sind im PDF um 90 Grad gedreht und kommen als Zeichensalat an
  ("m\\no\\nrtS\\ne\\ntra\\np\\nS" = "Sparte Strom"). Sie werden als
  Fingerabdruck genommen, wie sie sind -- nicht entziffert.
* Die Tabelle ist WEDER nach PI-Nummer NOCH nach laufender Nummer sortiert.
  Die "Lfd. Nr." ist eine duenn besetzte, duplikatfreie Quell-ID
  (1..38890, davon 1362 vergeben); acht vollstaendige Datenzeilen haben gar
  keine. Sie taugt deshalb nicht als Schluessel, wohl aber als Provenienz.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator, Sequence

import pdfplumber
from sqlalchemy import null
from sqlalchemy.orm import Session

from . import models
from .regulatory_extraction import compute_file_hash, resolve_active_regulatory_version

# ---------------------------------------------------------------------------
# Konstanten der erwarteten Dokumentform
# ---------------------------------------------------------------------------

# Kopfzeile jeder Datenseite. Der Teil hinter "Anwendungsuebersicht der " nennt
# das Tabellenkonzept. Auf S. 7-77 steht dort zusaetzlich das Wort
# "Pruefidentifikatoren" aus dem Dokumenttitel, deshalb der lockere Anker.
_PAGE_HEADING_RE = re.compile(r"^Anwendungsübersicht der\s+(.+?)\s*$")

# Spaltenbeschriftungen der Tabelle 1, in Dokumentreihenfolge. Sie sind KEIN
# Formmerkmal -- das ist der Fingerabdruck unten -- sondern dienen dem Report
# und der Verlustbilanz.
MAIN_COLUMNS: tuple[str, ...] = (
    "Lfd. Nr.",
    "AHB",
    "Beschreibung des Anwendungsfalls aus dem AHB (EDIFACT) / API-Webservice (API)",
    "Prüfidentifikator",
    "Reaktion auf Prüfidentifikator",
    "Prozessbeschreibung",
    "Prozessschritt aus Kapitel",
    "Bezeichnung aus Sequenzdiagramm",
    "Prozessschritt aus Sequenzdiagramm",
    "Aktion",
    "Kommunikation von",
    "Kommunikation an",
    "Zuordnung zu einem Objekt",
    "Zuordnung zu einem Geschäftsvorfall",
    "Erweiterte Zuordnung",
    "Objekteigenschaft",
    "Sparte Strom",
    "Sparte Gas",
    "Übertragungsweg",
    "API-Kennung",
    "Fußnote",
)

# Spaltenindizes, die dieser Schritt tatsaechlich in die Wissensbasis uebernimmt.
COL_LFD_NR = 0
COL_AHB = 1
COL_DESCRIPTION = 2
COL_PI = 3
COL_REACTION = 4
COL_ASSIGN_OBJECT = 12
COL_ASSIGN_TRANSACTION = 13
COL_EXTENDED = 14
COL_OBJECT_PROPERTY = 15
COL_TRANSPORT = 18

# Diese Spalten wandern ins Modell (Freigabe Scoping A). Die AHB-Spalte liefert
# den EDIFACT-Nachrichtentyp -- Atlas braucht alle Formate, nicht nur UTILMD.
_MODELLED_COLUMNS = frozenset({COL_PI, COL_DESCRIPTION, COL_AHB})


@dataclass(frozen=True)
class TableConcept:
    """Ein erwartetes Tabellenkonzept des Dokuments.

    ``header`` ist ein Fingerabdruck der Kopfzeile: alle Zellen aneinander, je
    Zelle ohne Zeilenumbrueche. Er wird NICHT entziffert oder normalisiert --
    weicht er ab, gilt das Konzept als nicht erkannt (Auftrag Abschnitt 16).
    """
    key: str
    heading: str
    header: tuple[str, ...]
    processed: bool
    note: str = ""


# Die fuenf Konzepte, wie sie das Dokument selbst auf S. 2 auffuehrt, mit den
# empirisch gelesenen Kopfzeilen der Version 3.3.
TABLE_CONCEPTS: tuple[TableConcept, ...] = (
    TableConcept(
        key="pi_zu_prozessschritt",
        heading="Prüfidentifikatoren Prüfidentifikator zu Prozessschritt",
        header=(
            "Lfd. Nr.", "AHB",
            "Beschreibung des Anwendungsfalls ausdem AHB (EDIFACT)API-Webservice (API)",
            "Prüfidentifikator", "ReaktionaufPrüfidentifikator", "Prozessbeschreibung",
            "Prozessschritt ausKapitel", "Bezeichnung ausSequenzdiagramm",
            "ProzessschrittausSequenzdiagramm", "Aktion", "Kommunikation von",
            "Kommunikation an", "Zuordnung zueinem Objekt",
            "Zuordnung zueinemGeschäftsvorfall", "ErweiterteZuordnung",
            "Objekteigenschaft", "mortSetrapS", "e satra GpS", "Übertragungsweg",
            "API-Kennung", "etonßuF",
        ),
        processed=True,
    ),
    TableConcept(
        key="tupel_uebersicht",
        heading="Tupel-Übersicht",
        header=("Tupel-Kenn-zeichnung", "Segmentangabe /Parameter", "__Tupel",
                "Bezeichnung der Datenelemente", "Nachrichtentyp"),
        processed=False,
        note="eigenes Modell erforderlich -- zurückgestellt (Freigabe Scoping A)",
    ),
    TableConcept(
        key="objekteigenschaften",
        heading="Objekteigenschaften",
        header=("Objekteigenschaftsbezeichnung", "__Identifikator Beschreibung", "", "Segment"),
        processed=False,
        note="eigenes Modell erforderlich -- zurückgestellt (Freigabe Scoping A)",
    ),
    TableConcept(
        key="erweiterte_zuordnungslogik",
        heading="Erweiterte Zuordnungslogik",
        header=("ErweiterteZuordnungReferenz", "__Erweiterte Zuordnungslogik",
                "Voraussetzungen / Hinweise"),
        processed=False,
        note="eigenes Modell erforderlich -- zurückgestellt (Freigabe Scoping A)",
    ),
    TableConcept(
        key="aenderungshistorie",
        heading="Änderungshistorie",
        header=("Änd-ID", "Ort", "Änderungen", "", "Grund der Anpassung", "Status"),
        processed=False,
        note="bewusst nicht verarbeitet (Auftrag Abschnitt 11) -- Delta-Engine",
    ),
)

_CONCEPT_BY_HEADING = {c.heading: c for c in TABLE_CONCEPTS}
_MAIN_CONCEPT = TABLE_CONCEPTS[0]

# Ein Pruefidentifikator ist fuenfstellig. Gilt fuer Spalte 3 und fuer die
# Reaktionsspalte gleichermassen.
_RE_PI = re.compile(r"^\d{5}$")
# Tupelverweis. Der Zeilenumbruch in der Zelle kann "ZO- T14" erzeugen, deshalb
# das tolerante Leerraummuster -- der gefundene Code wird anschliessend
# leerraumfrei verglichen.
_RE_TUPLE_REF = re.compile(r"Z[OG]-\s*[TF]\s*\d+")
# Platzhalter des Dokuments fuer "hier gibt es nichts".
_PLACEHOLDER = "--"

# EDIFACT-Nachrichtentyp am Anfang der AHB-Spalte. Nachrichtentypbezeichner sind
# im EDIFACT-Standard durchgaengig sechsstellig -- im Stand 3.3 sind das UTILMD,
# MSCONS, IFTSTA, ORDERS, ORDRSP, REMADV, INVOIC, PARTIN, INSRPT, COMDIS, UTILTS,
# REQOTE, QUOTES, PRICAT, ORDCHG und SSQNOT. Bewusst KEINE Positivliste: eine
# kuenftige Version soll einen neuen Typ uebernehmen koennen, ohne dass dieser
# Parser gepflegt werden muss. Stattdessen fuehrt der Report jeden abgeleiteten
# Typ mit Anzahl auf -- ein neuer faellt dort auf.
_RE_MESSAGE_TYPE = re.compile(r"^([A-Z]{6})\b")


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _cell(row: Sequence, index: int) -> str:
    """Rohwert einer Zelle, nur aussen getrimmt -- Zeilenumbrueche bleiben."""
    if index < 0 or index >= len(row):
        return ""
    value = row[index]
    return value.strip() if isinstance(value, str) else ""


def flatten(value: str) -> str:
    """Zellrohwert fuer Vergleich und Anzeige auf eine Zeile bringen.

    Bewusst KEINE Rekonstruktion zerrissener Woerter: "Marktraumumstell\\nung"
    wird zu "Marktraumumstell ung", nicht zu "Marktraumumstellung". Ein
    Zusammenziehen ohne Leerzeichen wuerde umgekehrt echte Wortgrenzen
    vernichten ("Geschäftsprozesse\\nfür"). Beide Varianten waeren geraten;
    gespeichert wird ohnehin der Rohwert (Auftrag Abschnitt 8).
    """
    return re.sub(r"\s+", " ", value.replace("\n", " ")).strip()


def _is_set(value: str) -> bool:
    """Traegt die Zelle eine Aussage? "--" ist die Leerangabe des Dokuments."""
    return bool(value) and value != _PLACEHOLDER


def message_type_of(ahb_value: str) -> str | None:
    """EDIFACT-Nachrichtentyp aus der AHB-Spalte lesen.

    Die Spalte nennt das Anwendungshandbuch, dessen Name mit dem
    Nachrichtentyp beginnt, zu dem es gehoert: "MSCONS AHB",
    "UTILMD AHB Strom", "SSQNOT zur Uebermittlung von Mehr-/Mindermengen".
    Die fuehrenden sechs Grossbuchstaben sind damit KEINE Interpretation,
    sondern eine strukturelle Entnahme -- und je PI widerspruchsfrei
    (0 von 486 PIs haben mehrere AHB-Werte).

    Gibt None zurueck, wenn die Zelle nicht so beginnt (z. B. bei den
    API-Webdienst-Zeilen, die ohnehin keinen PI tragen). Dann bleibt das Feld
    leer, statt einen Typ zu raten.

    Die Sparte aus "UTILMD AHB Strom"/"... Gas" wandert NICHT hierher -- sie
    steht in eigenen Spalten und gehoert zum zurueckgestellten
    Prozessschritt-Konzept.
    """
    match = _RE_MESSAGE_TYPE.match(flatten(ahb_value))
    return match.group(1) if match else None


def header_fingerprint(row: Sequence) -> tuple[str, ...]:
    """Kopfzeile auf ihren Fingerabdruck reduzieren.

    Zeilenumbruch entfernt, sonst unveraendert. Die um 90 Grad gedrehten
    Kopfzellen bleiben damit als Zeichensalat stehen -- genau so sollen sie
    verglichen werden, denn eine Entzifferung waere Interpretation.
    """
    return tuple((c or "").replace("\n", "").strip() for c in row)


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class PidRow:
    """Eine Datenzeile der Tabelle 1 -- vollstaendig, alle 21 Spalten.

    Die Freigabe verlangt ausdruecklich, dass kein PID-Feld stillschweigend
    verloren geht. Deshalb haelt diese Struktur den kompletten Rohwert und
    nicht nur die beiden Spalten, die in das Modell wandern.
    """
    values: tuple[str, ...]
    source_page: int
    source_document: str = ""
    source_document_hash: str = ""

    def raw(self, index: int) -> str:
        return self.values[index] if 0 <= index < len(self.values) else ""

    def text(self, index: int) -> str:
        return flatten(self.raw(index))

    @property
    def lfd_nr(self) -> str:
        return self.raw(COL_LFD_NR)

    @property
    def pi_number(self) -> str:
        value = self.raw(COL_PI)
        return value if _RE_PI.match(value) else ""

    @property
    def description(self) -> str:
        return self.raw(COL_DESCRIPTION)

    @property
    def message_type(self) -> str | None:
        """EDIFACT-Nachrichtentyp laut AHB-Spalte."""
        return message_type_of(self.raw(COL_AHB))

    @property
    def is_api_webservice(self) -> bool:
        """API-Webservice-Zeile: eigener Uebertragungsweg, kein PI.

        Diese Zeilen sind das, was Version 3.1 als eigene Tabelle
        "API-Webservice zu Prozessschritt" gefuehrt haben soll. In 3.3 stehen
        sie in derselben Tabelle und tragen ihren Endpunktpfad in der
        Beschreibungsspalte.
        """
        return self.text(COL_TRANSPORT) == "API"

    def describe(self) -> str:
        return f"S.{self.source_page} Lfd.Nr. {self.lfd_nr or '(ohne)'}"


@dataclass
class ConceptFinding:
    """Ergebnis der Formpruefung fuer ein Tabellenkonzept."""
    key: str
    heading: str
    recognized: bool
    processed: bool
    pages: list[int] = field(default_factory=list)
    data_rows: int = 0
    note: str = ""


@dataclass
class SkippedEntry:
    """Ein erkannter, aber bewusst nicht importierter Fall (Auftrag Abschnitt 14)."""
    reason: str
    source_page: int
    raw: str


@dataclass
class UnresolvedRef:
    """Ein Verweis, der im Dokument selbst nicht aufloesbar ist.

    Wird ausgewiesen, nicht geraten (Auftrag Abschnitt 14). Im Stand 3.3 sind
    das ``ZG-T33`` (in der Tupel-Uebersicht nicht definiert) und der
    Reaktionsverweis auf PI 44108 (kein eigener Anwendungsfall).
    """
    kind: str
    value: str
    source_page: int
    context: str


@dataclass
class PidExtraction:
    """Ergebnis des Lesevorgangs, noch ohne Datenbankbezug.

    ``form_recognized=False`` heisst SKIP: dann ist ``rows`` leer und
    ``form_notes`` sagt, welches Merkmal gefehlt hat. Es wird nichts geraten
    und nichts aus einer aehnlich aussehenden Tabelle uebernommen.
    """
    form_recognized: bool = False
    concepts: list[ConceptFinding] = field(default_factory=list)
    rows: list[PidRow] = field(default_factory=list)
    # Rohbestand der nicht verarbeiteten Konzepte -- gelesen und gezaehlt,
    # damit die Verlustbilanz belegbar ist.
    deferred_rows: dict[str, int] = field(default_factory=dict)
    unresolved: list[UnresolvedRef] = field(default_factory=list)
    freetext_assignments: list[tuple[int, str, str]] = field(default_factory=list)
    form_notes: list[str] = field(default_factory=list)

    @property
    def pages(self) -> list[int]:
        return sorted({r.source_page for r in self.rows})

    @property
    def rows_with_pi(self) -> list[PidRow]:
        return [r for r in self.rows if r.pi_number]

    @property
    def api_rows(self) -> list[PidRow]:
        return [r for r in self.rows if r.is_api_webservice]

    @property
    def rows_without_pi(self) -> list[PidRow]:
        return [r for r in self.rows if not r.pi_number]

    @property
    def pi_numbers(self) -> set[str]:
        return {r.pi_number for r in self.rows_with_pi}

    def column_usage(self) -> list[tuple[int, str, int, bool]]:
        """Verlustbilanz je Spalte: (Index, Name, belegte Zeilen, uebernommen?)."""
        result = []
        for index, name in enumerate(MAIN_COLUMNS):
            filled = sum(1 for r in self.rows if _is_set(r.raw(index)))
            result.append((index, name, filled, index in _MODELLED_COLUMNS))
        return result


@dataclass
class NameDiscrepancy:
    """Abweichende Bezeichnung fuer denselben PI zwischen zwei Quellen.

    Wird ausgewiesen, nicht aufgeloest (Auftrag Abschnitt 9). ``kind``
    unterscheidet die beiden empirisch belegten Faelle: die MIG stellt die
    Prozessfamilie voran ("GeLi Gas / Anmeldung NN"), die PID fuehrt sie in
    einer eigenen Spalte. Wo darueber hinaus der Wortlaut abweicht, ist das
    fachlich beachtenswert und nicht blosse Schreibweise.
    """
    pi_number: str
    mig_name: str
    pid_name: str
    kind: str          # "praefix" | "wortlaut"

    @property
    def prefix_only(self) -> bool:
        return self.kind == "praefix"


@dataclass
class PidImportReport:
    """Ergebnis eines Importlaufs (Auftrag Abschnitt 19)."""
    document: str
    file_hash: str
    regulatory_version_id: int
    regulatory_version_name: str
    extraction: PidExtraction = field(default_factory=PidExtraction)
    created: list[str] = field(default_factory=list)
    existing_name_preserved: list[tuple[str, str, str]] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    skipped: list[SkippedEntry] = field(default_factory=list)
    message_types: dict[str, int] = field(default_factory=dict)
    message_type_missing: list[tuple[str, str]] = field(default_factory=list)
    mig_document: str = ""
    mig_discrepancies: list[NameDiscrepancy] = field(default_factory=list)
    mig_only: list[str] = field(default_factory=list)
    mig_agreements: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def format_report(self) -> str:
        ex = self.extraction
        lines = [
            "=" * 78,
            "IMPORTREPORT PID -- Anwendungsübersicht der Prüfidentifikatoren",
            "=" * 78,
            f"Dokument:             {self.document}",
            f"Hash (SHA-256):       {self.file_hash}",
            f"RegulatoryVersion:    [{self.regulatory_version_id}] {self.regulatory_version_name}",
            "",
            f"Form erkannt:         {'ja' if ex.form_recognized else 'NEIN -- SKIP'}",
            "",
            "A. Tabellenkonzepte (Formprüfung über das gesamte Dokument)",
        ]
        for c in ex.concepts:
            status = "erkannt" if c.recognized else "NICHT ERKANNT"
            mode = "verarbeitet" if c.processed else "zurückgestellt"
            pages = f"S.{c.pages[0]}-{c.pages[-1]}" if c.pages else "-"
            lines.append(f"  [{status:<13}] {c.heading[:46]:<46} {pages:>10} "
                         f"{c.data_rows:>6} Zeilen  ({mode})")
            if c.note:
                lines.append(f"                   {c.note}")
        if ex.form_notes:
            lines.append("")
            lines.append("Formprüfung -- Auffälligkeiten:")
            lines.extend(f"  - {n}" for n in ex.form_notes)

        lines += [
            "",
            "B. Tabelle 1 -- gelesener Bestand",
            f"  Datenzeilen:                    {len(ex.rows)}",
            f"    davon mit Prüfidentifikator:  {len(ex.rows_with_pi)}",
            f"    davon API-Webservice (o. PI): {len(ex.api_rows)}",
            f"    davon ohne PI und ohne API:   "
            f"{len(ex.rows_without_pi) - len(ex.api_rows)}",
            f"  verschiedene Prüfidentifikatoren: {len(ex.pi_numbers)}",
            "",
            "C. Verlustbilanz je Spalte (Freigabe: kein PID-Feld geht stillschweigend verloren)",
            f"  {'#':>2}  {'Spalte':<62} {'belegt':>7}  Verbleib",
        ]
        for index, name, filled, modelled in ex.column_usage():
            if index == COL_AHB:
                verbleib = "-> ProcessIdentifier.message_type"
            elif modelled:
                verbleib = "-> ProcessIdentifier"
            else:
                verbleib = "nur Report (spätere Modellierung)"
            lines.append(f"  {index:>2}  {name[:62]:<62} {filled:>7}  {verbleib}")
        if self.message_types:
            lines.append("")
            lines.append("  Abgeleitete Nachrichtentypen (aus der AHB-Spalte):")
            for kind, count in sorted(self.message_types.items()):
                lines.append(f"    {kind:<10} {count:>4} PI")
        if self.message_type_missing:
            lines.append("")
            lines.append("  Ohne ableitbaren Nachrichtentyp -- Feld bleibt leer statt geraten:")
            for pi_number, ahb in self.message_type_missing:
                lines.append(f"    PI {pi_number}: AHB-Spalte {ahb!r}")

        lines += [
            "",
            "D. Import in die Wissensbasis (Scoping A)",
            f"  Neu angelegt:                   {len(self.created)}",
            f"  Bereits vorhanden (unverändert): {len(self.existing_name_preserved)}",
            f"  Konflikte:                      {len(self.conflicts)}",
            f"  Übersprungen:                   {len(self.skipped)}",
        ]

        lines += ["", "E. Abgleich mit Prompt 1 (MIG-PI-Namen)"]
        if not self.mig_document:
            lines.append("  nicht durchgeführt (keine MIG-Datei angegeben)")
        else:
            gemeinsam = len(self.mig_agreements) + len(self.mig_discrepancies)
            praefix = sum(1 for d in self.mig_discrepancies if d.prefix_only)
            lines += [
                f"  MIG-Dokument:                   {self.mig_document}",
                f"  PI in beiden Quellen:           {gemeinsam}",
                f"    Bezeichnung identisch:        {len(self.mig_agreements)}",
                f"    Bezeichnung abweichend:       {len(self.mig_discrepancies)}",
                f"      davon reine Präfixdifferenz: {praefix}",
                f"      davon abweichender Wortlaut: {len(self.mig_discrepancies) - praefix}",
                f"  nur in der MIG:                 {len(self.mig_only)}",
                f"  nur in der PID:                 "
                f"{len(ex.pi_numbers) - gemeinsam}",
            ]
            wortlaut = [d for d in self.mig_discrepancies if not d.prefix_only]
            if wortlaut:
                lines.append("")
                lines.append("  Abweichender Wortlaut -- NICHT überschrieben, zur Entscheidung:")
                for d in wortlaut[:12]:
                    lines.append(f"    PI {d.pi_number}")
                    lines.append(f"       MIG: {d.mig_name}")
                    lines.append(f"       PID: {d.pid_name}")
                if len(wortlaut) > 12:
                    lines.append(f"    ... und {len(wortlaut) - 12} weitere")

        if ex.unresolved:
            lines += ["", "F. Nicht auflösbare Verweise (Abschnitt 14 -- nicht geraten)"]
            for u in ex.unresolved:
                lines.append(f"  - {u.kind} {u.value!r} auf S.{u.source_page} ({u.context})")
        if ex.freetext_assignments:
            lines += ["", f"G. Zuordnungszellen mit Bedingungsfreitext statt Code: "
                          f"{len(ex.freetext_assignments)}"]
            for page, lfd, text in ex.freetext_assignments[:5]:
                lines.append(f"  - S.{page} Lfd.Nr. {lfd}: {text[:80]}")
            if len(ex.freetext_assignments) > 5:
                lines.append(f"  ... und {len(ex.freetext_assignments) - 5} weitere")

        if self.existing_name_preserved:
            lines += ["", "H. Bereits vorhanden -- Atlas-Name beibehalten (Fall C aus Prompt 1)"]
            for pi, existing, raw in self.existing_name_preserved[:10]:
                lines.append(f"  {pi}  Atlas: {existing[:34]:<34} PID: {raw[:34]}")
            if len(self.existing_name_preserved) > 10:
                lines.append(f"  ... und {len(self.existing_name_preserved) - 10} weitere")
        if self.conflicts:
            lines += ["", "Konflikte:"]
            lines.extend(f"  - {c}" for c in self.conflicts)
        if self.skipped:
            lines += ["", "Übersprungen:"]
            for s in self.skipped:
                lines.append(f"  - S.{s.source_page} {s.raw[:60]!r}: {s.reason}")
        if self.errors:
            lines += ["", "Fehler:"]
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines += ["", "Warnungen:"]
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Lesevorgang
# ---------------------------------------------------------------------------

def page_heading(page) -> str | None:
    """Tabellenkonzept laut Kopfzeile der Seite, oder None auf Textseiten."""
    text = page.extract_text() or ""
    first = text.split("\n", 1)[0].strip() if text else ""
    match = _PAGE_HEADING_RE.match(first)
    return match.group(1).strip() if match else None


def iter_page_tables(pdf) -> Iterator[tuple[int, str | None, list]]:
    """Alle Tabellen des Dokuments als (Seite, Kopfzeilen-Konzept, Tabelle).

    Getrennt vom Auswerten, damit dieses gegen synthetische Tabellen getestet
    werden kann und nicht nur gegen ein 82-seitiges PDF.
    """
    for page_number, page in enumerate(pdf.pages, start=1):
        heading = page_heading(page)
        for table in page.extract_tables():
            if table:
                yield page_number, heading, table


def collect_pid_rows(tables: Iterator[tuple[int, str | None, list]]) -> PidExtraction:
    """Formpruefung und Zeilenaufbau ueber das gesamte Dokument.

    Ablauf:

        Kopfzeile der Seite -> Tabellenkonzept
        unbekanntes Konzept -> als "nicht erkannt" melden (Abschnitt 16)
        Kopfzeile der Tabelle != Fingerabdruck -> Konzept nicht erkannt
        Konzept 1 -> Datenzeilen sammeln (alle 21 Spalten roh)
        Konzept 2-5 -> nur zaehlen, nicht verarbeiten

    Eine Seite ohne Kopfzeilen-Konzept ist eine Textseite der Einleitung; die
    dortige Legendentabelle (S. 5) ist bewusst kein Datenbereich.
    """
    result = PidExtraction()
    seen: dict[str, ConceptFinding] = {}
    unknown_headings: set[str] = set()

    for page_number, heading, table in tables:
        if heading is None:
            continue
        concept = _CONCEPT_BY_HEADING.get(heading)
        if concept is None:
            # Auftrag Abschnitt 16: ein in einer kuenftigen Version neu
            # hinzukommendes Tabellenkonzept muss auffallen, statt still
            # ignoriert zu werden.
            if heading not in unknown_headings:
                unknown_headings.add(heading)
                result.form_notes.append(
                    f"S.{page_number}: unbekanntes Tabellenkonzept {heading!r} -- "
                    "nicht verarbeitet, Dokumentform weicht von der geprüften ab"
                )
                result.concepts.append(ConceptFinding(
                    key="(unbekannt)", heading=heading, recognized=False,
                    processed=False, pages=[page_number],
                    note="in dieser Version nicht vorgesehen -- Formprüfung schlägt an",
                ))
            continue

        finding = seen.get(concept.key)
        if finding is None:
            finding = ConceptFinding(
                key=concept.key, heading=concept.heading, recognized=True,
                processed=concept.processed, note=concept.note,
            )
            seen[concept.key] = finding
            result.concepts.append(finding)
        if page_number not in finding.pages:
            finding.pages.append(page_number)

        fingerprint = header_fingerprint(table[0])
        if fingerprint != concept.header:
            finding.recognized = False
            finding.note = "Kopfzeile weicht von der geprüften Form ab"
            result.form_notes.append(
                f"S.{page_number}: Kopfzeile von {concept.heading!r} weicht ab -- "
                f"erwartet {len(concept.header)} Zellen, gelesen {len(fingerprint)}"
            )
            continue

        data = table[1:]
        finding.data_rows += len(data)
        if not concept.processed:
            result.deferred_rows[concept.key] = finding.data_rows
            continue

        for row in data:
            if len(row) != len(concept.header):
                result.form_notes.append(
                    f"S.{page_number}: Datenzeile mit {len(row)} statt "
                    f"{len(concept.header)} Zellen -- übersprungen"
                )
                continue
            result.rows.append(PidRow(
                values=tuple(_cell(row, i) for i in range(len(row))),
                source_page=page_number,
            ))

    main = seen.get(_MAIN_CONCEPT.key)
    if main is None:
        result.form_notes.append(
            f"Tabellenkonzept {_MAIN_CONCEPT.heading!r} im Dokument nicht gefunden -- SKIP"
        )
    elif not main.recognized:
        result.form_notes.append("Haupttabelle mit abweichender Kopfzeile -- SKIP")
    elif not result.rows:
        result.form_notes.append("Haupttabelle erkannt, aber ohne Datenzeilen -- SKIP")
    else:
        # Alle fuenf bekannten Konzepte muessen vorkommen. Fehlt eines, ist das
        # eine Strukturaenderung und wird gemeldet -- der Import der
        # Haupttabelle bleibt davon unberuehrt, weil sie fuer sich vollstaendig
        # ist.
        for concept in TABLE_CONCEPTS:
            if concept.key not in seen:
                result.form_notes.append(
                    f"Tabellenkonzept {concept.heading!r} fehlt in diesem Dokumentstand"
                )
        result.form_recognized = True

    if not result.form_recognized:
        result.rows.clear()
    return result


def analyse_references(extraction: PidExtraction, tuple_codes: set[str]) -> None:
    """Verweise der Haupttabelle pruefen und Befunde in die Extraktion schreiben.

    Aendert nichts an den Daten -- es geht ausschliesslich darum, nicht
    aufloesbare Verweise sichtbar zu machen, statt sie zu raten
    (Auftrag Abschnitt 14). Aufgeloest wird gegen die Tupelcodes, die beim
    Lesen der Tupel-Uebersicht anfallen; ist diese nicht lesbar, wird der
    Tupelabgleich uebersprungen und nicht geschaetzt.
    """
    known_pi = extraction.pi_numbers
    for row in extraction.rows:
        reaction = flatten(row.raw(COL_REACTION))
        if _RE_PI.match(reaction) and reaction not in known_pi:
            extraction.unresolved.append(UnresolvedRef(
                kind="Reaktion auf Prüfidentifikator", value=reaction,
                source_page=row.source_page,
                context=f"{row.describe()}, kein eigener Anwendungsfall in Tabelle 1",
            ))
        for column in (COL_ASSIGN_OBJECT, COL_ASSIGN_TRANSACTION):
            raw = row.raw(column)
            if not _is_set(raw):
                continue
            text = flatten(raw)
            found = [re.sub(r"\s+", "", m.group(0)) for m in _RE_TUPLE_REF.finditer(text)]
            rest = _RE_TUPLE_REF.sub("", text)
            rest = re.sub(r"[\s,;.]|und|oder|–|-", "", rest, flags=re.IGNORECASE)
            if rest:
                # Bedingungslogik als Fliesstext. Der Tupelcode laesst sich
                # herausziehen, die Bedingung nicht ohne Interpretation.
                extraction.freetext_assignments.append(
                    (row.source_page, row.lfd_nr or "(ohne)", text)
                )
            if not tuple_codes:
                continue
            for code in found:
                if code not in tuple_codes:
                    extraction.unresolved.append(UnresolvedRef(
                        kind="Tupel-Kennzeichnung", value=code,
                        source_page=row.source_page,
                        context=f"{row.describe()}, in der Tupel-Übersicht nicht definiert",
                    ))


def read_tuple_codes(pdf) -> set[str]:
    """Die Tupel-Kennzeichnungen der Tupel-Uebersicht lesen.

    Nur zum Aufloesen der Verweise aus der Haupttabelle -- die Tupel-Uebersicht
    selbst wird in diesem Schritt NICHT importiert (Freigabe: zurueckgestellt,
    weil sie sich nicht verlustfrei in ``CodeList``/``CodeListEntry`` abbilden
    laesst; die Segmentangabe haette dort kein eigenes Feld).
    """
    concept = _CONCEPT_BY_HEADING["Tupel-Übersicht"]
    codes: set[str] = set()
    for page_number, page in enumerate(pdf.pages, start=1):
        if page_heading(page) != concept.heading:
            continue
        for table in page.extract_tables():
            if not table or header_fingerprint(table[0]) != concept.header:
                continue
            for row in table[1:]:
                value = _cell(row, 0)
                if _RE_TUPLE_REF.fullmatch(value):
                    codes.add(re.sub(r"\s+", "", value))
    return codes


def extract_pid(pdf_path: str) -> PidExtraction:
    """Formpruefung und Extraktion fuer eine PID-Datei."""
    file_hash = compute_file_hash(pdf_path)
    document_name = pdf_path.rsplit("/", 1)[-1]
    with pdfplumber.open(pdf_path) as pdf:
        result = collect_pid_rows(iter_page_tables(pdf))
        tuple_codes = read_tuple_codes(pdf) if result.form_recognized else set()
    for row in result.rows:
        row.source_document = document_name
        row.source_document_hash = file_hash
    if result.form_recognized:
        analyse_references(result, tuple_codes)
    return result


# ---------------------------------------------------------------------------
# Abgleich mit Prompt 1 (Auftrag Abschnitt 9)
# ---------------------------------------------------------------------------

def classify_discrepancy(mig_name: str, pid_name: str) -> str | None:
    """Art der Abweichung zwischen MIG- und PID-Bezeichnung bestimmen.

    Gibt None zurueck, wenn beide Bezeichnungen uebereinstimmen.

    Die MIG stellt die Prozessfamilie voran ("GeLi Gas / Anmeldung NN"), die
    PID fuehrt sie in einer eigenen Spalte ("Anmeldung NN"). Faellt der
    Unterschied genau darauf zusammen, ist er formal -- sonst weicht der
    Wortlaut ab und das ist fachlich beachtenswert. In KEINEM Fall wird
    etwas ueberschrieben; die Einstufung dient nur dem Report.
    """
    mig = flatten(mig_name)
    pid = flatten(pid_name)
    if mig == pid:
        return None
    if "/" in mig and mig.split("/", 1)[1].strip() == pid:
        return "praefix"
    return "wortlaut"


def compare_with_mig(
    pid_names: dict[str, set[str]],
    mig_names: dict[str, str],
) -> tuple[list[str], list[NameDiscrepancy], list[str]]:
    """PID- und MIG-Bezeichnungen gegenueberstellen.

    Liefert (uebereinstimmend, abweichend, nur_in_mig). Rein lesend und ohne
    Datenbankbezug, damit der Abgleich fuer sich testbar ist.
    """
    agreements: list[str] = []
    discrepancies: list[NameDiscrepancy] = []
    for pi_number in sorted(set(pid_names) & set(mig_names)):
        mig_name = mig_names[pi_number]
        variants = sorted(pid_names[pi_number])
        kinds = {v: classify_discrepancy(mig_name, v) for v in variants}
        if any(kind is None for kind in kinds.values()):
            agreements.append(pi_number)
            continue
        # Mehrere PID-Schreibweisen: die fachlich schwerere Einstufung gewinnt,
        # damit eine Wortlautabweichung nicht hinter einer Praefixdifferenz
        # verschwindet.
        kind = "wortlaut" if "wortlaut" in kinds.values() else "praefix"
        discrepancies.append(NameDiscrepancy(
            pi_number=pi_number, mig_name=mig_name,
            pid_name=" | ".join(variants), kind=kind,
        ))
    mig_only = sorted(set(mig_names) - set(pid_names))
    return agreements, discrepancies, mig_only


def pid_message_types(extraction: PidExtraction) -> dict[str, str | None]:
    """PI -> EDIFACT-Nachrichtentyp laut AHB-Spalte.

    Die AHB-Spalte ist je PI widerspruchsfrei (empirisch: 0 von 486 PIs mit
    mehreren Werten). Kommen wider Erwarten doch mehrere vor, wird None
    zurueckgegeben -- dann bleibt das Feld leer, statt einen davon zu waehlen.
    """
    seen: dict[str, set[str | None]] = {}
    for row in extraction.rows_with_pi:
        seen.setdefault(row.pi_number, set()).add(row.message_type)
    return {
        pi_number: (next(iter(types)) if len(types) == 1 else None)
        for pi_number, types in seen.items()
    }


def pid_names_by_number(extraction: PidExtraction) -> dict[str, set[str]]:
    """PI -> Menge der in der PID vorkommenden Beschreibungen.

    Eine Menge, weil ein PI in vielen Prozessschritten auftritt (PI 33001 in
    47 Zeilen). Im Stand 3.3 fuehrt das genau bei PI 55672 zu zwei
    Schreibweisen.
    """
    result: dict[str, set[str]] = {}
    for row in extraction.rows_with_pi:
        result.setdefault(row.pi_number, set()).add(flatten(row.description))
    return result


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_pid_process_identifiers(
    db: Session,
    pdf_path: str,
    regulatory_version_id: int,
    mig_pdf_path: str | None = None,
) -> PidImportReport:
    """Die Pruefidentifikatoren der PID in die Wissensbasis uebernehmen.

    Bewusst OHNE ``reimport``-Schalter: der Lauf ist von sich aus idempotent.
    Ein bestehender ``ProcessIdentifier`` wird nie veraendert -- weder Name noch
    Prozessgruppe noch Rollen -- und ein zweiter Lauf legt nichts Zusaetzliches
    an. Das ist Fall C aus Prompt 1, hier zusaetzlich fachlich begruendet: die
    PID-Bezeichnung ist ohne ihre Nachbarspalten nicht eindeutig (44147 und
    44148 tragen beide "Anfrage an MSB mit Abhaengigkeiten"), taugt also
    grundsaetzlich nicht als Ersatz fuer einen bestehenden Namen.

    Was ein neuer PI bekommt und warum:

    * ``pi_number`` und ``name`` -- das Einzige, was die PID je PI eindeutig belegt.
    * ``message_type`` aus der AHB-Spalte. Atlas braucht alle Formate, nicht
      nur UTILMD: die PID fuehrt PIs aus 16 verschiedenen Nachrichtentypen, und
      der Modell-Default "UTILMD" waere fuer die meisten davon schlicht falsch.
      Die AHB-Spalte nennt das Anwendungshandbuch, dessen Name mit dem
      Nachrichtentyp beginnt ("MSCONS AHB"), ist je PI widerspruchsfrei und
      widerspricht bei keinem der 88 bereits bekannten PIs dem, was Atlas heute
      fuehrt. Laesst sich kein Typ entnehmen, bleibt das Feld leer statt
      geraten -- gesetzt wird dann ``null()`` und nicht ``None``, weil
      SQLAlchemy bei ``None`` den Spalten-Default zieht und doch wieder
      "UTILMD" schreiben wuerde.
      Die Sparte aus "UTILMD AHB Strom" wandert NICHT mit: sie gehoert zum
      zurueckgestellten Prozessschritt-Konzept.
    * ``process_group_id``, ``sender_role``, ``receiver_role`` bleiben leer.
      Rollen stehen in der PID zwar als "Kommunikation von/an", aber am
      Prozessschritt und nicht am PI: 113 bzw. 142 von 486 PIs haben mehrere
      verschiedene Werte. Sie hier zu setzen hiesse, einen davon zu raten.
    """
    file_hash = compute_file_hash(pdf_path)
    document_name = pdf_path.rsplit("/", 1)[-1]
    version = db.get(models.RegulatoryVersion, regulatory_version_id)

    report = PidImportReport(
        document=document_name,
        file_hash=file_hash,
        regulatory_version_id=regulatory_version_id,
        regulatory_version_name=version.name if version else "(unbekannt)",
    )
    if version is None:
        report.errors.append(f"RegulatoryVersion {regulatory_version_id} existiert nicht")
        return report

    report.extraction = extract_pid(pdf_path)
    if not report.extraction.form_recognized:
        report.warnings.append(
            "Erwartete Dokumentform nicht eindeutig erkannt -- kein Import (Abschnitt 6)"
        )
        return report

    by_number = pid_names_by_number(report.extraction)
    types_by_number = pid_message_types(report.extraction)

    if mig_pdf_path:
        # Der Abgleich laeuft gegen die MIG-Quelle selbst und nicht gegen den
        # Atlas-Namen: nur so lassen sich die beiden Quellen benennen
        # (Abschnitt 9 verlangt beide Werte MIT Quellenangabe). Der Atlas-Name
        # kann kuratiert und damit eine dritte Fassung sein -- er steht separat
        # in existing_name_preserved.
        from .regulatory_extraction_mig import extract_pi_entries

        mig_extraction = extract_pi_entries(mig_pdf_path)
        if mig_extraction.form_recognized:
            report.mig_document = mig_pdf_path.rsplit("/", 1)[-1]
            mig_names = {e.pi_number: e.process_name for e in mig_extraction.entries}
            agreements, discrepancies, mig_only = compare_with_mig(by_number, mig_names)
            report.mig_agreements = agreements
            report.mig_discrepancies = discrepancies
            report.mig_only = mig_only
        else:
            report.warnings.append(
                f"MIG-Abgleich übersprungen: {mig_pdf_path} nicht in erwarteter Form"
            )

    existing = {pi.pi_number: pi for pi in db.query(models.ProcessIdentifier).all()}

    for pi_number in sorted(by_number):
        names = by_number[pi_number]
        message_type = types_by_number.get(pi_number)
        found = existing.get(pi_number)
        if found is not None:
            # Fall C: bestehender Eintrag bleibt unangetastet -- auch sein
            # Nachrichtentyp. Ob sein Name aus der MIG stammt oder kuratiert
            # ist, sagt das Schema nicht; ein Unterschied ist deshalb kein
            # regulatorischer Konflikt.
            report.existing_name_preserved.append(
                (pi_number, found.name, " | ".join(sorted(names)))
            )
            if found.message_type and message_type and found.message_type != message_type:
                # Waere ein echter Widerspruch zwischen zwei Quellen. Im Stand
                # 3.3 kommt er nicht vor (0 von 88) -- gemeldet statt behoben.
                report.conflicts.append(
                    f"PI {pi_number}: Nachrichtentyp in Atlas {found.message_type!r}, "
                    f"laut PID {message_type!r} -- nicht überschrieben"
                )
            continue

        if len(names) > 1:
            # Zwei Schreibweisen in derselben Quelle: nicht eigenstaendig
            # entscheiden, welche gilt (Abschnitt 14).
            report.conflicts.append(
                f"PI {pi_number} kommt in derselben Quelle mit abweichenden Bezeichnungen "
                f"vor ({sorted(names)}) -- nicht importiert"
            )
            for row in report.extraction.rows_with_pi:
                if row.pi_number == pi_number:
                    report.skipped.append(SkippedEntry(
                        reason="mehrdeutige Bezeichnung innerhalb derselben Quelle",
                        source_page=row.source_page,
                        raw=f"{pi_number} {flatten(row.description)}",
                    ))
            continue

        if message_type:
            report.message_types[message_type] = report.message_types.get(message_type, 0) + 1
        else:
            ahb = next(
                (r.text(COL_AHB) for r in report.extraction.rows_with_pi
                 if r.pi_number == pi_number),
                "",
            )
            report.message_type_missing.append((pi_number, ahb))

        created = models.ProcessIdentifier(
            pi_number=pi_number,
            name=next(iter(names)),
            # null() statt None -- sonst greift der Spalten-Default "UTILMD".
            message_type=message_type or null(),
            process_group_id=None,
            sender_role=None,
            receiver_role=None,
        )
        db.add(created)
        existing[pi_number] = created
        report.created.append(pi_number)

    db.commit()
    return report


__all__ = [
    "MAIN_COLUMNS",
    "TABLE_CONCEPTS",
    "ConceptFinding",
    "NameDiscrepancy",
    "PidExtraction",
    "PidImportReport",
    "PidRow",
    "SkippedEntry",
    "TableConcept",
    "UnresolvedRef",
    "analyse_references",
    "classify_discrepancy",
    "collect_pid_rows",
    "compare_with_mig",
    "extract_pid",
    "flatten",
    "header_fingerprint",
    "import_pid_process_identifiers",
    "iter_page_tables",
    "page_heading",
    "message_type_of",
    "pid_message_types",
    "pid_names_by_number",
    "read_tuple_codes",
    "resolve_active_regulatory_version",
]
