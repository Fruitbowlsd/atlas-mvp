# Etappe 1 — Pilot UTILMD (Strom + Gas)

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 17.09.2026
**Status:** Etappe 1 abgeschlossen. **STOP vor Etappe 2:** Das Provenienzschema und der
Vorschlag zu `RegulatoryVersion` müssen bestätigt werden, bevor auf weitere
Nachrichtentypen skaliert wird.

Artefakte:

* [`etappe1_utilmd_provenienz.json`](etappe1_utilmd_provenienz.json): 4 Datensätze, validiert gegen das Schema
* [`provenienz_schema_v0.json`](provenienz_schema_v0.json): JSON Schema (Draft 2020-12), **zur Bestätigung**
* [`vorschlag_regulatory_state_modell.md`](vorschlag_regulatory_state_modell.md): Abschnitt 9a, **zur Bestätigung**

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| Dokumente vollständig belegt | **4 / 4** (AHB Strom 2.2, MIG Strom S2.2, AHB Gas 1.2, MIG Gas G1.2) |
| erfasste Fassungen | **38** (davon 10 PDF geladen und gehasht, dazu 1 Vorversions-PDF für eine Gegenprobe) |
| offene/unklare Fälle | **1** neu (O-10, ohne Einfluss auf die Auswahl); O-8 aus Etappe 0 **gelöst** |
| Widersprüche BNetzA ↔ BDEW | **0** |

## 2. Ergebnis: Welche Fassung gilt am 01.10.2026?

| Dokument | Version | gültig ab | gültig bis | maßgebliche Fassung | Seiten | SHA-256 (maßgeblich) |
|---|---|---|---|---|---|---|
| UTILMD AHB Strom | **2.2** | 01.10.2026 | offen | konsolidiert, Fehlerkorrekturen **Stand 29.06.2026** (BDEW 8440) | 944 | `7a175760…cf1c8eda3fe4` |
| UTILMD MIG Strom | **S2.2** | 01.10.2026 | offen | konsolidiert, Fehlerkorrekturen **Stand 06.08.2026** (BDEW 8458) | 536 | `9f6dcf92…63af514305` |
| UTILMD AHB Gas | **1.2** | 01.10.2026 | offen | konsolidiert, Fehlerkorrekturen **Stand 06.08.2026** (BDEW 8455) | 293 | `7562e2fd…52ff72c9e802` |
| UTILMD MIG Gas | **G1.2** | 01.10.2026 | offen | konsolidiert, Fehlerkorrekturen **Stand 29.06.2026** (BDEW 8437) | 165 | `8105c2bf…42b6ff874f2acfb5` |

Vollständige Hashes und Belege stehen in der JSON-Datei.

**Begründung, gleiches Muster für alle vier:** Die Version gilt ab 01.10.2026, weil
Mitteilung 56 sie als Anlage „verbindlich ab dem 01.10.2026“ veröffentlicht und bis zum
Stichtag keine verbindliche Nachfolgeversion erschienen ist (nur Mitteilung 57,
Konsultation). Maßgeblich ist die konsolidierte Lesefassung mit dem neuesten
Fehlerkorrekturstand. Sie gibt es nur auf BDEW-MaKo. Der Stand ist dreifach belegt:
BDEW-Titel, sichtbarer Deckblattvermerk und Statusvermerke „Fehler (Datum)“ in der
Änderungshistorie.

**Vorgänger (nicht überschrieben, Abschnitt 10):** AHB Strom 2.1, MIG Strom S2.1, AHB Gas
1.1 und MIG Gas G1.1 gelten bis 30.09.2026. Art `abgeleitet`: Die Gültigkeit des
Nachfolgers beginnt am 01.10.2026, und BDEW führt `validTo 2026-09-30` an allen
Vorgänger-Fassungen. Keine Quelle nennt das Ende ausdrücklich.

## 3. Fragenkatalog Abschnitt 8

| Frage | AHB Strom 2.2 | MIG Strom S2.2 | AHB Gas 1.2 | MIG Gas G1.2 |
|---|---|---|---|---|
| 1 durch M56 geändert? | ja | ja | ja | ja |
| 2 fortgeltende Vorversion? | n/a | n/a | n/a | n/a |
| 3 BDEW gültige Version? | ja, Basis bytegleich | ja, bytegleich | ja, bytegleich | ja, bytegleich |
| 4 Fehlerkorrekturen? | 29.06.2026 | 29.06., 06.08.2026 | 29.06., 06.08.2026 | 29.06.2026 |
| 5 konsolidierte Fassung? | ja | ja | ja | ja |
| 6 neuere, noch nicht gültige Version? | nein | nein | nein | nein |
| 7 Konsultationsfassung? | **ja: 2.3** (M57, für 01.04.2027) | **ja: S2.3** (M57) | nein | nein |
| 8 Widerspruch BNetzA/BDEW? | nein | nein | nein | nein |

## 4. Methodische Befunde aus dem Pilot (gelten für alle weiteren Etappen)

1. **Das BNetzA-PDF und das BDEW-Basis-PDF sind bytegleich** (4/4, identischer SHA-256).
   Die BNetzA-Anlage ist also keine eigene Fassung, sondern dieselbe Datei.
2. **Die maßgebliche Fassung liegt nie bei der BNetzA**, sobald es Fehlerkorrekturen gibt.
3. **Die konsolidierte Fassung ersetzt nicht alles.** Ihre Änderungshistorie enthält nur die
   Fehlerkorrekturen der eigenen Version, kumuliert (Status „Fehler (29.06.2026)“, „Fehler
   (06.08.2026)“). Die fachlichen Änderungen gegenüber dem Vorgänger (Status „Genehmigt“,
   z. B. 218 Statusvermerke „Genehmigt“ bei AHB Strom 2.2) stehen **nur in der Basisfassung**. Die Basisfassung
   wird deshalb als `ergaenzend` geführt, nicht verworfen. Das ist relevant für Abschnitt 12
   („Änderungshistorie“).
4. **Seiten- und Kapitelnummern sind fassungsgebunden.** AHB Gas 1.2 nummeriert in der
   konsolidierten Fassung Kapitel um (5.13.x → 5.12.x). AHB Strom 2.2 schrumpft von 1.397 auf
   944 Seiten, bei gleichem Inhalt (189 Prüfidentifikatoren) und mehr Text ohne Historie.
   Eine Provenienz „Kapitel/Seite“ ist nur zusammen mit dem SHA-256 gültig.
   `MessageDefinition.quelle_hash` ist dafür schon richtig angelegt.
5. **Fehlerkorrekturen ändern den Umfang.** Durch die Korrektur vom 29.06.2026 kommt in Gas
   der Prüfidentifikator **44170** (Ablehnung Verpflichtungsanfrage, WiM Gas) hinzu: AHB 88 →
   89, MIG 91 → 92. Ein Import aus der Basisfassung hätte ihn verloren.
6. **O-8 gelöst, die BDEW-Metadaten sind jetzt deutbar.** Ein ersetzter Fehlerkorrekturstand
   hat `validTo` = Tag vor dem nächsten Stand (2 von 2 Fällen: AHB Gas, MIG Strom, jeweils
   2026-08-05). Die Basisfassung behält `validTo = offen`. XML-Basisdateien haben
   `validTo 2026-06-28` vor `validFrom` (zurückgezogen, sobald die konsolidierte XML
   erschien). Die Regel zur Fassungswahl stützt sich deshalb auf Titel, Deckblatt und
   Historie, nie auf die Kennzeichenfelder. `validTo` dient nur als Gegenprobe.
7. **Parallele Fehlerkorrekturen der Vorversion sind nachgezogen.** Die Korrekturen an AHB
   Strom 2.1 vom 29.06.2026 (Änd-IDs 27368, 27376) stehen auch in der Fehlerkorrektur-Historie
   von 2.2.
8. **Die Vollständigkeit wird geprüft, nicht angenommen.** Ob die konsolidierte Fassung
   vollständig ist, wurde je Dokument gegen die Basis geprüft: Seitenzahl, Inhaltsverzeichnis,
   Menge der Prüfidentifikatoren. Die unterschiedlichen Dateigrößen (AHB Gas Stand 06.08.:
   3,7 MB statt 10,8 MB) kommen von der Kompression, die Seitenzahl ist identisch.

## 5. Abweichende Termine und Einführungsszenario

* **Keine abweichende Gültigkeit** einer der vier Versionen.
* **Strom:** Mitteilung 56 enthält einen Sonderhinweis zu § 10b EEG (Z24, ZW5/ZW6). Dazu gibt
  es die BDEW-Anwendungshilfe „Einführungsszenario … zum 1. Oktober 2026 in der UTILMD“,
  **Version 1.1 vom 18.08.2026** (ersetzt 1.0 vom 29.06.2026), SHA-256 `de168bf0…61cbaa`.
  Sie regelt operative Migrationsschritte: NB-Frist **18.09.2026** für Verbrauchsarten/TR,
  Übermittlung der Fernsteuerbarkeit ab 01.10.2026 per PID 55693/55694 (empfohlen bis
  03.10.2026), Vergütungsverpflichtung per PID 55617. Das sind Hinweise, keine
  Versionsfrage.
* **Gas:** Laut Vorwort betrifft das Einführungsszenario „ausschließlich die Sparte Strom“.

## 6. Neue offene Fälle

| ID | Fall | Bearbeitung |
|---|---|---|
| **O-10** | MIG Gas G1.2, Basis, Änderungshistorie S. 168: Vermerk, eine Anpassung zu Übergangsversorgung (§ 38a EnWG, ZZD) finde „erst zum 1.4.2026 Anwendung“. Das Datum liegt vor dem Stichtag, der Vermerk ist vermutlich aus G1.1 übernommen. Die Zuordnung zur Änd-ID ist wegen des Spaltenlayouts nicht sicher belegt. Kein Einfluss auf die Auswahl. | fachliche Analyse (Abschnitt 12) |

O-6 (GeLi Gas 3.0) bleibt für Etappe 3 offen: Der UTILMD-Gas-Pilot hat keinen Hinweis auf
einen abweichenden Termin gefunden, die Festlegung selbst ist aber nicht gelesen.

## 7. Provenienzschema v0 — Abdeckung von Abschnitt 11 (zur Bestätigung)

| Anforderung | Schema-Pfad |
|---|---|
| Quelle | `fassungen[].quelle`, `fassungen[].quelle_ref` |
| URL | `fassungen[].url`, `dokumentversion.mitteilung.url` |
| Dokumentname | `dokument.dokumentname`, `fassungen[].titel_in_quelle` |
| Dokumentversion | `dokumentversion.version` |
| Veröffentlichungsdatum | `dokumentversion.veroeffentlicht_am` (Datum + Art + Belege) |
| Gültig ab | `dokumentversion.gueltig_ab` (Datum + Art + Belege) |
| Gültig bis | `dokumentversion.gueltig_bis` (Datum/null + Art `ausdruecklich`/`abgeleitet`/`offen` + Belege) |
| Mitteilung | `dokumentversion.mitteilung` (Nr., URL, Typ, Datum, Zusammenhang) |
| PDF-Datei | `fassungen[]` mit `dateityp`, `dateiname`, `seiten`, `deckblatt`, `aenderungshistorie` |
| Hash der Datei | `fassungen[].sha256`, `fassungen[].bytegleich_mit`, `auswahl.massgebliche_fassung_pdf_sha256` |
| Analysezeitpunkt | `analyse.analysezeitpunkt_utc`, `fassungen[].abruf_utc`, `analyse.bdew_api_abzug_sha256` |
| Fehlerkorrekturstand | `fassungen[].fehlerkorrekturstand` |
| Prioritätsentscheidung | `fassungen[].rolle` (`massgeblich` / `ergaenzend` / `ersetzt` / `informativ` / `nicht_verbindlich`), `auswahl.regelschritte[]` |
| Begründung | `auswahl.begruendung`, `fassungen[].rolle_begruendung` |
| *zusätzlich* 4A: Dokumenttyp, Nachrichtentyp, Sparte, Dateityp, Dokumentstatus, Vorgängerversion | `dokument.*`, `dokumentversion.dokumentstatus`, `dokumentversion.vorgaenger` |
| *zusätzlich* 8: Fragen 1–8 | `fragenkatalog.f1…f8` (Antwort + Belege) |
| *zusätzlich* 14: Maßgebliche Fassung, Auswahlbegründung | `auswahl.massgebliche_fassung_id`, `auswahl.begruendung` |
| *zusätzlich* Beobachtungen ohne Auswahlwirkung | `hinweise[]` |

**Entscheidungen im Schema, die ich bestätigt haben möchte:**

1. **Drei Ebenen** Dokument → Dokumentversion → Fassung. Die Fassung ist die Datei mit
   SHA-256, nicht die Version.
2. **Jede Fassung wird erfasst**, auch informatorische, ersetzte, kostenpflichtige (nicht
   abgerufen, mit Grund) und Konsultationsfassungen. Die Auswahl setzt nur eine `rolle`,
   nichts wird entfernt.
3. **Daten sind belegte Objekte**, kein nacktes Datum. „Gültig bis“ unterscheidet
   `ausdruecklich` / `abgeleitet` / `offen`.
4. **Die Basisfassung ist `ergaenzend`**, nicht `ersetzt`, weil sie die einzige Quelle der
   Änderungshistorie gegenüber dem Vorgänger ist.
5. **BDEW-Rohwerte** (`validFrom`/`validTo`) werden ungedeutet mitgeführt, die Deutung steht
   in `hinweise`.

**Ticket:** #64
