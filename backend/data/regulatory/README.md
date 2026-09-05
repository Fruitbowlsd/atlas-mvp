# Regulatorische Quelldokumente

Die PDF-Dateien selbst liegen **nicht** im Repository (mehrere MB je Datei, siehe
`.gitignore`). Sie werden aus der offiziellen Quelle bezogen; der SHA-256 jeder
importierten Datei steht in `message_definitions.quelle_hash` und macht den
Dokumentstand nachvollziehbar.

## UTILMD Anwendungshandbuch Gas 1.1

| | |
|---|---|
| Dateiname | `UTILMD_AHB_Gas_1_1_20251001.pdf` |
| Version | 1.1, Stand MIG G1.1 |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 |
| Seiten | 329 |
| SHA-256 | `b8950fb45134dd0927c95e5b8f5f0bd98ce59bb2fc7911c5105f552d18c96ae0` |

Bezug:

```bash
curl -L -o backend/data/regulatory/UTILMD_AHB_Gas_1_1_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/UTILMD_AHB_Gas_1_1_20251001.pdf?__blob=publicationFile&v=1"
```

Uebersichtsseite der Mitteilung Nr. 54:
<https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Mitteilung_Nr_54.html>

> Hinweis: Das Deckblatt der Datei traegt die Aufschrift "Konsultationsfassung".
> Das ist der von der BNetzA unter Mitteilung Nr. 54 veroeffentlichte Stand; die
> Mitteilung selbst weist die Fassung als ab 01.04.2026 anzuwenden aus.

## UTILMD Nachrichtenbeschreibung (MIG) Gas G1.1

| | |
|---|---|
| Dateiname | `UTILMD_MIG_Gas_G1_1_20251001.pdf` |
| Version | G1.1 |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 |
| Seiten | 168 |
| SHA-256 | `f5191a473b650dd6e5de2a673f97b6db685f57de8f6b8d2da7d6ccebb2bfe634` |

Bezug:

```bash
curl -L -o backend/data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/UTILMD_MIG_Gas_G1_1_20251001.pdf?__blob=publicationFile&v=1"
```

> Anders als das AHB traegt diese Datei **keinen** Konsultationsvermerk -- es ist
> die finale, unter Mitteilung Nr. 54 veroeffentlichte Fassung.

Genutzt wird daraus die amtliche Zuordnung Pruefidentifikator -> Prozessbezeichnung
(Segmentlayout, SG6/RFF, Datenelement 1154, S. 51-53; 91 Eintraege). Struktur-
befund und Parserform siehe Issue #46.


## Codeliste der OBIS-Kennzahlen und Medien

| | |
|---|---|
| Dateiname | `Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf` |
| Version | 2.5c |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 (Autor laut PDF-Metadaten: BDEW) |
| Seiten | 46 |
| SHA-256 | `bc43ff890fde3d02203e72b67e10bfeb966c53791d85246067c54c45a67c8aef` |

Bezug:

```bash
curl -L -o backend/data/regulatory/Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/Codeliste-OBIS-Kennzahlen_Medien_2_5c_20251001.pdf?__blob=publicationFile&v=1"
```

> Die Uebersichtsseite der Mitteilung Nr. 54 verlinkt diese Anlage relativ, also
> auf derselben Domain wie AHB und MIG. Eine zusaetzlich kursierende URL unter
> `dsc.bund.de` wird **nicht** verwendet -- sie ist nicht noetig, der direkte
> Abruf oben liefert HTTP 200 ohne Redirect.

Das Dokument enthaelt **zehn** strukturell verschiedene Tabellenformen. Importiert
werden die sieben, die tatsaechlich Wertelisten sind; sie verteilen sich auf die
Kapitel 2.2, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5 und 5 (zwei Formen kommen je
zweimal vor, einmal fuer Strom und einmal fuer Gas). Ergebnis: 12 `CodeList`-
Eintraege mit 224 `CodeListEntry`.

Bewusst NICHT importiert:

* **Kapitel 3.3.x / 4.6.x** (Messprodukt-Code -> zulaessige OBIS-Kennzahlen):
  eine Zuordnungstabelle mit Bedingungen, keine Werteliste. Zurueckgestellt als
  eigenes Wissensobjekt.
* **Kapitel 3.3.4** (Korrekturenergiemenge): Merkmalskombination -> OBIS.
* **Kapitel 7** (Aenderungshistorie): Dokumentationstabelle. Sie zitiert 14
  OBIS-Kennzahlen und 4 Messprodukt-Codes frueherer Staende, teils inzwischen
  geloescht -- expliziter Nicht-Datenbereich, per Regressionstest abgesichert.

Strukturbefund und Formspezifikationen siehe Issue #48.

## Entscheidungsbaum-Diagramme und Codelisten fuer die Antwortnachrichten

| | |
|---|---|
| Dateiname | `EBD_und_Codelisten_4_2_20251001.pdf` |
| Version | 4.2 |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 (Autor laut PDF-Metadaten: BDEW) |
| Seiten | 851 |
| SHA-256 | `11c3f77b738a4e0e0f743ddc907f82ab01ceb9d1835da4a0b9ce181ae418f8eb` |

Bezug:

```bash
curl -L -o backend/data/regulatory/EBD_und_Codelisten_4_2_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/EBD_und_Codelisten_4_2_20251001.pdf?__blob=publicationFile&v=1"
```

> **Zur Version 4.2 gegen 4.3.** Kursierend ist eine gleichnamige Fassung
> **4.3, Stand 01.04.2026** unter `bdew-mako.de`. Sie wird **nicht** verwendet:
> die Uebersichtsseite der Mitteilung Nr. 54 verlinkt die **4.2**, und die
> Mitteilung ist die amtliche Quelle. Die 4.2 traegt zudem dasselbe
> Publikationsdatum wie AHB 1.1, MIG G1.1 und die OBIS-Codeliste 2.5c --
> ein Mischstand aus vier Dokumenten mit verschiedenen Publikationsdaten waere
> fachlich nicht vertretbar. Deckblatt und PDF-Metadaten der geladenen Datei
> weisen sie in sich selbst als 4.2 aus.

Das Dokument enthaelt zwei fachlich verschiedene Bestandteile. Importiert wird
**nur der Codelisten-Teil**:

* **Codelisten** -- 127 Abschnitte mit den Praefixen `S_` (Strom, 36), `G_`
  (Gas, 89) und `GS_` (beide, 2). Davon 125 importiert: 388 `CodeListEntry` in
  125 `CodeList`, ueber alle Prozessfamilien hinweg (GPKE, WiM Strom, MaBiS,
  GeLi Gas, WiM Gas, Mehr-/Mindermengen, Herkunftsnachweisregister,
  Netzbetreiberwechsel, Kapazitaetsabrechnung) -- keine Filterung nach Sparte.
* **Entscheidungsbaum-Diagramme (EBD)** -- 346 Abschnitte `E_XXXX_` auf den
  Seiten 28-835, davon 240 Seiten mit EBD-Tabelle. **Bewusst ausgeklammert**:
  weder als Bild extrahiert noch in eine Tabellenstruktur gepresst. Eine
  spaetere Erfassung der Entscheidungsbaum-Logik ist eine eigenstaendige
  Aufgabe und hier nicht vorbereitet.

Die Unterscheidung ist rein strukturell und noetig, weil **beide** Tabellenarten
eine Spalte `Code` mit gleich aussehenden Werten fuehren (`A01`, `Z07`): die
Codeliste hat laut Kapitel 5 die Spalten `Code`/`Nutzung`/`Name` (optional
`Bedingung`), die EBD-Tabelle laut Kapitel 4 `Nr.`/`Prüfschritt`/
`Prüfergebnis`/`Code`/`Hinweis`. Eine Volltextsuche nach Codes wuerde zwingend
Prueflogik-Codes einsammeln.

Bewusst NICHT importiert:

* **`S_0109_Nichtzahlungsavis prüfen`** (Abschnitt 6.10.4, S. 158): fuehrt zwei
  fachlich unterschiedliche Bedingungsspalten je Code (eine fuer Codes aus
  `S_0103`, eine fuer Codes aus dem EBD `E_0406`). `CodeListEntry` hat dafuer
  ein Feld; ein Import wuerde die Zuordnung "welche Bedingung gilt wann"
  vernichten. Zurueckgestellt statt verfaelscht -- eigener Modellierungsschritt.
* **`G_0088 Stornierung prüfen`** (Abschnitt 15.1.2.2): enthaelt keine Tabelle,
  sondern den Querverweis "Es ist die Codeliste G_0079 zu nutzen."
* **Kapitel 19** (Aenderungshistorie, ab S. 836): Nicht-Datenbereich.
* **`Code A99`/"Antwortgrund Sonstiges"** und die Datenstatus-Codes eines BIKO
  (`A01`-`A04`, `A06`): stehen in Kapitel 3 als Fliesstext, nicht als Tabelle.
  Es sind Festlegungen *ueber* Codes, keine Codelisteneintraege.

> **Keine globale Deduplizierung ueber den Codewert.** Die 388 Eintraege
> verteilen sich auf nur 82 verschiedene Codewerte. `Z07` heisst in `S_0103`
> "Netznutzungsmesswerte / -energiemengen fehlen" und in `G_0060` "Ablehnung
> (Keine Berechtigung)". Das Dokument sagt es in Kapitel 3 selbst: "Die
> Antwortcodes haben eine unterschiedliche Bedeutung je EBD." Die fachliche
> Identitaet eines Antwortcodes entsteht erst aus RegulatoryVersion + CodeList
> + Code; zusammengefuehrt wird ausschliesslich innerhalb einer `CodeList`.

Strukturbefund, Formspezifikationen und Wiederverwendungsbilanz siehe Issue #50.

## Anwendungsuebersicht der Pruefidentifikatoren (PID)

| | |
|---|---|
| Dateiname | `PID_3_3_Konsultationsfassung_20250801.pdf` |
| Version | 3.3 (Konsultationsfassung) |
| Publikationsdatum | 01.08.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 (Datei liegt als Anlage unter Mitteilung Nr. 52; Autor laut PDF-Metadaten: BDEW) |
| Seiten | 82 |
| SHA-256 | `6b4f5e362703d481a4e362f19abd43c197dc5d1b1643750b4a59cb92d9c7139a` |

Bezug:

```bash
curl -L -o backend/data/regulatory/PID_3_3_Konsultationsfassung_20250801.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_52/Anlagen/PID_3_3_Konsultationsfassung_20250801.pdf?__blob=publicationFile&v=1"
```

> Wie beim AHB Gas 1.1 und der MIG Gas G1.1 traegt die Datei den Vermerk
> "Konsultationsfassung". Die Uebersichtsseite der Mitteilung Nr. 54 fuehrt
> "Anwendungsuebersicht der Pruefidentifikatoren 3.3" unter den EDIFACT-Dokumenten
> und weist die Fassung als ab 01.04.2026 anzuwenden aus. Version und Datum sind
> im Dokument selbst doppelt belegt: Deckblatt (S. 1) und Fusszeile aller 82 Seiten.

Das Dokument besteht laut eigenem Inhaltsverzeichnis aus **fuenf** Tabellen; die
empirische Pruefung bestaetigt genau diese fuenf:

| # | Tabellenkonzept | Seiten | Spalten | Datenzeilen |
|---|---|---|---|---|
| 1 | Pruefidentifikator zu Prozessschritt / API Webservice zu Prozessschritt | 7-77 | 21 | 1370 |
| 2 | Tupel-Uebersicht | 78-79 | 5 | 68 |
| 3 | Objekteigenschaften | 80 | 4 | 11 |
| 4 | Erweiterte Zuordnungslogik | 81 | 3 | 9 |
| 5 | Aenderungshistorie | 82 | 6 | 5 |

Tabelle 1 enthaelt 486 verschiedene Pruefidentifikatoren -- 88 davon kennt Atlas
bereits aus der MIG (Prompt 1), 398 waeren neu. Anders als MIG und AHB liefert
`extract_tables()` hier saubere Zellen: alle 1370 Zeilen haben exakt 21 Zellen,
mehrzeilige Inhalte kommen als `\n` **innerhalb** der Zelle an, und keine Zeile
laeuft ueber einen Seitenumbruch.

### Was importiert wird (Freigabe Scoping A)

Uebernommen wird **ausschliesslich** das Paar Pruefidentifikator -> Bezeichnung aus
Tabelle 1: 397 neue `ProcessIdentifier` (486 verschiedene PIs, davon 88 bereits aus
der MIG bekannt und unveraendert gelassen, 1 wegen zweier Schreibweisen in derselben
Quelle nicht importiert). Bestand danach: 91 -> 488.

Neue PIs bekommen, was die PID je PI eindeutig belegt: Nummer, Bezeichnung und
**Nachrichtentyp**. `sender_role`/`receiver_role` bleiben leer, obwohl die PID
"Kommunikation von/an" fuehrt -- diese Angaben haengen am Prozessschritt und nicht
am PI (113 bzw. 142 von 486 PIs haben mehrere verschiedene Werte).

### Nachrichtentyp: alle Formate, nicht nur UTILMD

Der Modell-Default von `ProcessIdentifier.message_type` ist "UTILMD" und waere fuer
die meisten der 397 neuen PIs falsch. Die PID fuehrt **16 verschiedene
Nachrichtentypen**:

| Typ | PI | Typ | PI | Typ | PI | Typ | PI |
|---|---|---|---|---|---|---|---|
| UTILMD | 277 | IFTSTA | 35 | INSRPT | 8 | REMADV | 4 |
| ORDERS | 46 | MSCONS | 25 | UTILTS | 8 | PRICAT | 3 |
| ORDRSP | 40 | PARTIN | 14 | QUOTES | 5 | ORDCHG | 3 |
| | | INVOIC | 11 | REQOTE | 5 | COMDIS | 2 |
| | | | | | | SSQNOT | 2 |

Der Typ wird aus der AHB-Spalte entnommen: sie nennt das Anwendungshandbuch, dessen
Name mit dem EDIFACT-Nachrichtentyp beginnt ("MSCONS AHB", "UTILMD AHB Strom",
"SSQNOT zur Uebermittlung von Mehr-/Mindermengen"). Das ist eine strukturelle
Entnahme der fuehrenden sechs Grossbuchstaben, keine Interpretation, und je PI
widerspruchsfrei (0 von 486 PIs mit mehreren AHB-Werten). Gegen die 88 bereits
bekannten PIs gibt es **0 Widersprueche** -- die PID bestaetigt, was Atlas fuehrt.
Bewusst ohne Positivliste der Typen, damit ein in einer kuenftigen Version neu
hinzukommendes Format uebernommen wird, ohne den Parser zu pflegen; der Importreport
fuehrt jeden abgeleiteten Typ mit Anzahl auf, ein neuer faellt dort auf. Laesst sich
kein Typ entnehmen, bleibt das Feld leer statt geraten (im Stand 3.3: kein Fall).

Die **Sparte** aus "UTILMD AHB Strom"/"... Gas" wandert NICHT mit -- sie steht in
eigenen Spalten und gehoert zum zurueckgestellten Prozessschritt-Konzept.

**Die PID-Bezeichnung ueberschreibt nie einen bestehenden Namen.** Sie ist ohne ihre
Nachbarspalten nicht eindeutig: 44147 und 44148 tragen beide "Anfrage an MSB mit
Abhaengigkeiten" und werden erst durch "Kommunikation von/an" unterschieden, waehrend
die MIG die Rollenrichtung in den Namen einbaut. Alle 88 gemeinsamen PIs weichen im
String ab (43 nur durch das Prozessfamilien-Praefix der MIG, 45 im Wortlaut); die
Abweichungen stehen im Importreport, nicht in der Datenbank.

### Bewusst NICHT importiert (zurueckgestellt, eigene Modelle noetig)

* **Prozessschritt-Zuordnung** (Spalten 5-11) und **Reaktionsbeziehung** (Spalte 4)
* **Tupel-Uebersicht** (Tabelle 2) -- nicht verlustfrei in `CodeList`/`CodeListEntry`
  abbildbar, die Segmentangabe (`ZO-T1 = SG5 LOC DE3225`) haette dort kein Feld
* **Objekteigenschaften** (Tabelle 3) und **Erweiterte Zuordnungslogik** (Tabelle 4)
* **Zuordnungslogik** (Spalten 12-15), **Uebertragungsweg**/**API-Kennung**,
  **Sparte**, **API-Webservices** (27 Zeilen ohne PI)
* **Aenderungshistorie** (Tabelle 5) -- Delta-Engine, eigene Aufgabe

Der Importreport fuehrt dafuer eine **Verlustbilanz je Spalte**: was gelesen wurde,
was uebernommen wurde und was fuer eine spaetere Modellierung vorgemerkt ist. Kein
PID-Feld geht stillschweigend verloren.

Zwei Verweise sind im Dokument selbst nicht aufloesbar und werden ausgewiesen statt
geraten: `ZG-T33` (neunmal verwendet, in der Tupel-Uebersicht nicht definiert) und
PI `44108` als Reaktionsziel ohne eigenen Anwendungsfall. Dazu 42 Zuordnungszellen
mit Bedingungsfreitext statt eines Codes.

Strukturbefund, Beziehungsketten und Modellvorschlaege siehe
`docs/befund_pid_uebersicht.md` und Issue #54.

## Import

```bash
cd backend && ./venv/bin/python -m app.import_ahb --help
cd backend && ./venv/bin/python -m app.import_mig --help
cd backend && ./venv/bin/python -m app.import_obis --help
cd backend && ./venv/bin/python -m app.import_ebd --help
cd backend && ./venv/bin/python -m app.import_pid --help
```

Alle fuenf Importe sind idempotent. Beim AHB wird derselbe Dateihash beim zweiten Lauf
erkannt und sauber uebersprungen (`--reimport` erzwingt einen kontrollierten
Neuaufbau). Der MIG-Import veraendert einen bestehenden `ProcessIdentifier`
grundsaetzlich nicht und braucht deshalb keinen Schalter. Der OBIS-Import
erkennt denselben Dateihash und ueberspringt ihn; `--reimport` erzwingt einen
kontrollierten Neuaufbau. Der EBD-Import verhaelt sich wie der OBIS-Import. Der PID-Import veraendert -- wie
der MIG-Import -- einen bestehenden `ProcessIdentifier` grundsaetzlich nicht und
braucht deshalb keinen Schalter. Sein optionaler Schalter `--mig` schaltet den
Konsistenzabgleich mit den MIG-PI-Namen aus Prompt 1 zu (Default: an).

## Tests

Die Tests in `backend/tests/` ueberspringen sich selbst, wenn die jeweilige
PDF-Datei nicht vorliegt. Abweichende Ablageorte lassen sich ueber die
Umgebungsvariablen `ATLAS_AHB_GAS_11_PDF`, `ATLAS_MIG_GAS_G11_PDF`,
`ATLAS_OBIS_CODELISTE_PDF`, `ATLAS_EBD_CODELISTEN_PDF` und
`ATLAS_PID_UEBERSICHT_PDF` setzen.
