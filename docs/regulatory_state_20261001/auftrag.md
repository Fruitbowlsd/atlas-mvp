<!-- Repo-Notiz (nicht Teil des Auftragstexts): Wortlaut des Claude-Projektdokuments,
     Fassung vom 18.09.2026 (Stand nach Etappe 5), an diesem Tag in die Arbeitssitzung
     übergeben und hier unverändert abgelegt. Ersetzt die Fassung vom 18.09.2026 (vor Etappe 4). Abweichungen zwischen
     dieser Referenz und dem Stand im Repo sind in Ticket #64 vermerkt. -->

# Claude Code Auftrag: Regulatorischer Stand der Marktkommunikation zum 01.10.2026

**Verhältnis zu anderen Projektdokumenten:** Dieser Auftrag ist eigenständig und ersetzt nicht `Claude_Code_Prompt_FINAL.md`. Jener Auftrag beschreibt eine engere, weiterhin gültige Teilaufgabe (kapitelweiser Import von AHB Gas 1.1 in die bestehenden, aktuell leeren Wissensbasis-Tabellen). Der vorliegende Auftrag liegt davor: Er soll zunächst den vollständigen, belastbaren regulatorischen Stand zum Stichtag 01.10.2026 als Recherche-Grundlage ermitteln, bevor auf dieser Basis weiter fachlich extrahiert wird (vgl. Abschnitt 12/13 unten). Erstellt: 2026-09-17, ergänzt um Etappenplan: 2026-09-17, ergänzt um Ticket-Pflicht: 2026-09-17, ergänzt um Pilot-Entscheidungen (Etappe 0/1): 2026-09-17, ergänzt um Etappe-2-Ergebnisse: 2026-09-17, ergänzt um Etappe-3-Ergebnisse: 2026-09-17, ergänzt um Aufnahmeregel und Mitteilung-57-Klärung: 2026-09-18, ergänzt um Etappe-4-Ergebnisse und Korrekturen (9b, Schema-Version, Kriterium C): 2026-09-18, ergänzt um Etappe-5-Ergebnisse (EBD/Codelisten, O-16 aufgelöst, O-17): 2026-09-18.

**Hinweis zur Synchronität:** Claude Code hat diese Fassung übernommen (bestätigt 2026-09-18) und zwei Abweichungen gemeldet, die eingearbeitet sind: die Rolle `verworfen` (siehe 11a) und ein Datumsfehler in 9b. Seither ergänzt um die Etappe-4- und Etappe-5-Ergebnisse (Anhang), eine Präzisierung von Kriterium C (11e), einen neuen Abschnitt 11f (EBD-Querprüfung) sowie die offenen Punkte O-15/O-16/O-17. Bitte bei Gelegenheit erneut mit `auftrag.md` im Repo abgleichen.

---

## Rolle

Du arbeitest wie ein sehr erfahrener Projektleiter für Marktprozesse bei einem deutschen Energieversorgungsunternehmen.

Deine Aufgabe ist es, für Atlas einen vollständigen, belastbaren und nachvollziehbaren regulatorischen Stand der Marktkommunikation zu ermitteln und strukturiert abzubilden.

Das Ziel ist nicht, lediglich die in einer BNetzA-Mitteilung verlinkten Dokumente herunterzuladen.

Das Ziel ist: Für einen eindeutig definierten regulatorischen Stichtag muss Atlas wissen, welche regulatorischen Dokumente und Versionen tatsächlich gültig sind, welche Dokumente zusammengehören, welche Fehlerkorrekturen bzw. konsolidierten Fassungen Vorrang haben und welche fachlichen Informationen daraus für Atlas relevant sind.

Jede Aussage muss auf einer konkreten Quelle und Dokumentversion nachvollziehbar sein.

---

## 0. Vorbereitung: Ticket anlegen

Bevor mit Etappe 0 des Anhangs begonnen wird: Lege im Repo ein neues Ticket/Issue für diesen gesamten Auftrag an (`gh issue create`, analog zum Workflow aus `Claude_Code_Prompt_FINAL.md`, Abschnitt 18), z.B. mit dem Titel "Regulatory State 01.10.2026: vollständigen regulatorischen Stand ermitteln". Übernimm den Etappenplan aus dem Anhang als Checkliste in die Issue-Beschreibung.

Arbeite während des gesamten Auftrags mit diesem einen Ticket: Nach jeder Etappe (siehe Abschnitt 13a und Anhang) den entsprechenden Checklisten-Punkt abhaken und den geforderten Zwischenstand als Kommentar im Ticket festhalten — nicht nur im Chat-Verlauf. Für die eigentliche Recherchearbeit einen eigenen Branch verwenden (z.B. `feature/regulatory-state-2026-10-01`); ob pro Etappe oder für den gesamten Auftrag ein PR erstellt wird, entscheidet sich danach, ob zwischendurch bereits committbare Artefakte (siehe Abschnitt 15a) entstehen. Das Ticket bleibt in jedem Fall die verbindliche, fortlaufende Quelle für den Bearbeitungsstand über mehrere Sessions hinweg — nicht der Chatverlauf, der zwischen Sessions verloren gehen kann.

Verweise am Ende jedes Etappenberichts auf die Ticketnummer, damit der Zusammenhang nachvollziehbar bleibt. Aktuelles Ticket: **#64**, aktueller PR: **#65**.

---

## 1. Grundverständnis der Formatumstellungen

Die reguläre Marktkommunikation kennt grundsätzlich zwei Umsetzungstermine pro Jahr:

* 01.04.
* 01.10.

Das Änderungsmanagement folgt dabei grundsätzlich diesem Muster:

**Formatumstellung zum 01.10.**
Die Konsultation erfolgt typischerweise 6 Monate vor dem Stichtag. Die verbindliche Veröffentlichung erfolgt zum 01.04.

Beispiel:
* Mitteilung 55: Konsultation für Umsetzungstermin 01.10.2026 — Veröffentlichung: 02.02.2026
* Mitteilung 56: verbindlicher Stand für Umsetzungstermin 01.10.2026 — Veröffentlichung: 01.04.2026 — Inkrafttreten: 01.10.2026

**Formatumstellung zum 01.04.**
Die Konsultation erfolgt typischerweise im August. Die verbindliche Veröffentlichung erfolgt zum 01.10. des Vorjahres.

Beispiel:
* Mitteilung 52: Konsultation für Umsetzungstermin 01.04.2026 — Veröffentlichung: 01.08.2025
* Mitteilung 54: verbindlicher Stand — Veröffentlichung: 01.10.2025 — Inkrafttreten: 01.04.2026

Diese Logik ist nicht nur textuell zu beschreiben, sondern muss als zeitliche Beziehung zwischen Konsultation, Veröffentlichung und Inkrafttreten in Atlas nachvollziehbar sein.

---

## 2. Ausgangspunkt: BNetzA

Beginne bei der Bundesnetzagentur: https://www.bundesnetzagentur.de/

Navigiere zu: Beschlusskammern → Beschlusskammer 6 → Aktuelles / Mitteilungen zu Datenformaten zur Abwicklung der Marktkommunikation.

**Prüfe eigenständig, ob für die Sparte Gas neben Beschlusskammer 6 auch Beschlusskammer 7 relevante Mitteilungen zu Datenformaten der Marktkommunikation veröffentlicht, oder ob Formatmitteilungen für Strom und Gas ausschließlich gemeinsam über Beschlusskammer 6 laufen und Beschlusskammer 7 andere Themen (z.B. Netzzugang Gas) behandelt. Nimm keine der beiden Möglichkeiten ungeprüft an und dokumentiere, welche Kammer(n) tatsächlich als Quelle herangezogen wurden und warum.**

Ermittle zunächst den relevanten Umsetzungstermin. Für den aktuellen Fall:

Regulatorischer Zielstand: 01.10.2026
Die dazugehörige verbindliche Mitteilung ist: Mitteilung Nr. 56
Veröffentlichung: 01.04.2026

**Mitteilung 56 wird hier als bekannter Ausgangspunkt vorgegeben, weil sie bereits an anderer Stelle im Projekt verifiziert wurde. Das entbindet nicht davon, sie eigenständig gegenzuprüfen: Bestätige über die BNetzA-Seite selbst, dass Mitteilung 56 tatsächlich die aktuell gültige, verbindliche Mitteilung für den Umsetzungstermin 01.10.2026 ist, und prüfe, ob zwischenzeitlich eine neuere Mitteilung (z.B. eine Korrektur oder Mitteilung 57) veröffentlicht wurde, die Mitteilung 56 ganz oder teilweise ersetzt oder ergänzt. Melde explizit, falls das der Fall ist, statt stillschweigend bei Mitteilung 56 zu bleiben.**

Nicht automatisch davon ausgehen, dass Mitteilung 56 alleine den vollständigen regulatorischen Stand enthält.

**Klärung (bestätigt 2026-09-18, aus Etappe 3):** Mitteilung 57 ist veröffentlicht (31.07.2026), enthält aber ausschließlich Konsultationsfassungen für den Umsetzungstermin 01.04.2027. Sie ersetzt oder ergänzt Mitteilung 56 nicht. Für den Stichtag 01.10.2026 existiert keine veröffentlichte, aber noch nicht gültige verbindliche Version — weder bei BDEW (kein Eintrag mit Gültigkeit nach dem 01.10.2026) noch bei BNetzA (keine Inkrafttretens-Mitteilung nach Nr. 56). Diese Aussage steht wörtlich in der Antwort auf Frage 6 aus Abschnitt 8 in allen bisherigen Datensätzen; die Konsultationsfassungen aus Mitteilung 57 laufen unter Frage 7.

---

## 3. Mitteilung vollständig analysieren

Lade die vollständige Mitteilung herunter und analysiere:

* Titel, Nummer, Veröffentlichungsdatum
* Umsetzungstermin / Inkrafttreten
* betroffene Sparten, betroffene Prozesse
* EDIFACT-Dokumente, Entscheidungsbaum-Diagramme, Codelisten
* Regelungen zum Übertragungsweg, AS4-Dokumente, API-Dokumente, XML-Dokumente
* sonstige Anlagen, ergänzende Hinweise
* ausdrücklich nicht veröffentlichte bzw. zurückgestellte Änderungen
* Hinweise auf andere Quellen
* Hinweise auf abweichende Umsetzungstermine

Wichtig: Die Mitteilung ist die regulatorische Startreferenz, aber nicht zwingend die vollständige Wissensbasis.

---

## 4. Alle Dokumente der Mitteilung erfassen

Für Mitteilung 56 müssen mindestens die folgenden Kategorien systematisch erfasst werden:

**A. EDIFACT-Dokumente** — alle dort aufgeführten: AHB, MIG, Allgemeine Festlegungen, PID / Anwendungsübersichten, API Guideline, Codelisten, sonstige EDIFACT-Dokumente.

Für jedes Dokument erfassen: Dokumenttyp, Nachrichtentyp, Sparte, Version, Veröffentlichungsdatum, Gültig-ab, Quelle, URL, Dateityp, Dokumentstatus, Zusammenhang mit Mitteilung, gegebenenfalls Vorgängerversion.

**B. Entscheidungsbaum-Diagramme** — erfassen: Version, Veröffentlichungsdatum, Gültigkeit, Codelisten, Entscheidungslogik, zugehörige Prozesse / Prüfidentifikatoren.

**C. Regelungen zum Übertragungsweg** — erfassen: Regelungen zum Übertragungsweg, AS4-Profil, Regelungen zum Übertragungsweg AS4, API-Webdienste / API-Regelungen, jeweilige Version, Gültigkeit.

---

## 5. Zweite regulatorische Quelle: BDEW MaKo

Die BNetzA-Quelle reicht nicht alleine aus. Deshalb muss anschließend die BDEW-MaKo-Plattform analysiert werden: https://www.bdew-mako.de/

Dort insbesondere: aktuell gültige Dokumente, zukünftig gültige Dokumente, gegebenenfalls historische Dokumente.

Die Dokumente müssen anhand ihres tatsächlichen Gültigkeitszeitraums bewertet werden: gültig von → gültig bis. Nicht nur anhand des Dateinamens.

### 5a. Dritte Quelle bei Gas-spezifischen, referenzierten Nachrichtentypen (K-2, bestätigt 2026-09-17, aus Etappe 3)

Für manche Gas-spezifische Nachrichtentypen reichen selbst BNetzA und BDEW zusammen nicht aus. Beispiel: SSQNOT wird von PID 4.0 (Prüfidentifikatoren 70095/70096, Sparte Gas) und von INVOIC AHB 1.0b/MIG 2.8e (Muss-Angabe "Dokumentennummer der SSQNOT") als benötigt referenziert, ist aber in keiner der 95 BNetzA-Mitteilungen und keinem der 1.752 BDEW-Einträge zu finden — sondern nur bei einer dritten, fachlich zuständigen Stelle (hier: DVGW Service & Consult, Reihe GABi Gastransport). Details siehe 11c.

**Regel für die weiteren Etappen:** Wird ein Dokument über ein gültiges PID oder AHB als benötigt referenziert, aber ist weder bei BNetzA noch bei BDEW auffindbar, muss gezielt nach einer dritten, fachlich zuständigen Stelle gesucht werden, bevor das Dokument als fehlend gilt. Ob ein bei dieser dritten Quelle gefundenes Dokument dann tatsächlich in den Regulatory State aufgenommen wird, regelt die Aufnahmeregel in 11e.

---

## 6. Wichtig: Fehlerkorrekturen und Lesefassungen

Bei mehreren Dokumenten können mehrere Dateien mit scheinbar gleicher Version existieren. Beispiel: IFTSTA AHB 2.0h

1. IFTSTA AHB 2.0h – informatorische Lesefassung
2. IFTSTA AHB 2.0h – informatorische Lesefassung – konsolidierte Lesefassung mit Fehlerkorrekturen Stand 23.06.2025
3. IFTSTA AHB 2.0h – konsolidierte Lesefassung mit Fehlerkorrekturen Stand 23.06.2025

Für die regulatorische Wissensbasis gilt folgende Priorität:
1. Konsolidierte Fassung mit Fehlerkorrekturen
2. Wenn mehrere solche Fassungen existieren: neuester Stand
3. Informatorische Lesefassung grundsätzlich ignorieren, wenn eine entsprechende konsolidierte Fassung vorhanden ist

Das Wort „informatorische Lesefassung" darf nicht automatisch als maßgebliche Version verwendet werden. Eine informatorische Lesefassung kann zwar als zusätzliche Quelle gespeichert werden, darf aber nicht die maßgebliche regulatorische Dokumentversion ersetzen.

### 6a. Erweiterung: außerordentliche Veröffentlichungen (bestätigt 2026-09-17, aus Etappe 2)

Neben Fehlerkorrektur-Ständen und Lesefassungen gibt es einen dritten, in Etappe 2 entdeckten Fassungstyp: **außerordentliche Veröffentlichungen** — Fassungen außerhalb des regulären Turnus, deren Änderungshistorie kumuliert ist (sie enthält sowohl frühere Fehlerkorrekturen als auch redaktionelle Anpassungen wie Layout oder Segmentzähler) und die von keiner BNetzA-Mitteilung angekündigt werden.

Für diesen Fassungstyp gilt dieselbe Priorität wie für konsolidierte Fassungen: **der neueste Stand der gemeinsamen chronologischen Reihe (Fehlerkorrektur-Stände und außerordentliche Veröffentlichungen zusammen) ist maßgeblich.** Betroffen zum Piloten-Zeitpunkt: CONTRL AHB/MIG, INSRPT AHB/MIG. Details und Beispiel siehe Abschnitt 11b.

---

## 7. PDF als Primärquelle für die Verifikation

Wenn mehrere Dateiformate verfügbar sind: PDF bevorzugen. Grund: Die PDF-Fassung soll als verlässliche Referenz für die tatsächlich veröffentlichte Dokumentversion dienen.

Andere Formate wie Word, Excel, XML dürfen zusätzlich analysiert werden, wenn sie fachlich benötigt werden. Sie ersetzen aber nicht automatisch die PDF-Referenz.

---

## 8. Nicht nur Mitteilung 56 betrachten

Das ist besonders wichtig. Wenn Atlas den regulatorischen Stand 01.10.2026 abbilden soll, darf nicht einfach angenommen werden: „Alles, was nicht in Mitteilung 56 steht, ist nicht relevant."

Stattdessen muss für jedes benötigte regulatorische Artefakt festgestellt werden:

1. Wurde es durch Mitteilung 56 geändert?
2. Wenn nein: Welche vorherige Version ist zum 01.10.2026 weiterhin gültig?
3. Gibt es auf BDEW-MaKo eine gültige bzw. zukünftig gültige Version?
4. Existieren Fehlerkorrekturen?
5. Existiert eine konsolidierte Fassung?
6. Gibt es eine neuere Version, die zwar veröffentlicht, aber noch nicht gültig ist?
7. Gibt es eine Konsultationsfassung, die nicht verbindlich ist?
8. Gibt es widersprüchliche Informationen zwischen BNetzA und BDEW?

---

## 9. Regulatorischer Stand als Stichtagsmodell

Atlas benötigt kein einfaches Dokumentenverzeichnis. Atlas benötigt einen Regulatorischen Stichtag, z.B. Regulatorischer Stand: 01.10.2026. Dieser besteht aus allen zu diesem Zeitpunkt gültigen regulatorischen Artefakten.

```text
Regulatorischer Stand 01.10.2026

├── EDIFACT
│   ├── UTILMD
│   │   ├── AHB Strom 2.2
│   │   ├── MIG Strom S2.2
│   │   ├── AHB Gas 1.2
│   │   └── MIG Gas G1.2
│   ├── APERAK
│   ├── IFTSTA
│   ├── INVOIC
│   ├── MSCONS
│   └── ...
├── PID
├── EBD
├── Codelisten
├── XML
├── API
├── AS4
└── Übertragungsweg
```

Für jedes Artefakt muss nachvollziehbar sein: Warum ist genau diese Version am Stichtag gültig?

### 9a. Verhältnis zum bestehenden Atlas-Datenmodell

Atlas kennt aktuell eine grobkörnige `RegulatoryVersion` (z.B. "Mitteilung 56, gültig ab 01.10.2026"), der bislang der gesamte Requirement-Katalog als Ganzes zugeordnet wird. Der in diesem Auftrag beschriebene `Regulatory State` (siehe Abschnitt 15) ist feingranularer: er bündelt pro Stichtag die jeweils gültige Version *jedes einzelnen* regulatorischen Dokuments (AHB, MIG, Codeliste, EBD, ...), nicht nur einen einzigen Versionsstring.

Baue diesen Lauf so, dass er das Verhältnis zwischen beiden Konzepten explizit benennt, statt es stillschweigend zu vermischen: entweder wird `RegulatoryVersion` zum groben Alias für einen `Regulatory State` (1:1-Beziehung, z.B. `RegulatoryVersion.regulatory_state_id`), oder `Regulatory State` wird als komplett neue Ebene oberhalb von `RegulatoryVersion` eingeführt. Triff hierzu einen konkreten Vorschlag mit Begründung, aber führe noch keine Schemaänderung durch, ohne dass dieser Vorschlag bestätigt wurde.

### 9b. Entscheidung zu 9a (bestätigt 2026-09-17, nach Pilot-Etappe 1)

Nach Analyse des tatsächlichen Bestands (`vorschlag_regulatory_state_modell.md`, Etappe 1) wurde bestätigt: **`Regulatory State` wird als neue Ebene oberhalb von `RegulatoryVersion` eingeführt**, kein 1:1-Alias. Ein `Regulatory State` steht für einen Stichtag; darunter hängen mehrere `RegulatoryVersion`-Datensätze über ein optionales Feld `RegulatoryVersion.regulatory_state_id`.

Begründung: Die bestehenden `RegulatoryVersion`-Datensätze sind nach Sparte getrennt, ein Stichtag umfasst aber Strom und Gas gemeinsam. Zudem haben zum selben Stichtag existierende RVs teils unterschiedliche Startdaten (Beispiel: zum Stand 01.04.2026 gehören heute zwei RVs mit unterschiedlichem Beginn — Gas ab 01.04.2026, Strom ab 06.06.2025, korrigiert 2026-09-18; das Datum stammt aus Mitteilung 46 in Verbindung mit der Verschiebung durch Mitteilung 47). Ein einfacher 1:1-Alias könnte das nicht abbilden. Die `RegulatoryVersion` bleibt weiterhin die produktseitige Steuergröße (aktiv/inaktiv, Release-Notiz, Assessments); der `Regulatory State` ist die regulatorische Tatsache mit eigenem Lebenszyklus.

**Offener Folgepunkt (Produktentscheidung, nicht Teil dieses Rechercheauftrags):** Für den Regulatory State 01.10.2026 existiert bisher nur eine Gas-seitige `RegulatoryVersion` (Mitteilung 56). Eine entsprechende Strom-`RegulatoryVersion` für den 01.10.2026 gibt es noch nicht. Ob und wann sie angelegt wird, ist separat zu entscheiden und im Ticket aus Abschnitt 0 als offener Punkt zu führen, damit er nicht im fertigen Regulatory-State-Ergebnis untergeht.

---

## 10. Versionen niemals überschreiben

Atlas muss regulatorische Historie erhalten. Beispiel: UTILMD AHB Gas

* 1.1 — gültig: 01.04.2026 – 30.09.2026
* 1.2 — gültig: ab 01.10.2026

Die Version 1.1 darf nicht durch 1.2 ersetzt werden. Stattdessen: Dokument → Dokumentversion → Gültigkeitszeitraum.

---

## 11. Jede regulatorische Aussage braucht eine Provenienz

Für jedes relevante Artefakt speichern: Quelle, URL, Dokumentname, Dokumentversion, Veröffentlichungsdatum, Gültig ab, Gültig bis, Mitteilung, PDF-Datei, Hash der Datei, Analysezeitpunkt, gegebenenfalls Fehlerkorrekturstand, Prioritätsentscheidung, Begründung.

Beispiel: IFTSTA AHB — Version: 2.1, Gültig ab: 01.10.2026, Quelle: BNetzA / Mitteilung 56, PDF: vorhanden, Konsolidierte Fassung: ja, Fehlerkorrekturstand: ..., Maßgebliche Fassung: ja, Begründung: ...

### 11a. Konkretisierung nach Pilot-Etappe 1: Drei-Ebenen-Provenienz-Schema

Etappe 1 (UTILMD) hat gezeigt, dass eine Dokumentversion (z.B. "AHB Gas 1.2") mehrere konkrete Dateien mit eigenem Hash umfassen kann (Basisfassung, konsolidierte Fassung, informatorische Lesefassung). Das Provenienz-Modell aus diesem Abschnitt wird deshalb um eine dritte Ebene präzisiert: **Dokument → Dokumentversion → Fassung**, wobei eine Fassung eine konkrete Datei mit SHA-256-Hash ist.

Jede Fassung wird erfasst, keine wird gelöscht — die Auswahl vergibt stattdessen eine Rolle: `maßgeblich`, `ergänzend`, `ersetzt`, `informativ` oder `verworfen`. Beispiel aus dem Piloten: Die BDEW-Basisfassung von AHB Gas wird nicht verworfen, obwohl eine konsolidierte Fehlerkorrektur-Fassung existiert — sie bleibt `ergänzend`, weil nur sie die Änderungshistorie gegenüber der Vorversion trägt (die konsolidierte Fassung listet nur die Fehlerkorrekturen).

Jedes Datum (Veröffentlichung, Gültig ab, Gültig bis) erhält zusätzlich einen Beleg-Typ: ausdrücklich genannt, abgeleitet, oder offen. Die acht Fragen aus Abschnitt 8 sind je Dokument Pflichtfelder im Schema, nicht optional. Referenz: `provenienz_schema_v0.json`, Zuordnung zu den Feldern dieses Abschnitts in `etappe1_utilmd.md`, Abschnitt 7.

Die Rollen-Abgrenzung `ersetzt` vs. `verworfen` ist seit Commit 4617854 in `rollendefinition.md` schriftlich festgelegt (Kernregel: eine Fassung wird `ersetzt`, wenn eine neuere Fassung sie inhaltlich vollständig fortführt; `verworfen` nur, wenn eine Fassung fehlerhaft oder zurückgezogen ist, unabhängig vom Vorhandensein einer neueren Fassung). **Klarstellung (bestätigt 2026-09-18, aus Etappe 4):** Das Muster „Gültig-bis liegt vor Gültig-ab der Folgefassung" ist für sich genommen **kein** Beleg für `verworfen` — es tritt gleichermaßen bei korrekt `ersetzt`en Fehlerkorrekturständen auf. `verworfen` wird ausschließlich bei ausdrücklichem Beleg einer Rücknahme durch die Quelle vergeben, niemals aus einem bloßen Datumsmuster abgeleitet. Diese Rolle war zwischenzeitlich im Repo (`rollendefinition.md`) ausgeschlossen worden; das war eine echte Abweichung vom Auftrag und wurde in Etappe 4 korrigiert (Schema v0.6): `verworfen` ist zulässig, aber belegpflichtig und bislang an keine der geprüften Fassungen vergeben.

### 11b. Erweiterung nach Etappe 2: außerordentliche Veröffentlichungen, Schema v0.3 (bestätigt 2026-09-17)

Etappe 2 hat einen vierten Fassungstyp identifiziert, der in Abschnitt 6/11a noch nicht vorgesehen war: **außerordentliche Veröffentlichungen** (siehe 6a). Bestätigte Regel: der neueste Stand der gemeinsamen chronologischen Reihe aus Fehlerkorrektur-Ständen und außerordentlichen Veröffentlichungen ist maßgeblich — dieselbe "neuester Stand gilt"-Logik wie in Abschnitt 6, nur auf den neuen Fassungstyp ausgeweitet.

Beispiel CONTRL MIG 2.0b (durchgerechnet gegen die Rollendefinition):

| Fassung | Typ | Stand | Rolle |
|---|---|---|---|
| bdew:6776 PDF | Basis | — | ergänzend (Anlage Mitteilung 24, bytegleich) |
| bdew:6777 PDF | konsolidiert | 06.12.2021 | ersetzt → 7422 |
| bdew:7422 PDF | außerordentlich | 26.07.2024 | ersetzt → 8195 |
| bdew:8195 PDF | außerordentlich | 11.12.2025 | maßgeblich |
| bdew:7561 XML | außerordentlich | ohne Stand | informativ (Nicht-PDF, siehe Abschnitt 7) |

Nichts wird verworfen; die Frage "welche Fassung galt am 01.08.2024?" bleibt beantwortbar (Antwort: 7422).

**Schema v0.3** (Weiterentwicklung von `provenienz_schema_v0.json`): eigenes Datumsfeld `stand_ausserordentlich`, getrennt von `fehlerkorrekturstand` (nie beide gleichzeitig gefüllt); abgeleitetes Sortierfeld `stand_reihe_datum` für die gemeinsame chronologische Reihe (reine Sortierung, keine Vermischung der Typen); neues Pflichtfeld je Fassung `mitteilungsbezug` mit den Werten: bytegleiche Mitteilungsanlage, Mitteilungsanlage, Konsultationsanlage, **kein Mitteilungsbezug** (plus Freitext-Vermerk). (Stand 2026-09-18: Das Schema ist inzwischen bei v0.6 angelangt, die Datei heißt im Repo `provenienz_schema.json`, ohne Versionssuffix im Namen — Verweise auf `provenienz_schema_v0.json`/v0.3 in diesem Auftrag sind insofern historisch zu lesen.)

**Kernbefund K-1, für den Übergabebericht in Etappe 8 hervorzuheben:** Über Etappe 0–2 hinweg (36 Dokumente, 209 Fassungen) haben 116 Fassungen keinen Mitteilungsbezug — darunter 11 von 36 maßgeblichen Fassungen. In knapp einem Drittel der Fälle kennt die amtliche BNetzA-Quelle die am Stichtag tatsächlich geltende Fassung nicht; sie wäre ohne den BDEW-Abgleich aus Abschnitt 5 unauffindbar geblieben. **Ergänzung aus Etappe 4:** ein weiterer Fall ohne Mitteilungsbezug ist hinzugekommen — die Standardlastprofile nach TU München 1.1, die in keiner Mitteilung stehen, keine eigene BNetzA-Anlage besitzen und nur über Kriterium C (Referenzierung durch UTILMD Gas) gehalten werden. Die kumulierte Fassungszahl für K-1 wird erst im Etappe-8-Bericht abschließend ausgewertet.

### 11c. SSQNOT: dritte Quelle DVGW (O-5, bestätigt 2026-09-17/18, aus Etappe 3)

SSQNOT wird am Stichtag benötigt (siehe 5a), ist aber weder bei BNetzA noch bei BDEW veröffentlicht. Maßgeblich: **SSQNOT 5.7**, konsolidierte Lesefassung mit Fehlerkorrekturen, Stand 31.10.2021, Autor DVGW Service & Consult (Reihe GABi Gastransport), gültig ab 01.12.2019, verifiziert direkt am Originaldokument (27 Seiten, Segmentlayout und Anwendungsfall-Tabelle in einer Datei).

**Offener Punkt O-14 (ungeklärt, bewusst nicht aufgelöst):** Prüfidentifikator 70096 heißt in PID 4.0 "Mehr-/Mindermengenmeldung RLP", in SSQNOT 5.7 "Mehr-/Mindermengenmeldung RLM". Beide Bezeichnungen stehen mit Seitenangabe im Provenienzdatensatz, ausdrücklich ohne Vereinheitlichung. Für PI 70095 stimmen beide Quellen überein ("SLP") — das erhöht die Zuversicht, dass es sich bei 70096 um eine echte Einzelabweichung handelt, nicht um eine systematische Bezeichnungsdifferenz zwischen den Quellen. Punkt steht im Ticket unter "Offene fachliche Punkte".

Die generelle Frage, ob ein bei einer solchen dritten Quelle gefundenes Dokument automatisch in den Regulatory State gehört, ist in 11e als eigene, empirisch geprüfte Aufnahmeregel geklärt.

### 11d. Weitere Etappe-3-Befunde: Sparten-Zuordnung, GeLi Gas 3.0 (bestätigt 2026-09-17)

**Sparten-Zuordnung evidenzbasiert statt angenommen:** Aus PID 4.0 (1.344 ausgewertete Zeilen, Spalten "Sparte Strom"/"Sparte Gas") ist belegt, dass MSCONS, IFTSTA, ORDERS, ORDRSP, REMADV, INVOIC, PARTIN, INSRPT, COMDIS, PRICAT, QUOTES, REQOTE und ORDCHG echte Gas-Anwendungsfälle haben ("beide" ist damit für diese 13 Nachrichtentypen belegt, nicht nur angenommen). Zwei Korrekturen: UTILTS AHB/MIG sind entgegen der ursprünglichen Annahme reines Strom (0 von 26 Zeilen betreffen Gas) — dazu passend deutete sich zunächst an, dass Mitteilung 57 UTILTS perspektivisch durch API-Webdienste Strom ersetzen könnte; nach Klärung in Abschnitt 2 ist Mitteilung 57 zum Stichtag 01.10.2026 nicht verbindlich (nur Konsultationsfassungen für 01.04.2027), die UTILTS-Ablösung ist also ein Ausblick für Frage 7, nicht für Frage 6. APERAK und CONTRL haben dagegen keine einzige PID-Zeile; ihre "beide"-Einstufung bleibt vorerst unverändert, aber ausdrücklich ohne Einzelnachweis — dieser Unterschied (belegt vs. angenommen) muss bis zur Konsolidierung in Etappe 7 sichtbar bleiben und darf dort nicht mit den 13 belegten Fällen gleichgesetzt werden.

**Gegenprobe erledigt (siehe 11f, Etappe 5):** Diese Auswertung wurde ursprünglich gegen die PID-4.0-Basisfassung durchgeführt. Etappe 5 hat sie gegen die maßgebliche Fassung (zweiter Korrekturstand vom 12.08.2026) gegengeprüft — Ergebnis: praktisch keine Änderung (nur UTILMD AHB Gas +1 Gas-Zeile). Der ursprünglich als O-16 geführte Punkt ist damit erledigt, keine weitere Wiederholung in Etappe 7 nötig.

**GeLi Gas 3.0 (O-6), kein Formatimpact:** Der Beschluss der Beschlusskammer 7 vom 12.09.2025 nennt weder EDIFACT noch UTILMD noch eine Nachrichtentypversion; für Datenformate verweist er auf die Anlage zu BK7-06-067 "in der jeweils geltenden Fassung". Zum 01.10.2026 wirkt er dennoch — aber vertraglich, nicht formatseitig (Widerruf der Festlegung BK7-17-026, neuer Messstellenbetreiberrahmenvertrag Gas). Kein Eintrag im Regulatory-State-Dokumentbaum, aber als vertraglicher Kontext für die spätere fachliche Analyse (Abschnitt 12/16) vormerken, nicht vollständig fallenlassen.

### 11e. Aufnahmeregel für den Regulatory State (bestätigt 2026-09-18, empirisch geprüft)

Ausgehend von der SSQNOT-Erfahrung (11c) wurde eine generelle, empirisch geprüfte Regel festgelegt, wann ein Dokument überhaupt Teil des Regulatory State wird (Referenz: `aufnahmeregel.md`). Ein Dokument gehört hinein, wenn mindestens eines der folgenden Kriterien greift:

* **A** — Anlage einer verbindlichen Mitteilung der BK6/BK7-Reihe, die am Stichtag noch wirkt
* **B** — geführt in der am Stichtag gültigen Anwendungsübersicht der Prüfidentifikatoren (PID)
* **C** — von einem Dokument aus A oder B verbindlich referenziert, z.B. als Muss-Angabe

Alles andere bleibt draußen — aber mit Negativbeleg je geprüfter Dokumentreihe, nicht mit einer bloßen Behauptung. Jeder Provenienzdatensatz trägt seither ein Pflichtfeld `aufnahmekriterium` mit Beleg.

**Empirische Prüfung:** Gegen die DVGW-Reihe (11 Gas-Nachrichtentypen, u.a. TSIMSG 5.11) geprüft: nur SSQNOT hat Treffer in PID 4.0, die übrigen zehn keine — die Regel trennt also tatsächlich zwischen benötigten und nicht benötigten externen Dokumenten, nicht nur zwischen "von derselben Quelle" und "nicht von derselben Quelle". Rückwirkend gegen alle bis Etappe 3 erfassten 37 Dokumente geprüft: keines fällt heraus, keines kommt neu hinzu — die Regel bestätigt den bisherigen Bestand, ändert ihn nicht rückwirkend.

**Präzisierung zu Kriterium C (bestätigt 2026-09-18, aus Etappe 4):** Eine bloße Gattungsnennung im Text einer AHB/MIG (z.B. das Wort „Anwendungshilfe") erfüllt Kriterium C nicht. Erforderlich ist eine konkrete Bezugnahme mit Dokumentname und Version. Beispiel: Drei BDEW-Anwendungshilfen (Stand 18.08.2026) wurden deshalb mit Negativbeleg ausgeschlossen, obwohl der Begriff „Anwendungshilfe" in den einschlägigen AHB vorkommt. Umgekehrt bestätigt: Die Standardlastprofile nach TU München 1.1 erfüllen Kriterium C, weil UTILMD Gas sie konkret mit Dokumentname und Version referenziert (siehe K-1-Ergänzung in 11b).

### 11f. EBD 4.3 und Querprüfung gegen die maßgebliche PID-Fassung (bestätigt 2026-09-18, aus Etappe 5)

Maßgeblich am 01.10.2026: **EBD und Codelisten 4.3**, konsolidierte Fassung, Stand 23.06.2026, 831 Seiten. Die Basisfassung ist bytegleich mit der Mitteilung-56-Anlage und bleibt `ergänzend` (trägt weiterhin die Änderungshistorie gegenüber 4.2, analog zum UTILMD-Beispiel in 11a).

**Methodische Besonderheit gegenüber AHB/MIG:** Anders als bei AHB und MIG, wo die konsolidierte Fassung die Historie auf die Fehlerkorrekturen verkürzt (vgl. 11a), führt die konsolidierte EBD-Fassung beide Historien zusammen — 24 Einträge „Genehmigt" für inhaltliche Änderungen gegenüber 4.2 sowie 12 Fehlerkorrektur-Einträge in derselben Liste. Für die fachliche Analyse in Abschnitt 12 muss der Herkunftstyp jedes Eintrags erhalten bleiben, damit inhaltliche Änderungen nicht mit reinen Korrekturen vermischt werden.

**Querprüfung gegen die maßgebliche PID-Fassung** (Stand 12.08.2026, 1.352 Zeilen, Spalte „EBD-Code / Code Codeliste"): 285 von 285 referenzierten EBD-Kennungen sind in 4.3 vorhanden. 10 von 11 referenzierten Codelisten-Kennungen sind vorhanden (Ausnahme: O-17, unten). 79 der 364 EBD-Kennungen im Dokument werden von keiner PID-Zeile referenziert — sie sind über keinen Prüfidentifikator erreichbar. Das begrenzt, was Atlas später über die PID an EBD-Kennungen andocken kann, und ist für Abschnitt 16 vorzumerken.

**Offener Punkt O-17 (neu, bewusst ungeklärt):** Prüfidentifikator 55024 referenziert in der PID die Codelisten-Kennung S_0088. Diese existiert in EBD 4.3 nicht (die `S_`-Kennungen enden dort bei S_0087) und auch in keinem anderen maßgeblichen Dokument. Sie steht nur in der PID selbst, unverändert in Basis- und maßgeblicher Fassung — auch die Fehlerkorrekturen haben daran nichts geändert. Der Verweis bleibt unaufgelöst; keine Korrektur auf eine ähnliche Kennung.

**O-16 aufgelöst:** Die Gegenprobe der Sparten-/Referenzauswertung aus 11d gegen die maßgebliche PID-Fassung (1.352 statt 1.344 Zeilen) ändert praktisch nichts: UTILMD AHB Gas steigt von 131 auf 132 Gas-Zeilen, alle übrigen 17 AHB-Werte bleiben unverändert, UTILTS bleibt bei 0 Gas-Zeilen. Keine Aussage aus 11d kippt. Für Etappe 7 ist damit nichts mehr zu wiederholen.

---

## 12. Dokumente anschließend fachlich analysieren

Erst nachdem der regulatorische Stand vollständig bestimmt wurde, dürfen die Dokumente fachlich analysiert werden. Dabei insbesondere:

**AHB:** Prozesse, Prozessschritte, Prüfidentifikatoren, Muss-/Kann-/Abhängigkeitslogik, Bedingungen, Rollen, Nachrichten, Segmente, Datenelemente, Codelisten, Entscheidungslogik, Änderungshistorie.

**MIG:** Nachrichtenstruktur, Segmente, Datenelemente, Status, Pflichtigkeiten, Codelisten, Beispiele, Bemerkungen, Änderungen.

**PID:** Prüfidentifikator, Prozess, Prozessschritt, Nachricht, Rollen, Antwort-/Folgebeziehungen, AHB-Bezug.

**EBD:** Entscheidungsregeln, Bedingungen, Prüfentscheidungen, fachliche Auswirkungen.

**Codelisten:** Codeliste, Version, Code, Bedeutung, Gültigkeit, Bedingungen.

---

## 13. Ziel: Aufbau der ersten Atlas-Wissensbasis

Die erste regulatorische Wissensbasis von Atlas soll den vollständigen regulatorischen Stand zum 01.10.2026 abbilden. Der 01.10.2026 ist der erste verbindliche Stichtag, den Atlas als vollständigen regulatorischen Stand aufnimmt.

Der bisher gültige Stand zum 01.04.2026 muss nicht vollständig rekonstruiert oder als eigene Wissensbasis aufgebaut werden. Er wird nur dann herangezogen, wenn dies notwendig ist, um beispielsweise festzustellen: ob ein Dokument zum 01.10.2026 weiterhin gültig ist, welche Version eines Dokuments zum 01.10.2026 gilt, ob ein Dokument durch Mitteilung 56 geändert wurde, ob eine bestehende Version weitergeführt wird, ob eine neue Version eine alte Version ablöst.

Wichtig: Nicht unnötig den historischen Stand 01.04.2026 analysieren. Der Analysefokus liegt auf dem Zielzustand 01.10.2026.

### 13a. Etappierung statt Gesamtlauf

Dieser Lauf soll die vollständige Dokumentlandschaft zum Stichtag 01.10.2026 abdecken, das sind voraussichtlich mehrere Dutzend bis über hundert Einzeldokumente über alle Sparten, Nachrichtentypen und Dokumentkategorien hinweg. Arbeite das etappiert ab, nicht als einen einzigen großen Durchlauf. Der konkrete Etappenplan steht im Anhang am Ende dieses Dokuments — folge ihm als Task-Liste im in Abschnitt 0 angelegten Ticket, statt eine eigene Aufteilung zu improvisieren, damit Fortschritt zwischen mehreren Sessions vergleichbar bleibt.

Gib nach jeder Etappe einen Zwischenstand aus (analog zum bestehenden Prinzip "kapitelweise mit Zwischenstand" aus der Extraktionspipeline, siehe `Claude_Code_Prompt_FINAL.md`): Anzahl erfasster Dokumente, Anzahl offener/unklarer Fälle, Anzahl Widersprüche zwischen BNetzA und BDEW. Kein einzelner Sammelbericht erst am Ende.

Wenn absehbar wird, dass eine vollständige Abdeckung in diesem Lauf nicht erreichbar ist, priorisiere die Etappen in der im Anhang vorgegebenen Reihenfolge, und melde explizit, welche Etappen noch offen sind.

---

## 14. Der regulatorische Zielzustand 01.10.2026

Das Ergebnis muss eine vollständige Momentaufnahme des regulatorischen Zustands zum 01.10.2026 sein. Atlas muss für jedes relevante regulatorische Artefakt beantworten können: Welche Version gilt am 01.10.2026? Und: Warum wurde genau diese Version ausgewählt?

```text
Regulatorischer Stand
01.10.2026

├── EDIFACT
│   ├── UTILMD
│   ├── APERAK
│   ├── IFTSTA
│   ├── INVOIC
│   ├── MSCONS
│   └── ...
├── AHB
├── MIG
├── PID
├── EBD
├── Codelisten
├── Entscheidungsbaum-Diagramme
├── API
├── XML
├── AS4
└── Regelungen zum Übertragungsweg
```

Für jedes Artefakt: Dokument, Version, Gültig ab, Gültig bis, Quelle, Mitteilung, PDF, Fehlerkorrekturstand, Maßgebliche Fassung, Auswahlbegründung.

---

## 15. Atlas Regulatory State

Der ermittelte regulatorische Stand wird als eigener Regulatory State in Atlas angelegt. Beispiel:

```text
Regulatory State
----------------
Name: Marktkommunikation 01.10.2026
Stichtag: 01.10.2026
Basis: BNetzA Mitteilung 56
Ergänzende Quelle: BDEW MaKo
Status: VALID
```

Darunter werden die tatsächlich maßgeblichen Dokumentversionen verknüpft. Wichtig: Die Dokumente selbst bleiben versioniert. Der Regulatory State referenziert lediglich die zu diesem Stichtag gültigen Versionen. Damit kann Atlas später beispielsweise einen neuen Regulatory State erzeugen: 01.10.2026 → 01.04.2027 → 01.10.2027, ohne die bestehenden regulatorischen Daten zu überschreiben.

### 15a. Output-Format und Abgrenzung zur bestehenden Datenbank

Das Ergebnis dieses Laufs ist zunächst ein strukturierter Rechercheartefakt zur menschlichen Prüfung (z.B. eine strukturierte Markdown- oder JSON-Datei je Dokumentkategorie mit den in Abschnitt 11 geforderten Provenienzfeldern), kein direkter Schreibvorgang in die produktive Atlas-Datenbank.

Die bestehenden, aktuell leeren Tabellen (`MessageDefinition`, `MessageSegment`, `MessageField`, `CodeList`, `CodeListEntry`, `Testkonstellation`, `TestkonstellationSchritt`) werden in diesem Auftrag nicht befüllt — das ist laut Abschnitt 12 dieses Auftrags ausdrücklich ein nachgelagerter Schritt, der erst nach vollständiger und bestätigter Ermittlung des Regulatory State erfolgt.

Diese Rechercheartefakte werden im in Abschnitt 0 angelegten Ticket bzw. dessen Branch committet und über einen PR eingereicht (Issue anlegen, eigener Branch, PR mit Ergebnisbericht — siehe `Claude_Code_Prompt_FINAL.md`, Abschnitt 18), auch wenn dieser Lauf keine Code-Änderung, sondern nur Recherche-Artefakte liefert.

---

## 16. Fachliche Abbildung in Atlas

Erst nachdem der vollständige Regulatory State 01.10.2026 ermittelt wurde, werden daraus die Atlas-Fachobjekte abgeleitet: Prozesse, Prozessschritte, Rollen, Nachrichten, PI, Segmente, Datenelemente, Regeln, Codelisten, Abhängigkeiten, Anforderungen, Testfälle.

Dabei gilt weiterhin: Regulatorische Rohdaten ≠ Atlas-Semantik. Die Originaldokumente und ihre extrahierten Inhalte bleiben die belastbare Quelle. Die Atlas-Semantik wird darauf aufgebaut.

Zu beachten (aus Etappe 5, siehe 11f): 79 der 364 EBD-Kennungen aus EBD/Codelisten 4.3 sind über keinen Prüfidentifikator der PID erreichbar. Eine spätere Verknüpfung von EBD zu Prozessen/Prüfidentifikatoren in Atlas kann diese 79 Kennungen nicht über die PID herleiten — sie brauchen, falls fachlich relevant, einen anderen Erschließungsweg oder bleiben bewusst unverknüpft.

---

## Wichtigster Grundsatz für diesen Durchlauf

Baue jetzt den vollständigen regulatorischen Stand 01.10.2026. Rekonstruiere nicht unnötig den vollständigen Stand 01.04.2026. Nutze den alten Stand ausschließlich dort, wo er zur Bestimmung des neuen Stands erforderlich ist.

Das ist für den ersten Durchlauf auch wesentlich effizienter. Wir wollen am Ende nicht zwei Wissensbasen haben, sondern eine belastbare Ausgangsbasis für Atlas: Marktkommunikation 01.10.2026.

---

## Anhang: Konkreter Etappenplan

Verbindliche Reihenfolge für diesen Auftrag, geführt als Checkliste im in Abschnitt 0 angelegten Ticket (**#64**). Jede Etappe endet mit einem kurzen Zwischenbericht (siehe Abschnitt 13a) als Ticket-Kommentar und, sofern der Projekt-Workflow das vorsieht, einem eigenen Commit/PR-Zwischenstand — nicht erst am Ende der gesamten Recherche.

**Etappe 0 — Fundament: Mitteilung 56 selbst erfassen**
Mitteilung 56 (und ggf. neuere/korrigierende Mitteilungen) vollständig lesen. Alle darin referenzierten Dokumente als Rohliste erfassen — nur Metadaten (Name, Dokumenttyp, Sparte, Version, Link), noch keine Tiefenanalyse einzelner Dokumente. Gegenprüfung nach Abschnitt 2 (BK6/BK7, Aktualität von Mitteilung 56).
*Abnahmekriterium:* vollständige Rohliste aller in Mitteilung 56 referenzierten Dokumente, je mit Kategorie-Tag (AHB / MIG / PID / EBD / Codeliste / Übertragungsweg / AS4 / API / XML / Sonstiges) und Sparte-Tag (Strom / Gas / beide). Diese Liste ist die Arbeitsgrundlage für alle folgenden Etappen — sie legt auch fest, welche Nachrichtentypen in Etappe 2/3 konkret bearbeitet werden, statt das vorab zu erraten.
*Status: abgeschlossen.* Dabei aufgetreten: offener Fall O-8 (Interpretation der BDEW-Gültigkeitsdaten) und O-10 (Vermerk „erst zum 1.4.2026" in der Änderungshistorie von MIG Gas G1.2) — beide gehören laut Rückmeldung in die spätere fachliche Analyse (Abschnitt 12/16) und ändern nichts an der Versionsauswahl.

**Etappe 1 — Pilot: UTILMD vollständig (Strom + Gas)**
UTILMD zuerst und exemplarisch vollständig durchziehen (AHB Strom, MIG Strom, AHB Gas, MIG Gas), inklusive Fragenkatalog aus Abschnitt 8 und vollständiger Provenienz nach Abschnitt 11. Grund für die Sonderstellung: UTILMD ist komplex und zentral genug, um die gesamte Methodik (Lesefassung/Fehlerkorrektur-Priorität, PDF-Referenz, BDEW-Abgleich, Provenienz-Schema) einmal end-to-end zu validieren, bevor auf alle übrigen Nachrichtentypen skaliert wird.
*Abnahmekriterium:* für alle vier UTILMD-Dokumente eine vollständig belegte Aussage "diese Version gilt ab 01.10.2026, weil ...", inklusive Auflösung etwaiger Lesefassungs-/Fehlerkorrektur-Konflikte.
*Status: abgeschlossen und bestätigt.* Ergebnisse siehe Abschnitt 9b (Regulatory-State-Modell) und 11a (Drei-Ebenen-Provenienz-Schema, Rollen-Abgrenzung `ersetzt`/`verworfen` seit Commit 4617854 in `rollendefinition.md` festgelegt).

**Etappe 2 — Übrige EDIFACT-Nachrichtentypen, Strom**
Alle in Etappe 0 identifizierten Strom-Nachrichtentypen außer UTILMD, nach demselben Muster wie Etappe 1 abarbeiten. Umfasst praktisch auch die meisten sparten-übergreifenden Nachrichtentypen (nur UTILMD hat eine echte Sparten-Trennung; die übrigen EDIFACT-Dokumente nutzen dieselbe Datei für Strom und Gas), damit Etappe 3 nicht doppelt arbeitet.
*Abnahmekriterium:* pro Nachrichtentyp derselbe Provenienz-Datensatz wie in Etappe 1.
*Status: abgeschlossen und bestätigt.* 32/32 Dokumente belegt, keine Widersprüche BNetzA/BDEW. Neuer Fassungstyp "außerordentliche Veröffentlichung" identifiziert und geregelt (Abschnitt 6a/11b, Schema v0.3). O-1/O-2/O-3 aus Etappe 0 gelöst. Kernbefund K-1 zur Mitteilungsbezug-Lücke siehe 11b — für Etappe 8 vormerken.

**Etappe 3 — Übrige EDIFACT-Nachrichtentypen, Gas**
Da Etappe 2 die gemeinsamen (sparten-übergreifenden) Dokumente bereits mit erfasst hat, beschränkt sich Etappe 3 auf echte Gas-Spezifika: welche der in Etappe 2 erfassten gemeinsamen Dokumente in Gas tatsächlich angewendet werden, gas-spezifische Festlegungen (z.B. GeLi Gas 3.0), und ungeklärte Dokumente wie SSQNOT.
*Abnahmekriterium:* SSQNOT als eigener Provenienzdatensatz oder belegte Entfall-Aussage; GeLi Gas 3.0 auf Formatwirkung geprüft; Sparten-Zuordnung der Etappe-2-Dokumente belegt statt angenommen.
*Status: abgeschlossen und bestätigt (Commit 1f3137b, PR #65).* SSQNOT bei dritter Quelle (DVGW Service & Consult) gefunden und verifiziert (11c). Kernbefund K-2 ("BNetzA + BDEW reichen für Gas-spezifische, referenzierte Nachrichtentypen nicht aus") bestätigt und zur generellen, empirisch geprüften Aufnahmeregel A/B/C ausgebaut (11e) — rückwirkend gegen alle 37 Dokumente geprüft, keine Änderung am Bestand. O-14 (RLP/RLM-Unstimmigkeit) offen und bewusst ungeklärt gelassen, mit positivem Gegenbeleg bei PI 70095. GeLi Gas 3.0 (O-6) ohne Formatwirkung, vertraglicher Kontext für Abschnitt 12/16 vorgemerkt. Sparten-Zuordnung für 13 Nachrichtentypen evidenzbasiert; UTILTS auf Strom-only korrigiert; Mitteilung 57 geklärt (veröffentlicht 31.07.2026, nur Konsultationsfassungen für 01.04.2027, siehe Abschnitt 2) und in allen 37 Datensätzen unter Frage 6/7 aus Abschnitt 8 vermerkt. APERAK/CONTRL bleiben "beide" ohne Einzelnachweis, das muss bis Etappe 7 sichtbar bleiben (siehe 11d).

**Etappe 4 — Querschnittsdokumente: PID/Anwendungsübersichten, Codelisten, Allgemeine Festlegungen**
Diese sind meist nachrichtentyp- und sparten-übergreifend und werden als eigener Block bearbeitet, da sie sich nicht sauber einer einzelnen Etappe 2/3 zuordnen lassen. PID 4.0 ist durch die Sparten-Auswertung aus Etappe 3 bereits teilweise erschlossen. Bewertung nach Abschnitt 6a (Fehlerkorrekturen/außerordentliche Veröffentlichungen), 11a–11e (Provenienz-Schema, Aufnahmeregel).
*Status: abgeschlossen und bestätigt.* 10 Dokumente aufgenommen (u.a. PID 4.0 im zweiten Korrekturstand vom 12.08.2026, Allgemeine Festlegungen 6.1d, Konfigurationen 1.4, Verwendungszwecke 1.0 kons. 29.06.2026, sechs fortgeltende Codelisten teils bis zurück ins Jahr 2015), 6 mit Negativbeleg ausgeschlossen (u.a. Codeliste der Temperaturanbieter — bei BDEW gültig, aber ohne Mitteilungs-, PID- oder Referenzbeleg; drei BDEW-Anwendungshilfen — siehe Kriterium-C-Präzisierung in 11e). Bei 6 von 10 ist erst die konsolidierte Fassung maßgeblich. K-1 um einen weiteren Fall ohne Mitteilungsbezug ergänzt: Standardlastprofile nach TU München 1.1 (nur über Kriterium C gehalten, referenziert von UTILMD Gas). Committet, Ticket #64 und PR #65 sind aktuell.

Ein neuer offener Punkt: **O-15** — bei der Codeliste der Lokationsbündelstrukturen passt die Anlage aus Mitteilung 32 nicht zur BDEW-Datei (das war die Konsultationsfassung); die verbindliche Anlage steht in Mitteilung 33, deren Link derzeit HTTP 404 liefert, ein Byte-Beleg ist also aktuell nicht möglich. Zusätzlich unterscheiden sich zwei Fehlerkorrekturstände dieser Codeliste, die nur einen Tag auseinander liegen, um den Faktor 7 in der Dateigröße — ungeklärt, nicht ungeprüft übernehmen.

*Rückfrage geklärt (2026-09-18):* Die neunte geprüfte Basisfassung ist der Lokationsbündel-Fall selbst — kein eigener, unbenannter Fall. Geprüft wurden neun Basisfassungen: die vier aus Mitteilung 56 sowie OBIS (Mitteilung 54), Artikelnummern (Mitteilung 51), Zeitreihentypen (Mitteilung 19), Ländercodes (Mitteilung 58) und Lokationsbündel (Mitteilung 32). Acht davon sind bytegleich; die eine Abweichung ist exakt O-15. Das zehnte in Etappe 4 aufgenommene Dokument (Standardlastprofile nach TU München 1.1) hat keine eigene BNetzA-Anlage und ist daher nicht Teil dieses Neun-Fassungen-Vergleichs. Etappe 4 gilt damit als vollständig abgeschlossen.

**Etappe 5 — Entscheidungsbaum-Diagramme (EBD)**
Je Prozess/Prüfidentifikator wie in Abschnitt 4B beschrieben, inklusive Querprüfung gegen die maßgebliche PID-Fassung (siehe 11e/11f).
*Status: abgeschlossen und bestätigt (Commit 9193ff9).* Maßgeblich am 01.10.2026: EBD und Codelisten 4.3, konsolidierte Fassung, Stand 23.06.2026 (831 Seiten); Basisfassung bytegleich mit der Mitteilung-56-Anlage, bleibt `ergänzend`. 364 EBD-Kennungen, 103 Codelisten-Kennungen, gegenüber der Basis neu hinzugekommen: E_0265. Querprüfung gegen die maßgebliche PID-Fassung: 285/285 referenzierte EBD-Kennungen vorhanden, 10/11 referenzierte Codelisten-Kennungen vorhanden (Ausnahme: neuer offener Punkt O-17), 79 von 364 EBD-Kennungen ohne jede PID-Referenz (Vormerkung für Abschnitt 16). O-16 im Zuge dieser Querprüfung aufgelöst. Details, methodische Besonderheit der EBD-Historie (Genehmigt- und Fehlerkorrektur-Einträge in einer gemeinsamen Liste) und O-17 siehe neuer Abschnitt 11f.

**Etappe 6 — Übertragungsweg / AS4 / API / XML**
Kategorie C aus Abschnitt 4, eigener Block — strukturell anders als EDIFACT-Nachrichtentypen (Transport-/Protokollregelungen statt Nachrichtenformat). Hier werden voraussichtlich die meisten Grenzfälle für die Aufnahmeregel (11e) auftreten, insbesondere bei Redispatch-XML-Dokumenten und API-Webdiensten, die Mitteilung 56 ausdrücklich nicht veröffentlicht hat — Kriterium-C-Prüfung (Dokumentname + Version, keine Gattungsnennung) hier besonders konsequent anwenden.

**Etappe 7 — Konsolidierung & Widerspruchsprüfung**
Über alle Etappen hinweg: offene Fragen aus Abschnitt 8 (insbesondere Frage 6, 7, 8) sammeln, BNetzA-vs-BDEW-Widersprüche auflisten, das `Regulatory State`-Objekt gemäß Abschnitt 15 final zusammenstellen (inklusive der in Abschnitt 9a/9b geklärten Entscheidung zum Verhältnis zu `RegulatoryVersion`, des dort offen gebliebenen Folgepunkts zur fehlenden Strom-RV, sowie der belegt/angenommen-Unterscheidung bei der Sparten-Zuordnung aus 11d — APERAK/CONTRL bleiben ohne Einzelnachweis, das muss sichtbar bleiben; O-16 ist bereits in Etappe 5 gegengeprüft und erledigt, keine Wiederholung nötig).

**Etappe 8 — Übergabebericht**
Zusammenfassender Bericht an den Menschen: was ist vollständig und belegt, was ist als `relevanz_unklar` markiert, was wurde bewusst nicht vertieft (mit Begründung), welche offenen Rückfragen bestehen. Muss die Kernbefunde K-1 (Mitteilungsbezug-Lücke) und K-2 (dritte Quelle bei Gas, Aufnahmeregel) prominent enthalten. Ergebnis als PR gegen das Ticket aus Abschnitt 0 einreichen. Kein Übergang zur fachlichen Analyse (Abschnitt 12/16) ohne Bestätigung dieses Berichts.
