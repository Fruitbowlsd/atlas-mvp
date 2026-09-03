"""Deterministische MIG-Extraktion: Pruefidentifikator -> Prozessbezeichnung (Issue #46).

Zweiter Baustein der Regulatory-Extraktionspipeline neben der AHB-Extraktion in
``regulatory_extraction.py``. Dieselbe Architektur:

    Dokument -> Formpruefung -> deterministische Extraktion -> Wissensbasis

Bewusst OHNE LLM. Die MIG liefert die amtliche Bezeichnung eines PI; was diese
Bezeichnung fachlich bedeutet, ist eine spaetere, getrennte Aufgabe.

Eigenes Modul statt Erweiterung von ``regulatory_extraction.py`` (Freigabe
Punkt 4): jenes Modul ist auf 1263 Zeilen durchgaengig AHB-spezifisch
(Spaltengeometrie, Kapitelscan, Fussnoten). Gemeinsam genutzt wird nur, was
wirklich generisch ist -- ``compute_file_hash`` und
``resolve_active_regulatory_version``. Ein erzwungenes Generalisieren der
laufenden AHB-Logik waere Risiko ohne Gegenwert.

Die Parserform stammt aus der empirischen Strukturanalyse des echten Dokuments
(Issue #46, Befund) und NICHT aus einer Annahme. Drei Befunde bestimmen den
Aufbau:

* Die MIG hat keine nummerierte Kapitelstruktur -- der Kapitelscan der
  AHB-Extraktion ist hier nicht anwendbar. Anker ist das Datenelement 1154.
* Es gibt im ganzen Dokument KEINE mehrzeilige Tabellenzelle. Die Word-Tabelle
  zieht je Textzeile eine eigene Linie, deshalb liefert
  ``extract_tables()`` umbrochene Bezeichnungen als FOLGEZEILE. Der Parser muss
  zusammenfuehren, nicht aufteilen.
* Der Spaltenindex von "Anwendung / Bemerkung" ist nicht stabil (6 von 7, 8 von
  10, 8 von 11) -- er wird je Tabelle aus der Kopfzeile bestimmt.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator, Sequence

import pdfplumber
from sqlalchemy.orm import Session

from . import models
from .regulatory_extraction import compute_file_hash, resolve_active_regulatory_version

# ---------------------------------------------------------------------------
# Konstanten der erwarteten Dokumentform
# ---------------------------------------------------------------------------

# Kopfzelle der Zielspalte. Sie ist das einzige verlaessliche Merkmal, um die
# Spalte zu finden -- der Index wechselt im selben Dokument.
_HEADER_ANWENDUNG = "Anwendung / Bemerkung"
# Weitere Zellen derselben Kopfzeile. Werden zur Absicherung mitgeprueft, damit
# nicht irgendeine Tabelle mit gleichlautender Kopfzelle als Datenelementtabelle
# durchgeht.
_HEADER_COMPANIONS = ("Bez", "Name")
# Gruppenkopf ueber der Kopfzeile ("Standard | BDEW"). Wiederholt sich auf jeder
# Folgeseite und darf den laufenden Block NICHT beenden.
_BANNER_CELLS = ("Standard", "BDEW")

# Anker: Datenelement 1154 "Referenz, Identifikation" in der Auspraegung
# "Pruefidentifikator". Dokumentweit gibt es 18 Zeilen mit Bez 1154, aber nur
# diese eine traegt in der Zielspalte "Pruefidentifikator" -- die uebrigen sind
# Vorgangsnummer, ID der Marktlokation, OBIS-Kennzahl usw.
_ANCHOR_BEZ = "1154"
_ANCHOR_VALUE = "Prüfidentifikator"
# Vorgeschaltete Qualifier-Zeile 1153. Zweites, unabhaengiges Merkmal: der
# Anker soll nicht an einer einzelnen Zelle haengen.
_ANCHOR_QUALIFIER_BEZ = "1153"
_ANCHOR_QUALIFIER_CODE = "Z13"

# Ein Listeneintrag: fuenfstellige PI-Nummer, Leerraum, Bezeichnung.
_RE_PI_ENTRY = re.compile(r"^(\d{5})\s+(\S.*)$")


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class PiEntry:
    """Ein aus der MIG gelesenes Paar PI -> Prozessbezeichnung.

    ``process_name`` ist der Rohwert des Dokuments, nicht interpretiert
    (Auftrag Abschnitt 8): "GeLi Gas / Anmeldung NN", nicht "Lieferbeginn".

    Provenance wandert bewusst in DIESE Struktur und nicht in das
    ``ProcessIdentifier``-Modell (Freigabe Punkt 1): das Modell wird fuer diesen
    Schritt nicht erweitert. ``source_document_hash`` ist die Dokumentidentitaet,
    die Atlas heute schon verwendet (``MessageDefinition.quelle_hash``) -- eine
    eigene Dokumententabelle mit einer ``id`` gibt es noch nicht. Wird sie
    spaeter eingefuehrt, laesst sich ueber genau diesen Hash verknuepfen, ohne
    den Parser anzufassen.
    """
    pi_number: str
    process_name: str
    source_page: int
    source_document: str = ""
    source_document_hash: str = ""
    # Anzahl der Quellzeilen, aus denen die Bezeichnung zusammengesetzt wurde.
    # Macht die Zusammenfuehrung messbar statt schaetzbar -- analog zu
    # Footnote.lines in der AHB-Extraktion.
    source_lines: int = 1
    # Erste Seite des Eintrags, falls er ueber einen Seitenumbruch laeuft.
    # Im Dokumentstand G1.1 betrifft das 44148 (S.52 -> S.53).
    source_page_start: int = 0

    def __post_init__(self) -> None:
        if not self.source_page_start:
            self.source_page_start = self.source_page

    @property
    def spans_page_break(self) -> bool:
        return self.source_page_start != self.source_page

    def append_line(self, more: str) -> None:
        """Umbrochene Fortsetzungszeile anhaengen.

        Verbunden wird mit EINEM Leerzeichen. Fuer G1.1 ist das nachweislich
        verlustfrei: alle 52 Fortsetzungszeilen beginnen mit einem vollstaendigen
        Wort. Ein am Zeilenende getrenntes Wort faengt ``_looks_hyphenated`` ab.
        """
        self.process_name = f"{self.process_name} {more}".strip()
        self.source_lines += 1


@dataclass
class SkippedEntry:
    """Ein erkannter, aber bewusst nicht importierter Fall (Auftrag Abschnitt 14)."""
    reason: str
    source_page: int
    raw: str


@dataclass
class PiExtraction:
    """Ergebnis des Lesevorgangs, noch ohne Datenbankbezug.

    ``form_recognized=False`` heisst: SKIP. Dann ist ``entries`` leer und
    ``form_notes`` sagt, welches Merkmal gefehlt hat -- es wird nichts geraten
    und nichts aus einer aehnlich aussehenden Tabelle uebernommen
    (Auftrag Abschnitt 6).
    """
    form_recognized: bool = False
    anchor_pages: list[int] = field(default_factory=list)
    anchor_column_index: int | None = None
    block_end_marker: str = ""
    entries: list[PiEntry] = field(default_factory=list)
    skipped: list[SkippedEntry] = field(default_factory=list)
    form_notes: list[str] = field(default_factory=list)

    @property
    def pages(self) -> list[int]:
        return sorted({e.source_page_start for e in self.entries})

    @property
    def multiline_entries(self) -> int:
        return sum(1 for e in self.entries if e.source_lines > 1)


@dataclass
class PiImportReport:
    """Ergebnis eines Importlaufs (Auftrag Abschnitt 20)."""
    document: str
    file_hash: str
    regulatory_version_id: int
    regulatory_version_name: str
    extraction: PiExtraction = field(default_factory=PiExtraction)
    created: list[str] = field(default_factory=list)
    existing_name_preserved: list[tuple[str, str, str]] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def entries_detected(self) -> int:
        return len(self.extraction.entries)

    def format_report(self) -> str:
        ex = self.extraction
        pages = ", ".join(str(p) for p in ex.pages) or "-"
        lines = [
            "=" * 72,
            "IMPORTREPORT MIG -- Prüfidentifikator -> Prozessbezeichnung",
            "=" * 72,
            f"Dokument:             {self.document}",
            f"Hash (SHA-256):       {self.file_hash}",
            f"RegulatoryVersion:    [{self.regulatory_version_id}] {self.regulatory_version_name}",
            "",
            f"Form erkannt:         {'ja' if ex.form_recognized else 'NEIN -- SKIP'}",
            f"Anker (DE 1154):      Seite(n) {ex.anchor_pages or '-'}, "
            f"Spaltenindex {ex.anchor_column_index}",
            f"Blockende erkannt an: {ex.block_end_marker or '-'}",
            f"Quellseiten:          {pages}",
            "",
            f"Einträge erkannt:     {len(ex.entries)}",
            f"  davon mehrzeilig:   {ex.multiline_entries}",
            f"  über Seitenumbruch: {sum(1 for e in ex.entries if e.spans_page_break)}",
            f"Neu angelegt:         {len(self.created)}",
            f"Bereits vorhanden:    {len(self.existing_name_preserved)} (Name unverändert)",
            f"Konflikte:            {len(self.conflicts)}",
            f"Übersprungen:         {len(ex.skipped)}",
        ]
        if ex.form_notes:
            lines.append("")
            lines.append("Formprüfung:")
            lines.extend(f"  - {n}" for n in ex.form_notes)
        if self.existing_name_preserved:
            lines.append("")
            lines.append("Bereits vorhanden -- kuratierter Name beibehalten (Abschnitt 15, Fall C):")
            lines.append(f"  {'PI':<8} {'Atlas-Name':<38} MIG-Rohwert")
            for pi, existing, raw in self.existing_name_preserved:
                lines.append(f"  {pi:<8} {existing[:38]:<38} {raw}")
        if ex.skipped:
            lines.append("")
            lines.append("Übersprungen:")
            for s in ex.skipped:
                lines.append(f"  - S.{s.source_page} {s.raw[:50]!r}: {s.reason}")
        if self.conflicts:
            lines.append("")
            lines.append("Konflikte:")
            lines.extend(f"  - {c}" for c in self.conflicts)
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
# Zeilenklassifikation
# ---------------------------------------------------------------------------

def _cell(row: Sequence, index: int) -> str:
    if index < 0 or index >= len(row):
        return ""
    value = row[index]
    return value.strip() if isinstance(value, str) else ""


def _values(row: Sequence) -> list[str]:
    return [c.strip() for c in row if isinstance(c, str) and c.strip()]


def header_column_index(row: Sequence) -> int | None:
    """Index der Spalte "Anwendung / Bemerkung" in einer Kopfzeile.

    Gibt None zurueck, wenn die Zeile keine Kopfzeile der Datenelementtabelle
    ist. Zusaetzlich zur Zielzelle werden "Bez" und "Name" verlangt: die
    Zielzelle allein koennte auch in einem anderen Tabellentyp auftauchen.
    """
    values = _values(row)
    if _HEADER_ANWENDUNG not in values:
        return None
    if not all(companion in values for companion in _HEADER_COMPANIONS):
        return None
    for index, cell in enumerate(row):
        if isinstance(cell, str) and cell.strip() == _HEADER_ANWENDUNG:
            return index
    return None


def is_page_banner(row: Sequence) -> bool:
    """Gruppenkopf "Standard | BDEW" ueber der eigentlichen Kopfzeile.

    Wiederholt sich auf jeder Folgeseite. Ein erster Prototyp, der ihn als
    "andere Spalte gefuellt" gewertet hat, beendete den Block am Seitenumbruch
    vorzeitig und verlor 24 Eintraege -- deshalb steht das hier explizit.
    """
    values = _values(row)
    return all(cell in values for cell in _BANNER_CELLS)


def is_anchor_row(row: Sequence, column: int) -> bool:
    """Zeile "1154 Referenz, Identifikation ... | Prüfidentifikator"."""
    return _cell(row, 0) == _ANCHOR_BEZ and _cell(row, column) == _ANCHOR_VALUE


def is_anchor_qualifier_row(row: Sequence, column: int) -> bool:
    """Vorgeschaltete Zeile "1153 Referenz, Qualifier ... | Z13 Prüfidentifikator"."""
    if _cell(row, 0) != _ANCHOR_QUALIFIER_BEZ:
        return False
    value = _cell(row, column)
    return _ANCHOR_QUALIFIER_CODE in value and _ANCHOR_VALUE in value


def _looks_hyphenated(previous: str) -> bool:
    """Am Zeilenende getrenntes Wort.

    Nur der Bindestrich ist deterministisch feststellbar. Ein Umbruch MITTEN im
    Wort ohne Trennzeichen -- die Aenderungshistorie auf S.168 bricht
    "Geschaeftsdatenanfra" / "ge" so um -- traegt keine erkennbare Markierung
    und liesse sich nur raten. Im Pruefidentifikator-Block kommt er im Stand
    G1.1 nicht vor (alle 52 Fortsetzungszeilen beginnen mit einem vollstaendigen
    Wort); die Grenze ist im Report vermerkt.
    """
    return previous.rstrip().endswith("-")


# ---------------------------------------------------------------------------
# Lesevorgang
# ---------------------------------------------------------------------------

def iter_table_rows(pdf) -> Iterator[tuple[int, int, list]]:
    """Alle Tabellenzeilen des Dokuments als (Seite, Tabellenindex, Zeile).

    Getrennt vom Zustandsautomaten, damit dieser mit synthetischen Zeilen
    getestet werden kann und nicht nur gegen ein 168-seitiges PDF.
    """
    for page_number, page in enumerate(pdf.pages, start=1):
        for table_index, table in enumerate(page.extract_tables()):
            for row in table:
                yield page_number, table_index, row


def collect_pi_entries(rows: Iterator[tuple[int, int, list]]) -> PiExtraction:
    """Zustandsautomat ueber die Tabellenzeilen des Dokuments.

    Ablauf (empirisch belegt, siehe Modul-Docstring):

        Kopfzeile -> Spaltenindex fuer DIESE Tabelle
        Ankerzeile 1154/Prüfidentifikator -> Block beginnt
        Zielspalte matcht "44001 GeLi Gas / ..." -> neuer Eintrag
        nur Zielspalte gefuellt -> Fortsetzung des letzten Eintrags
        andere Spalte gefuellt -> Blockende
        Banner- und Kopfzeilen -> ueberspringen, KEIN Blockende

    Der Zustand laeuft ueber Tabellen- und Seitengrenzen hinweg: 44148 beginnt
    auf S.52 und wird auf S.53 fortgesetzt. Nach dem Blockende wird das restliche
    Dokument weiter nach Ankern durchsucht -- ein zweiter Anker waere eine
    Strukturaenderung und fuehrt zu SKIP.
    """
    result = PiExtraction()
    column: int | None = None
    current_table: tuple[int, int] | None = None
    previous_row: list | None = None
    active = False
    finished = False
    last_line = ""

    for page_number, table_index, row in rows:
        # Der Spaltenindex gilt je Tabelle: jede Seite wiederholt die Kopfzeile,
        # und der Index wechselt zwischen den Seiten (8 auf S.51, 6 auf S.52/53).
        if (page_number, table_index) != current_table:
            current_table = (page_number, table_index)
            column = None
            previous_row = None

        header = header_column_index(row)
        if header is not None:
            column = header
            previous_row = row
            continue
        if column is None:
            continue
        if is_page_banner(row):
            previous_row = row
            continue

        cell = _cell(row, column)
        others = [
            value
            for index, value in enumerate(
                c.strip() if isinstance(c, str) else "" for c in row
            )
            if index != column and value
        ]

        if not active:
            if not finished and is_anchor_row(row, column):
                # Zweites Merkmal: die Qualifier-Zeile 1153 muss unmittelbar
                # davor stehen. Ein Anker soll nicht an einer Zelle haengen.
                if previous_row is not None and is_anchor_qualifier_row(previous_row, column):
                    active = True
                    result.anchor_pages.append(page_number)
                    result.anchor_column_index = column
                else:
                    result.form_notes.append(
                        f"S.{page_number}: Ankerzeile 1154/{_ANCHOR_VALUE} ohne vorangehende "
                        f"Qualifier-Zeile {_ANCHOR_QUALIFIER_BEZ}/{_ANCHOR_QUALIFIER_CODE} -- nicht verwendet"
                    )
            elif finished and is_anchor_row(row, column):
                result.anchor_pages.append(page_number)
                result.form_notes.append(
                    f"S.{page_number}: zweiter Anker 1154/{_ANCHOR_VALUE} gefunden -- "
                    "die Dokumentform weicht von der geprüften ab"
                )
            previous_row = row
            continue

        match = _RE_PI_ENTRY.match(cell)
        if match:
            result.entries.append(
                PiEntry(
                    pi_number=match.group(1),
                    process_name=match.group(2).strip(),
                    source_page=page_number,
                )
            )
            last_line = cell
            previous_row = row
            continue

        if cell and not others:
            if not result.entries:
                result.skipped.append(SkippedEntry(
                    reason="Fortsetzungszeile ohne vorangehenden PI-Eintrag",
                    source_page=page_number, raw=cell,
                ))
            elif _looks_hyphenated(last_line):
                # Nicht raten: getrenntes Wort -> Eintrag verwerfen (Abschnitt 14).
                broken = result.entries.pop()
                result.skipped.append(SkippedEntry(
                    reason="Bezeichnung am Zeilenende getrennt -- Zusammenführung nicht eindeutig",
                    source_page=broken.source_page_start,
                    raw=f"{broken.pi_number} {broken.process_name} / {cell}",
                ))
            else:
                entry = result.entries[-1]
                entry.append_line(cell)
                entry.source_page = page_number
            last_line = cell
            previous_row = row
            continue

        if not cell and not others:
            previous_row = row
            continue

        # Andere Spalte gefuellt -> Ende des Blocks. Im Stand G1.1 ist das die
        # Zeile "Bemerkung:"; direkt darunter folgt das EDIFACT-Beispiel
        # "RFF+Z13:44001'", das damit ausserhalb des Blocks liegt und nicht als
        # PI 44001 gelesen wird.
        active = False
        finished = True
        result.block_end_marker = f"S.{page_number} {others[0][:40]!r}"
        previous_row = row

    if result.entries and result.anchor_column_index is not None and len(result.anchor_pages) == 1:
        result.form_recognized = True
    elif not result.anchor_pages:
        result.form_notes.append(
            f"Anker 1154/{_ANCHOR_VALUE} im Dokument nicht gefunden -- SKIP"
        )
    elif len(result.anchor_pages) > 1:
        result.form_notes.append(
            f"Anker 1154/{_ANCHOR_VALUE} mehrfach gefunden ({result.anchor_pages}) -- SKIP"
        )
        result.entries.clear()
    elif not result.entries:
        result.form_notes.append("Anker gefunden, aber kein einziger PI-Eintrag darunter -- SKIP")

    if not result.form_recognized:
        result.entries.clear()
    return result


def extract_pi_entries(pdf_path: str) -> PiExtraction:
    """Formpruefung und Extraktion fuer eine MIG-Datei."""
    file_hash = compute_file_hash(pdf_path)
    document_name = pdf_path.rsplit("/", 1)[-1]
    with pdfplumber.open(pdf_path) as pdf:
        result = collect_pi_entries(iter_table_rows(pdf))
    for entry in result.entries:
        entry.source_document = document_name
        entry.source_document_hash = file_hash
    return result


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_mig_process_identifiers(
    db: Session,
    pdf_path: str,
    regulatory_version_id: int,
) -> PiImportReport:
    """Die PI-Bezeichnungen einer MIG in die Wissensbasis uebernehmen.

    Bewusst OHNE ``reimport``-Schalter: der Lauf ist von sich aus idempotent.
    Ein bestehender ``ProcessIdentifier`` wird nie veraendert -- weder Name noch
    Prozessgruppe -- und ein zweiter Lauf legt nichts Zusaetzliches an.

    Abschnitt 15, Fall C: die Herkunft eines bestehenden ``name`` ist im heutigen
    Schema nicht feststellbar. Ein Unterschied zwischen kuratiertem Namen
    ("Anmeldung Netznutzung") und amtlichem MIG-Rohwert
    ("GeLi Gas / Anmeldung NN") ist deshalb KEIN regulatorischer Konflikt,
    sondern wird nur als ``existing_name_preserved`` ausgewiesen.

    Neue PIs bekommen ausschliesslich, was die MIG belegt: Nummer und
    Bezeichnung. ``process_group_id``, ``sender_role`` und ``receiver_role``
    bleiben leer, ``criticality`` und ``weight`` behalten die Modell-Defaults
    (Freigabe Punkte 2 und 3). Eine Rolle aus "SDÄ Gas / ... NB an LF"
    herauszulesen waere Interpretation, keine Extraktion.
    """
    file_hash = compute_file_hash(pdf_path)
    document_name = pdf_path.rsplit("/", 1)[-1]
    version = db.get(models.RegulatoryVersion, regulatory_version_id)

    report = PiImportReport(
        document=document_name,
        file_hash=file_hash,
        regulatory_version_id=regulatory_version_id,
        regulatory_version_name=version.name if version else "(unbekannt)",
    )
    if version is None:
        report.errors.append(f"RegulatoryVersion {regulatory_version_id} existiert nicht")
        return report

    report.extraction = extract_pi_entries(pdf_path)
    if not report.extraction.form_recognized:
        report.warnings.append(
            "Erwartete Dokumentform nicht eindeutig erkannt -- kein Import (Auftrag Abschnitt 6)"
        )
        return report

    # Doppelte PI-Nummer innerhalb derselben Quelle: nicht eigenstaendig
    # entscheiden, welcher Wert gilt (Abschnitt 14).
    by_number: dict[str, list[PiEntry]] = {}
    for entry in report.extraction.entries:
        by_number.setdefault(entry.pi_number, []).append(entry)

    existing = {pi.pi_number: pi for pi in db.query(models.ProcessIdentifier).all()}

    for pi_number, entries in sorted(by_number.items()):
        names = {e.process_name for e in entries}
        if len(names) > 1:
            report.conflicts.append(
                f"PI {pi_number} kommt in derselben Quelle mit abweichenden Bezeichnungen vor "
                f"({sorted(names)}) -- nicht importiert"
            )
            for e in entries:
                report.extraction.skipped.append(SkippedEntry(
                    reason="mehrdeutige Bezeichnung innerhalb derselben Quelle",
                    source_page=e.source_page_start, raw=f"{e.pi_number} {e.process_name}",
                ))
            continue

        entry = entries[0]
        found = existing.get(pi_number)
        if found is not None:
            report.existing_name_preserved.append((pi_number, found.name, entry.process_name))
            continue

        created = models.ProcessIdentifier(
            pi_number=entry.pi_number,
            name=entry.process_name,
            # Kein Guessing: die MIG belegt weder Prozessgruppe noch Rollen.
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
    "PiEntry",
    "PiExtraction",
    "PiImportReport",
    "SkippedEntry",
    "collect_pi_entries",
    "extract_pi_entries",
    "header_column_index",
    "import_mig_process_identifiers",
    "is_anchor_row",
    "is_anchor_qualifier_row",
    "is_page_banner",
    "iter_table_rows",
    "resolve_active_regulatory_version",
]
