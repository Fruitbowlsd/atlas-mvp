# Auftragstext (Referenzfassung)

> **Herkunft:** Wortlaut aus dem Claude-Projektdokument, Fassung vom **17.09.2026**
> („Erstellt: 2026-09-17, ergänzt um Etappenplan: 2026-09-17, ergänzt um Ticket-Pflicht:
> 2026-09-17"), am 17.09.2026 in die Arbeitssitzung übergeben und hier unverändert abgelegt.
> Zweck: Der Arbeitsstand im Repo soll nicht von der Projektreferenz abweichen (Ticket #64).
> Spätere Änderungen am Projektdokument sind hier **nicht** automatisch nachgeführt — bei
> einer neuen Fassung diese Datei ersetzen.
>
> **Ergänzungen aus der Arbeitssitzung**, die nicht im Text unten stehen, aber verbindlich
> sind (alle 17.09.2026): schriftliche Rollenabgrenzung „ersetzt" vs. „verworfen"
> ([`rollendefinition.md`](rollendefinition.md)); außerordentliche Veröffentlichung als
> eigener Fassungstyp mit Vermerk „kein Mitteilungsbezug" (O-11, bestätigt); die fehlende
> Strom-`RegulatoryVersion` als eigener offener Punkt P-1; die Statistik zu Fassungen ohne
> Mitteilungsbezug als Kernbefund K-1 für Etappe 8; SSQNOT als eigener offener Punkt vor
> Abschluss von Etappe 3.

---

Claude Code Auftrag: Regulatorischer Stand der Marktkommunikation zum 01.10.2026

Verhältnis zu anderen Projektdokumenten: Dieser Auftrag ist eigenständig und ersetzt nicht `Claude_Code_Prompt_FINAL.md`. Jener Auftrag beschreibt eine engere, weiterhin gültige Teilaufgabe (kapitelweiser Import von AHB Gas 1.1 in die bestehenden, aktuell leeren Wissensbasis-Tabellen). Der vorliegende Auftrag liegt davor: Er soll zunächst den vollständigen, belastbaren regulatorischen Stand zum Stichtag 01.10.2026 als Recherche-Grundlage ermitteln, bevor auf dieser Basis weiter fachlich extrahiert wird (vgl. Abschnitt 12/13 unten). Erstellt: 2026-09-17, ergänzt um Etappenplan: 2026-09-17, ergänzt um Ticket-Pflicht: 2026-09-17.

## Rolle

Du arbeitest wie ein sehr erfahrener Projektleiter für Marktprozesse bei einem deutschen Energieversorgungsunternehmen.
Deine Aufgabe ist es, für Atlas einen vollständigen, belastbaren und nachvollziehbaren regulatorischen Stand der Marktkommunikation zu ermitteln und strukturiert abzubilden.
Das Ziel ist nicht, lediglich die in einer BNetzA-Mitteilung verlinkten Dokumente herunterzuladen.
Das Ziel ist: Für einen eindeutig definierten regulatorischen Stichtag muss Atlas wissen, welche regulatorischen Dokumente und Versionen tatsächlich gültig sind, welche Dokumente zusammengehören, welche Fehlerkorrekturen bzw. konsolidierten Fassungen Vorrang haben und welche fachlichen Informationen daraus für Atlas relevant sind.
Jede Aussage muss auf einer konkreten Quelle und Dokumentversion nachvollziehbar sein.

## 0. Vorbereitung: Ticket anlegen

Bevor mit Etappe 0 des Anhangs begonnen wird: Lege im Repo ein neues Ticket/Issue für diesen gesamten Auftrag an (`gh issue create`, analog zum Workflow aus `Claude_Code_Prompt_FINAL.md`, Abschnitt 18), z.B. mit dem Titel "Regulatory State 01.10.2026: vollständigen regulatorischen Stand ermitteln". Übernimm den Etappenplan aus dem Anhang als Checkliste in die Issue-Beschreibung.
Arbeite während des gesamten Auftrags mit diesem einen Ticket: Nach jeder Etappe (siehe Abschnitt 13a und Anhang) den entsprechenden Checklisten-Punkt abhaken und den geforderten Zwischenstand als Kommentar im Ticket festhalten — nicht nur im Chat-Verlauf. Für die eigentliche Recherchearbeit einen eigenen Branch verwenden (z.B. `feature/regulatory-state-2026-10-01`); ob pro Etappe oder für den gesamten Auftrag ein PR erstellt wird, entscheidet sich danach, ob zwischendurch bereits committbare Artefakte (siehe Abschnitt 15a) entstehen. Das Ticket bleibt in jedem Fall die verbindliche, fortlaufende Quelle für den Bearbeitungsstand über mehrere Sessions hinweg — nicht der Chatverlauf, der zwischen Sessions verloren gehen kann.
Verweise am Ende jedes Etappenberichts auf die Ticketnummer, damit der Zusammenhang nachvollziehbar bleibt.

## 1. Grundverständnis der Formatumstellungen

Die reguläre Marktkommunikation kennt grundsätzlich zwei Umsetzungstermine pro Jahr:

* 01.04.
* 01.10.

Das Änderungsmanagement folgt dabei grundsätzlich diesem Muster:
Formatumstellung zum 01.10. Die Konsultation erfolgt typischerweise 6 Monate vor dem Stichtag. Die verbindliche Veröffentlichung erfolgt zum 01.04.
Beispiel:

* Mitteilung 55: Konsultation für Umsetzungstermin 01.10.2026 — Veröffentlichung: 02.02.2026
* Mitteilung 56: verbindlicher Stand für Umsetzungstermin 01.10.2026 — Veröffentlichung: 01.04.2026 — Inkrafttreten: 01.10.2026

Formatumstellung zum 01.04. Die Konsultation erfolgt typischerweise im August. Die verbindliche Veröffentlichung erfolgt zum 01.10. des Vorjahres.
Beispiel:

* Mitteilung 52: Konsultation für Umsetzungstermin 01.04.2026 — Veröffentlichung: 01.08.2025
* Mitteilung 54: verbindlicher Stand — Veröffentlichung: 01.10.2025 — Inkrafttreten: 01.04.2026

Diese Logik ist nicht nur textuell zu beschreiben, sondern muss als zeitliche Beziehung zwischen Konsultation, Veröffentlichung und Inkrafttreten in Atlas nachvollziehbar sein.

## 2. Ausgangspunkt: BNetzA

Beginne bei der Bundesnetzagentur: https://www.bundesnetzagentur.de/
Navigiere zu: Beschlusskammern → Beschlusskammer 6 → Aktuelles / Mitteilungen zu Datenformaten zur Abwicklung der Marktkommunikation.
Prüfe eigenständig, ob für die Sparte Gas neben Beschlusskammer 6 auch Beschlusskammer 7 relevante Mitteilungen zu Datenformaten der Marktkommunikation veröffentlicht, oder ob Formatmitteilungen für Strom und Gas ausschließlich gemeinsam über Beschlusskammer 6 laufen und Beschlusskammer 7 andere Themen (z.B. Netzzugang Gas) behandelt. Nimm keine der beiden Möglichkeiten ungeprüft an und dokumentiere, welche Kammer(n) tatsächlich als Quelle herangezogen wurden und warum.
Ermittle zunächst den relevanten Umsetzungstermin. Für den aktuellen Fall:
Regulatorischer Zielstand: 01.10.2026 Die dazugehörige verbindliche Mitteilung ist: Mitteilung Nr. 56 Veröffentlichung: 01.04.2026
Mitteilung 56 wird hier als bekannter Ausgangspunkt vorgegeben, weil sie bereits an anderer Stelle im Projekt verifiziert wurde. Das entbindet nicht davon, sie eigenständig gegenzuprüfen: Bestätige über die BNetzA-Seite selbst, dass Mitteilung 56 tatsächlich die aktuell gültige, verbindliche Mitteilung für den Umsetzungstermin 01.10.2026 ist, und prüfe, ob zwischenzeitlich eine neuere Mitteilung (z.B. eine Korrektur oder Mitteilung 57) veröffentlicht wurde, die Mitteilung 56 ganz oder teilweise ersetzt oder ergänzt. Melde explizit, falls das der Fall ist, statt stillschweigend bei Mitteilung 56 zu bleiben.
Nicht automatisch davon ausgehen, dass Mitteilung 56 alleine den vollständigen regulatorischen Stand enthält.

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

## 4. Alle Dokumente der Mitteilung erfassen

Für Mitteilung 56 müssen mindestens die folgenden Kategorien systematisch erfasst werden:
A. EDIFACT-Dokumente — alle dort aufgeführten: AHB, MIG, Allgemeine Festlegungen, PID / Anwendungsübersichten, API Guideline, Codelisten, sonstige EDIFACT-Dokumente.
Für jedes Dokument erfassen: Dokumenttyp, Nachrichtentyp, Sparte, Version, Veröffentlichungsdatum, Gültig-ab, Quelle, URL, Dateityp, Dokumentstatus, Zusammenhang mit Mitteilung, gegebenenfalls Vorgängerversion.
B. Entscheidungsbaum-Diagramme — erfassen: Version, Veröffentlichungsdatum, Gültigkeit, Codelisten, Entscheidungslogik, zugehörige Prozesse / Prüfidentifikatoren.
C. Regelungen zum Übertragungsweg — erfassen: Regelungen zum Übertragungsweg, AS4-Profil, Regelungen zum Übertragungsweg AS4, API-Webdienste / API-Regelungen, jeweilige Version, Gültigkeit.

## 5. Zweite regulatorische Quelle: BDEW MaKo

Die BNetzA-Quelle reicht nicht alleine aus. Deshalb muss anschließend die BDEW-MaKo-Plattform analysiert werden: https://www.bdew-mako.de/
Dort insbesondere: aktuell gültige Dokumente, zukünftig gültige Dokumente, gegebenenfalls historische Dokumente.
Die Dokumente müssen anhand ihres tatsächlichen Gültigkeitszeitraums bewertet werden: gültig von → gültig bis. Nicht nur anhand des Dateinamens.

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

## 7. PDF als Primärquelle für die Verifikation

Wenn mehrere Dateiformate verfügbar sind: PDF bevorzugen. Grund: Die PDF-Fassung soll als verlässliche Referenz für die tatsächlich veröffentlichte Dokumentversion dienen.
Andere Formate wie Word, Excel, XML dürfen zusätzlich analysiert werden, wenn sie fachlich benötigt werden. Sie ersetzen aber nicht automatisch die PDF-Referenz.

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

## 9a. Verhältnis zum bestehenden Atlas-Datenmodell

Atlas kennt aktuell eine grobkörnige `RegulatoryVersion` (z.B. "Mitteilung 56, gültig ab 01.10.2026"), der bislang der gesamte Requirement-Katalog als Ganzes zugeordnet wird. Der in diesem Auftrag beschriebene `Regulatory State` (siehe Abschnitt 15) ist feingranularer: er bündelt pro Stichtag die jeweils gültige Version jedes einzelnen regulatorischen Dokuments (AHB, MIG, Codeliste, EBD, ...), nicht nur einen einzigen Versionsstring.
Baue diesen Lauf so, dass er das Verhältnis zwischen beiden Konzepten explizit benennt, statt es stillschweigend zu vermischen: entweder wird `RegulatoryVersion` zum groben Alias für einen `Regulatory State` (1:1-Beziehung, z.B. `RegulatoryVersion.regulatory_state_id`), oder `Regulatory State` wird als komplett neue Ebene oberhalb von `RegulatoryVersion` eingeführt. Triff hierzu einen konkreten Vorschlag mit Begründung, aber führe noch keine Schemaänderung durch, ohne dass dieser Vorschlag bestätigt wurde.

## 10. Versionen niemals überschreiben

Atlas muss regulatorische Historie erhalten. Beispiel: UTILMD AHB Gas

* 1.1 — gültig: 01.04.2026 – 30.09.2026
* 1.2 — gültig: ab 01.10.2026

Die Version 1.1 darf nicht durch 1.2 ersetzt werden. Stattdessen: Dokument → Dokumentversion → Gültigkeitszeitraum.

## 11. Jede regulatorische Aussage braucht eine Provenienz

Für jedes relevante Artefakt speichern: Quelle, URL, Dokumentname, Dokumentversion, Veröffentlichungsdatum, Gültig ab, Gültig bis, Mitteilung, PDF-Datei, Hash der Datei, Analysezeitpunkt, gegebenenfalls Fehlerkorrekturstand, Prioritätsentscheidung, Begründung.
Beispiel: IFTSTA AHB — Version: 2.1, Gültig ab: 01.10.2026, Quelle: BNetzA / Mitteilung 56, PDF: vorhanden, Konsolidierte Fassung: ja, Fehlerkorrekturstand: ..., Maßgebliche Fassung: ja, Begründung: ...

## 12. Dokumente anschließend fachlich analysieren

Erst nachdem der regulatorische Stand vollständig bestimmt wurde, dürfen die Dokumente fachlich analysiert werden. Dabei insbesondere:
AHB: Prozesse, Prozessschritte, Prüfidentifikatoren, Muss-/Kann-/Abhängigkeitslogik, Bedingungen, Rollen, Nachrichten, Segmente, Datenelemente, Codelisten, Entscheidungslogik, Änderungshistorie.
MIG: Nachrichtenstruktur, Segmente, Datenelemente, Status, Pflichtigkeiten, Codelisten, Beispiele, Bemerkungen, Änderungen.
PID: Prüfidentifikator, Prozess, Prozessschritt, Nachricht, Rollen, Antwort-/Folgebeziehungen, AHB-Bezug.
EBD: Entscheidungsregeln, Bedingungen, Prüfentscheidungen, fachliche Auswirkungen.
Codelisten: Codeliste, Version, Code, Bedeutung, Gültigkeit, Bedingungen.

## 13. Ziel: Aufbau der ersten Atlas-Wissensbasis

Die erste regulatorische Wissensbasis von Atlas soll den vollständigen regulatorischen Stand zum 01.10.2026 abbilden. Der 01.10.2026 ist der erste verbindliche Stichtag, den Atlas als vollständigen regulatorischen Stand aufnimmt.
Der bisher gültige Stand zum 01.04.2026 muss nicht vollständig rekonstruiert oder als eigene Wissensbasis aufgebaut werden. Er wird nur dann herangezogen, wenn dies notwendig ist, um beispielsweise festzustellen: ob ein Dokument zum 01.10.2026 weiterhin gültig ist, welche Version eines Dokuments zum 01.10.2026 gilt, ob ein Dokument durch Mitteilung 56 geändert wurde, ob eine bestehende Version weitergeführt wird, ob eine neue Version eine alte Version ablöst.
Wichtig: Nicht unnötig den historischen Stand 01.04.2026 analysieren. Der Analysefokus liegt auf dem Zielzustand 01.10.2026.

## 13a. Etappierung statt Gesamtlauf

Dieser Lauf soll die vollständige Dokumentlandschaft zum Stichtag 01.10.2026 abdecken, das sind voraussichtlich mehrere Dutzend bis über hundert Einzeldokumente über alle Sparten, Nachrichtentypen und Dokumentkategorien hinweg. Arbeite das etappiert ab, nicht als einen einzigen großen Durchlauf. Der konkrete Etappenplan steht im Anhang am Ende dieses Dokuments — folge ihm als Task-Liste im in Abschnitt 0 angelegten Ticket, statt eine eigene Aufteilung zu improvisieren, damit Fortschritt zwischen mehreren Sessions vergleichbar bleibt.
Gib nach jeder Etappe einen Zwischenstand aus (analog zum bestehenden Prinzip "kapitelweise mit Zwischenstand" aus der Extraktionspipeline, siehe `Claude_Code_Prompt_FINAL.md`): Anzahl erfasster Dokumente, Anzahl offener/unklarer Fälle, Anzahl Widersprüche zwischen BNetzA und BDEW. Kein einzelner Sammelbericht erst am Ende.
Wenn absehbar wird, dass eine vollständige Abdeckung in diesem Lauf nicht erreichbar ist, priorisiere die Etappen in der im Anhang vorgegebenen Reihenfolge, und melde explizit, welche Etappen noch offen sind.

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

## 15a. Output-Format und Abgrenzung zur bestehenden Datenbank

Das Ergebnis dieses Laufs ist zunächst ein strukturierter Rechercheartefakt zur menschlichen Prüfung (z.B. eine strukturierte Markdown- oder JSON-Datei je Dokumentkategorie mit den in Abschnitt 11 geforderten Provenienzfeldern), kein direkter Schreibvorgang in die produktive Atlas-Datenbank.
Die bestehenden, aktuell leeren Tabellen (`MessageDefinition`, `MessageSegment`, `MessageField`, `CodeList`, `CodeListEntry`, `Testkonstellation`, `TestkonstellationSchritt`) werden in diesem Auftrag nicht befüllt — das ist laut Abschnitt 12 dieses Auftrags ausdrücklich ein nachgelagerter Schritt, der erst nach vollständiger und bestätigter Ermittlung des Regulatory State erfolgt.
Diese Rechercheartefakte werden im in Abschnitt 0 angelegten Ticket bzw. dessen Branch committet und über einen PR eingereicht (Issue anlegen, eigener Branch, PR mit Ergebnisbericht — siehe `Claude_Code_Prompt_FINAL.md`, Abschnitt 18), auch wenn dieser Lauf keine Code-Änderung, sondern nur Recherche-Artefakte liefert.

## 16. Fachliche Abbildung in Atlas

Erst nachdem der vollständige Regulatory State 01.10.2026 ermittelt wurde, werden daraus die Atlas-Fachobjekte abgeleitet: Prozesse, Prozessschritte, Rollen, Nachrichten, PI, Segmente, Datenelemente, Regeln, Codelisten, Abhängigkeiten, Anforderungen, Testfälle.
Dabei gilt weiterhin: Regulatorische Rohdaten ≠ Atlas-Semantik. Die Originaldokumente und ihre extrahierten Inhalte bleiben die belastbare Quelle. Die Atlas-Semantik wird darauf aufgebaut.

## Wichtigster Grundsatz für diesen Durchlauf

Baue jetzt den vollständigen regulatorischen Stand 01.10.2026. Rekonstruiere nicht unnötig den vollständigen Stand 01.04.2026. Nutze den alten Stand ausschließlich dort, wo er zur Bestimmung des neuen Stands erforderlich ist.
Das ist für den ersten Durchlauf auch wesentlich effizienter. Wir wollen am Ende nicht zwei Wissensbasen haben, sondern eine belastbare Ausgangsbasis für Atlas: Marktkommunikation 01.10.2026.

## Anhang: Konkreter Etappenplan

Verbindliche Reihenfolge für diesen Auftrag, geführt als Checkliste im in Abschnitt 0 angelegten Ticket. Jede Etappe endet mit einem kurzen Zwischenbericht (siehe Abschnitt 13a) als Ticket-Kommentar und, sofern der Projekt-Workflow das vorsieht, einem eigenen Commit/PR-Zwischenstand — nicht erst am Ende der gesamten Recherche.

**Etappe 0 — Fundament: Mitteilung 56 selbst erfassen** Mitteilung 56 (und ggf. neuere/korrigierende Mitteilungen) vollständig lesen. Alle darin referenzierten Dokumente als Rohliste erfassen — nur Metadaten (Name, Dokumenttyp, Sparte, Version, Link), noch keine Tiefenanalyse einzelner Dokumente. Gegenprüfung nach Abschnitt 2 (BK6/BK7, Aktualität von Mitteilung 56). Abnahmekriterium: vollständige Rohliste aller in Mitteilung 56 referenzierten Dokumente, je mit Kategorie-Tag (AHB / MIG / PID / EBD / Codeliste / Übertragungsweg / AS4 / API / XML / Sonstiges) und Sparte-Tag (Strom / Gas / beide). Diese Liste ist die Arbeitsgrundlage für alle folgenden Etappen — sie legt auch fest, welche Nachrichtentypen in Etappe 2/3 konkret bearbeitet werden, statt das vorab zu erraten.

**Etappe 1 — Pilot: UTILMD vollständig (Strom + Gas)** UTILMD zuerst und exemplarisch vollständig durchziehen (AHB Strom, MIG Strom, AHB Gas, MIG Gas), inklusive Fragenkatalog aus Abschnitt 8 und vollständiger Provenienz nach Abschnitt 11. Grund für die Sonderstellung: UTILMD ist komplex und zentral genug, um die gesamte Methodik (Lesefassung/Fehlerkorrektur-Priorität, PDF-Referenz, BDEW-Abgleich, Provenienz-Schema) einmal end-to-end zu validieren, bevor auf alle übrigen Nachrichtentypen skaliert wird. Abnahmekriterium: für alle vier UTILMD-Dokumente eine vollständig belegte Aussage "diese Version gilt ab 01.10.2026, weil ...", inklusive Auflösung etwaiger Lesefassungs-/Fehlerkorrektur-Konflikte.

**Etappe 2 — Übrige EDIFACT-Nachrichtentypen, Strom** Alle in Etappe 0 identifizierten Strom-Nachrichtentypen außer UTILMD, nach demselben Muster wie Etappe 1 abarbeiten. Abnahmekriterium: pro Nachrichtentyp derselbe Provenienz-Datensatz wie in Etappe 1.

**Etappe 3 — Übrige EDIFACT-Nachrichtentypen, Gas** Analog zu Etappe 2, für Gas.

**Etappe 4 — Querschnittsdokumente: PID/Anwendungsübersichten, Codelisten, Allgemeine Festlegungen** Diese sind meist nachrichtentyp- und sparten-übergreifend und werden als eigener Block bearbeitet, da sie sich nicht sauber einer einzelnen Etappe 2/3 zuordnen lassen.

**Etappe 5 — Entscheidungsbaum-Diagramme (EBD)** Je Prozess/Prüfidentifikator wie in Abschnitt 4B beschrieben.

**Etappe 6 — Übertragungsweg / AS4 / API / XML** Kategorie C aus Abschnitt 4, eigener Block — strukturell anders als EDIFACT-Nachrichtentypen (Transport-/Protokollregelungen statt Nachrichtenformat).

**Etappe 7 — Konsolidierung & Widerspruchsprüfung** Über alle Etappen hinweg: offene Fragen aus Abschnitt 8 (insbesondere Frage 6, 7, 8) sammeln, BNetzA-vs-BDEW-Widersprüche auflisten, das `Regulatory State`-Objekt gemäß Abschnitt 15 final zusammenstellen (inklusive der in Abschnitt 9a geforderten Entscheidung zum Verhältnis zu `RegulatoryVersion`).

**Etappe 8 — Übergabebericht** Zusammenfassender Bericht an den Menschen: was ist vollständig und belegt, was ist als `relevanz_unklar` markiert, was wurde bewusst nicht vertieft (mit Begründung), welche offenen Rückfragen bestehen. Ergebnis als PR gegen das Ticket aus Abschnitt 0 einreichen. Kein Übergang zur fachlichen Analyse (Abschnitt 12/16) ohne Bestätigung dieses Berichts.
