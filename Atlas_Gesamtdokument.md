# Atlas — Gesamtdokumentation

Ein zusammenhängendes Dokument für Vision, Produktarchitektur und die
vertiefte technische Ausarbeitung der Nachrichtensimulation. Ersetzt die
bisher getrennten Dateien (`Atlas_Konzept.md`, `Atlas_Produktarchitektur.md`,
`Atlas_Briefing_Nachrichtensimulation.md`, `Atlas_MVP_Referenz.md`) durch
eine einzige, vollständige Quelle.

**Hinweis zur Nummerierung:** Jeder Teil (A–D) behält seine ursprüngliche
Abschnittsnummerierung, damit bestehende Querverweise (z.B. "siehe
Abschnitt 11.2") weiterhin korrekt auf die Produktarchitektur in Teil B
zeigen. Innerhalb eines Teils sind die Nummern eindeutig, teilübergreifend
nicht — daher immer mit Teil-Buchstabe referenzieren (z.B. "Teil B,
Abschnitt 11.2").

## Inhaltsverzeichnis

- **Teil A — Vision & Konzept** (Executive-Zusammenfassung)
- **Teil B — Produktarchitektur** (das aktive, lebende Kernstück:
  Reifegradmodell, Regulatory Intelligence, Regulatorischer Stand &
  Assessment-Lifecycle, Multi-Tenancy, die vier großen Ausbaustufen,
  Gesamt-Feature-Übersicht & priorisierter Fahrplan)
- **Teil C — Vertiefung: Marktkommunikationssystem / Nachrichtensimulation**
  (detailliertes Briefing für die Zusammenarbeit mit einem externen
  Fachexperten zu Baustein 4 aus Teil B)
- **Teil D — Anhang: MVP-Referenz** (archiviert, technische Erstspezifikation
  des bereits gebauten und deployten MVP für Lieferbeginn Gas)

---

# Teil A — Vision & Konzept

## 1. Vision

Atlas ist eine Plattform, die Energieversorgungsunternehmen (EVUs) zeigt, wie
gut ihre Marktprozesse funktionieren — und zwar sowohl im Vorfeld einer
**regulatorischen Formatumstellung** als auch im Vorfeld eines
**technologischen Wechsels** (Systemmigration, z.B. S/4HANA). In beiden
Fällen stellt sich für die Geschäftsführung dieselbe Frage: *"Sind wir
bereit für den Produktivbetrieb?"*

Kein Zugriff auf interne Backend-Systeme der Kunden nötig — das ist der
bewusste Wettbewerbsvorteil (geringere Vertrauenshürde, schnellere
Time-to-Market, skalierbares Produkt statt Custom-Integration pro Kunde).

---

## 2. Kernprinzip: Kein Assessment ohne regulatorischen Stand

Jedes Assessment ist eindeutig einer **regulatorischen Version**
zugeordnet (z.B. "GeLi Gas 2.0, Konsultationsstand 01.08.2025" oder
"Mitteilung Nr. 56, gültig ab 01.10.2026"). Ein Score ist ohne diesen Bezug
nicht aussagekräftig — *"91 %"* beantwortet nichts, solange nicht klar ist,
**gegen was** gemessen wurde.

Jede Version bündelt den vollständigen Requirement-Katalog (Prüfidentifikatoren,
Anforderungen, Kritikalitäten) für ihren Stichtag.

---

## 3. Zwei unabhängige Achsen

Das Produkt deckt zwei Dimensionen ab, die unabhängig voneinander kippen
können:

```text
                    Regulatorischer Stand (Zeit)
                    Basis-Version ──────── künftige Version
                        │                        │
Technologie-   Alt-System │  Compliance          │  Readiness
Kontext                   │  (heutiger Zustand)  │  (Formatumstellung)
    │          ───────────┼──────────────────────────────────
    ▼          Neu-System │  Migrations-         │  beides gleichzeitig
               (Migration)│  readiness           │  = höchstes Risiko
```

Die Zeit-Achse (regulatorischer Stand) ist Kern des aktuellen MVP. Die
Technologie-Achse (`TechnologyContext`: welches System, welcher
Migrationsstatus) ist konzeptionell festgelegt, aber bewusst zurückgestellt
— das Datenmodell sieht das Feld bereits vor (`Assessment.technology_
context_id`, nullable), die UI/Logik folgt später.

---

## 4. Assessment-Lifecycle

### 4.1 Ein Kunde kann mehrere Assessments haben

Nicht "ein Kunde = ein Assessment". Ein Kunde kann Assessments gegen
mehrere Versionen parallel führen (z.B. Compliance gegen die Basis-Version
und gleichzeitig Readiness gegen eine künftige Version) und pro Version
über die Zeit mehrere aufeinanderfolgende Testläufe.

### 4.2 Assessment-Typ wird live berechnet, nicht gespeichert

Kein festes Label beim Erstellen — der Typ ergibt sich jederzeit aus dem
Verhältnis von `gueltig_ab` der Version zum heutigen Datum:

| Bedingung | Typ |
|---|---|
| `gueltig_ab` liegt in der Zukunft | Readiness |
| `gueltig_ab` ist die aktuell gültige (neueste Version mit `gueltig_ab ≤ heute`) | Compliance |
| Version wurde von einer neueren abgelöst | Historisch |

Ein heute als "Readiness" gestartetes Assessment wird am Stichtag automatisch
zu "Compliance" — ganz ohne dass sich am Datensatz selbst etwas ändert.
Das Dashboard zeigt standardmäßig das Assessment, dessen live berechneter
Typ gerade "Compliance" ist.

### 4.3 Zwei Phasen: "In Bearbeitung" → "Abgeschlossen"

| Phase | Verhalten |
|---|---|
| **In Bearbeitung** (Default) | Score live berechenbar, Requirement-Status frei editierbar — der normale Arbeitsprozess (z.B. 60 % → Lücken schließen → 78 %) |
| **Abgeschlossen** (nach explizitem Klick) | Score-Snapshot eingefroren (Zeitstempel + Werte), Requirement-Status schreibgeschützt |

Kein Wiederaufschrauben nach Abschluss. Weiterer Fortschritt = neues
Assessment gegen dieselbe Version → ergibt automatisch eine saubere
Historie:

```text
Testlauf #1 (Version: Mitteilung 56) — abgeschlossen 20.08.2026 — 30 %
Testlauf #2 (Version: Mitteilung 56) — abgeschlossen 05.09.2026 — 40 %
Testlauf #3 (Version: Mitteilung 56) — in Bearbeitung — aktuell 52 %
```

Keine Mindestschwelle zum Abschließen (auch ein niedriger, aber bewusst
gemeldeter Stand ist eine gültige Aussage). Stattdessen eine Warnung, falls
Requirements noch komplett unberührt sind ("12 von 133 Anforderungen wurden
noch nicht bearbeitet. Trotzdem abschließen?") — übersteuerbar.

### 4.4 UI: aktueller Score + Historie je Version

Nach Auswahl einer Version: oben prominent der aktuelle Stand (live, falls
ein Testlauf "in Bearbeitung" ist; sonst der neueste abgeschlossene mit
klarer Kennzeichnung "fest"), darunter chronologisch die abgeschlossenen
Testläufe dieser Version.

### 4.5 Zwei sich ergänzende Stabilitätsgarantien

- **Version fix pro Assessment** — das Referenzsystem (Requirement-Katalog)
  verschiebt sich nicht unter einem laufenden Assessment. Requirements
  einer Version mit mindestens einem existierenden Assessment werden im
  internen Kurations-Bereich schreibgeschützt.
- **In Bearbeitung → Abgeschlossen** — der Score selbst bewegt sich nach
  der offiziellen Momentaufnahme nicht mehr unbemerkt weiter.

Beantwortet damit zuverlässig: *"Warum hatten wir am 11.08.2026 einen Score
von 84 %?"*

---

## 5. Regulatory Intelligence: Formatumstellungen im Voraus analysieren

Zweiter großer Baustein, ergänzend zum Assessment-Kern: Atlas soll zeigen,
**was sich bei einer bevorstehenden Formatumstellung ändert** — bevor sie
produktiv wird.

### 5.1 Zwei Ebenen

- **Ebene 1 — Regulatory Intelligence** (Core, herstellerneutral): Was hat
  sich regulatorisch geändert? Quellen: BNetzA, BDEW, AHB, MIG, Codelisten.
- **Ebene 2 — Technology Intelligence** (optionale "Technology Packs"):
  Wie setzen einzelne Hersteller (SAP, Schleupen, Wilken, powercloud, …)
  das um? Rechtlich sensibler (Herstellerdokumente oft lizenzpflichtig) —
  nur Referenz/Kurzfassung/Link, nie Volltexte spiegeln.

### 5.2 MVP-Ansatz: kuratiert statt live analysiert

Kein automatischer Scraper/Live-Pipeline im MVP (zu fragil, zu teuer —
naive Volltextanalyse aller Dokumente einer Mitteilung läge bei
Millionen Tokens pro Durchlauf). Stattdessen:

- Interner Kurations-Bereich ("Formatänderungen"), Kanban-artiger
  Workflow: Zu prüfen → Entwurf → Veröffentlicht
- Reale Demo-Grundlage: BNetzA Mitteilung Nr. 55 (Entwurf) → Nr. 56
  (verbindliche Endfassung, gültig 01.10.2026) als Seed-Daten
- Kundenseitige "Atlas-Zusammenfassung" ist ein **manuell kuratiertes
  Textfeld**, nicht live generiert — fühlt sich für den Kunden gleich an,
  kostet aber keine API-Aufrufe

### 5.3 Spätere Ausbaustufe: kostengünstige Pipeline

Falls später automatisiert wird, KI bewusst erst am Ende der Kette:

```text
1. Monitoring (Hash-Vergleich)        → 0 Tokens
2. Extraktion (PDF/XLSX → Tabellen)   → 0 Tokens
3. Diff (alt vs. neu, zeilenweise)    → 0 Tokens
4. Fachliche Analyse                  → Anthropic API, NUR geänderte Zeilen
```

Reduziert Tokenverbrauch von Millionen auf Zehntausende pro Durchlauf.
Auslöser für den Bau dieser Pipeline: nicht ein Datum, sondern die
Bestätigung durch einen ersten Pilotkunden, dass das kuratierte Format
brauchbar ist.

### 5.4 Zusätzliche Geschäftsidee: Atlas API

Da es keine offizielle BNetzA/BDEW-API gibt, könnte Atlas diese Lücke
selbst füllen — als API, die Kundensysteme (Jira, SAP, interne Tools)
programmatisch abfragen können. Eigenständiger Produktbaustein für die
Pricing-Diskussion, nicht Teil der aktuellen technischen Umsetzung.

---

## 6. Reifegradmodell (Weg von Selbstauskunft zu automatisierter Prüfung)

| Stufe | Beschreibung | Objektivitätsgrad |
|---|---|---|
| 1 — Selbstauskunft ✅ | Status manuell pflegen, CSV-Import, SAP-Cloud-ALM-Anbindung | keiner |
| 2 — Einzelnachrichten-Simulation | Kunde schickt eine UTILMD-Nachricht, Atlas prüft Format/Pflichtfelder | erste Objektivität |
| 3 — Prozessketten-Simulation | Mehrere Nachrichten in Folge, Referenzkonsistenz + bewusste Fehlerfälle geprüft | hoch |

Kein Zugriff auf Kunden-Backends in keiner Stufe — Objektivität entsteht
über die Marktkommunikation selbst (simulierter Marktpartner), nicht über
einen Blick ins System des Kunden.

---

## 7. Aktueller Umsetzungsstand

- **Gebaut & deployt:** MVP-Dashboard (Wizard, Score/Heatmap, Marktkommunikations-
  Dreieck, Assessment-Bereich, CSV-/SAP-Cloud-ALM-Import, Roadmap-Seite,
  Formatänderungen-Kurationsbereich mit Kanban-Board), Passwortschutz,
  Railway-Deployment.
- **Als Fundament als Nächstes geplant:** Abschnitt 4 dieses Dokuments
  (mehrere Assessments pro Kunde, Versionswahl im Wizard, berechneter
  Assessment-Typ, Lifecycle In Bearbeitung/Abgeschlossen) — bewusst vor der
  Formatänderungen-Kundenansicht, damit letztere auf korrektem Fundament
  aufbaut.
- **Bewusst zurückgestellt:** TechnologyContext + Matrix-UI, automatisierte
  Monitoring-/Analyse-Pipeline, NB/MSB als Marktrolle (echte
  Scope-Erweiterung über "Lieferant" hinaus).

---

## 8. Leitprinzipien, die sich durch das ganze Konzept ziehen

1. **Kein Assessment ohne regulatorischen Stand.**
2. **Unveränderlichkeit statt rückwirkender Verfälschung** — abgeschlossene
   Assessments und ihre Requirement-Grundlage sind fest.
3. **System schlägt vor, Mensch bestätigt** — gilt für Import-Matching
   genauso wie für KI-gestützte Änderungsvorschläge.
4. **Kein Zugriff auf Kunden-Backends** — Objektivität über Marktkommunikation,
   nicht über Systemzugriff.
5. **Kosten bewusst steuern** — klassische Verfahren filtern, KI nur auf
   das wirklich Neue ansetzen.

---

# Teil B — Produktarchitektur

*Das aktive, lebende Kernstück dieses Dokuments — hier wird der Produktaufbau laufend fortgeschrieben.*

## 10. Integrationsstufen: Weg von der Selbstauskunft zur automatisierten Prüfung

Diese Roadmap beantwortet die strategische Frage "Wie wird Atlas mehr als ein
Selbstauskunfts-Dashboard?" — und damit auch das eigentliche Wertversprechen
gegenüber EVUs: weniger manuelle Pflegearbeit, objektivere Ergebnisse.

**Zentrales Prinzip, das über alle Stufen gilt:** Kein Zugriff auf interne
Backend-Systeme der Kunden. Das ist der bewusste Wettbewerbsvorteil von Atlas
(geringere Vertrauenshürde, schnellere Time-to-Market, echtes skalierbares
Produkt statt Custom-Integrationsprojekt pro Kunde). Objektivität wird
stattdessen über die Marktkommunikation selbst erreicht — nie über einen Blick
ins System des Kunden.

### Stufe 1 — Selbstauskunft (✅ aktueller MVP-Stand)

Nutzer pflegt Implementierungs-/Test-/Nachweis-Status manuell im Dropdown.

- **Objektivitätsgrad:** keiner — reine Selbstauskunft
- **Aufwand:** bereits gebaut
- **Zweck:** schneller Einstieg, funktioniert ohne jede Integration beim Kunden,
  gute Grundlage für die Geschäftsführungs-Demo

*Komfort-Ausbaustufen innerhalb Stufe 1 (kein Objektivitätsgewinn, nur weniger
Tipparbeit):*
- **1a — CSV/Excel-Bulk-Import:** Testfälle als Datei hochladen statt einzeln
  im Dropdown erfassen. Aufwand: gering (1–2 Wochen).
- **1b — Jira/Xray/TestRail-Anbindung:** Status wird aus einem bereits beim
  Kunden genutzten Test-Management-Tool gezogen. Bleibt Selbstauskunft, nur an
  anderer Stelle erfasst. Aufwand: mittel pro Tool (2–4 Wochen je Konnektor),
  steigt mit jeder weiteren Plattform.

### Stufe 2 — Einzelnachrichten-Simulation

Kunde schickt eine einzelne UTILMD-Nachricht (z.B. Anmeldung) an Atlas über
SFTP oder eine Upload-API. Atlas parst sie und antwortet.

- **Was neu geprüft wird:** Formatgültigkeit, Pflichtfelder, korrekter
  Prüfidentifikator — aber isoliert, ohne Bezug zu vorherigen/folgenden
  Nachrichten
- **Neue technische Bausteine:** UTILMD-Parser/Serializer (EDIFACT und/oder
  XML), Transport-Adapter (SFTP-Server oder Upload-Endpoint)
- **Objektivitätsgrad:** erste echte Objektivität — Atlas prüft selbst, statt
  einer Behauptung zu vertrauen
- **Aufwand-Einschätzung:** mehrwöchiges eigenständiges Projekt (grobe
  Hausnummer: 6–10 Wochen für ein Team, abhängig davon ob EDIFACT, XML oder
  beide Formate unterstützt werden müssen)

### Stufe 3 — Prozessketten-Simulation

Mehrere Nachrichten desselben Prozesses werden nacheinander verarbeitet, in
einer zustandsbehafteten Testsession.

- **Was neu geprüft wird:**
  - Referenzdaten (Zählpunkt/Marktlokation, Vertragskonto, Kundennummer)
    bleiben über die gesamte Nachrichtenkette konsistent
  - Bewusst eingeschleuste Fehlerfälle (z.B. doppelte Anmeldung, falsche
    Zählpunktnummer) werden korrekt abgelehnt
  - Damit wird interne Verarbeitungskorrektheit **indirekt über die
    Nachrichtenkette** geprüft — ganz ohne Backend-Zugriff
- **Neue technische Bausteine:** Session-/State-Machine-Engine (merkt sich
  Vorgangsnummern und Referenzdaten über mehrere Schritte), Mapping-Layer
  Testergebnis → bestehender Requirement-Katalog
- **Objektivitätsgrad:** hoch — das ist der eigentliche Kern des
  Wertversprechens ("Qualität automatisiert messen, Manpower beim Kunden
  sparen")
- **Aufwand-Einschätzung:** baut auf Stufe 2 auf, zusätzlich 6–8 Wochen für
  Zustandslogik und Fehlerfall-Bibliothek

### Was sich im Datenmodell durch Automatisierung ändert

Wichtige Erkenntnis: Die vier Qualitäts-Unterdimensionen aus Abschnitt 22
verschmelzen bei automatisierter Prüfung zu weniger, dafür objektiveren
Signalen:

| Dimension (heute, manuell) | Automatisiert (Stufe 2/3) |
|---|---|
| Implementierung: Dropdown "ja/nein" | Hat das System strukturell gültig geantwortet? |
| Testqualität: Dropdown "getestet ja/nein" | entfällt als eigene Dimension — der Simulator-Lauf **ist** der Test |
| Nachweisqualität: manueller Upload | Nachrichtenverkehr (Request/Response-Protokoll) ist automatisch der Nachweis |
| Aktualität: Platzhalterwert | exakt berechenbar aus Zeitstempel des letzten automatisierten Laufs |

**Vorbereitende, risikoarme Datenmodell-Änderung schon jetzt möglich:**
`AssessmentRequirement` um zwei Felder ergänzen — `data_source` (`"manuell"` /
`"automatisiert"`) und `last_automated_run_at` — damit später erkennbar ist,
welcher Anteil des Scores schon objektiv geprüft ist, ohne das bestehende
Modell umzubauen, wenn Stufe 2/3 kommen.

### Empfehlung für die Geschäftsführungs-Demo

Das aktuelle Dashboard (Stufe 1) bleibt die Demo-Grundlage — das läuft und
lässt sich zeigen. Stufen 2 und 3 gehören als **Roadmap mit Zeithorizont**
in die Präsentation, nicht in den aktuellen Code: "Hier ist, was schon läuft.
Hier ist der Plan, wie wir Schritt für Schritt Manpower beim Kunden einsparen."
Das zeigt Weitblick, ohne etwas zu versprechen, das technisch noch nicht steht.

---

## 11. Regulatory Intelligence: Formatumstellungen im Voraus analysieren

Neue strategische Ausbaustufe (Entscheidung vom heutigen Tag): Atlas soll eine
bevorstehende Formatumstellung analysieren können, bevor sie produktiv wird —
und daraus konkret ableiten, was sich für einen einzelnen Kunden ändert
("Delta"). Zwei-Ebenen-Architektur, wie besprochen:

- **Ebene 1 — Regulatory Intelligence (Core, herstellerneutral):** Was hat
  sich regulatorisch geändert? Quellen: BNetzA, BDEW, AHB, MIG, Codelisten,
  Formatbeschreibungen.
- **Ebene 2 — Technology Intelligence (optionale "Technology Packs"):** Wie
  setzen einzelne Systeme (SAP Utilities, Schleupen, Wilken, powercloud, ...)
  diese Änderungen um? Rechtlich sensibler (SAP Notes u.ä. sind
  lizenzpflichtig/nicht frei weiterverbreitbar) — deshalb: nur Referenz,
  Titel und eigene Kurzfassung speichern, nie Volltexte spiegeln.

**Entscheidung für den ersten Umsetzungsschritt:** Ebene 1 zuerst, ohne
Scraper — stattdessen eine interne **Kuratoren-Oberfläche**, in der
regulatorische Änderungen manuell/halbautomatisch erfasst werden. Kein
Scraper gegen edi-energy.de im MVP (fragil, wartungsintensiv, lohnt sich erst
nach Validierung beim Kunden).

### 11.1 Faktenlage zu den Quellen (recherchiert)

- Weder BNetzA noch BDEW/edi-energy.de bieten eine offizielle API. Dokumente
  werden als PDF/DOCX/XLSX zu festen Stichtagen veröffentlicht (i.d.R. April/
  Oktober, plus außerordentliche Veröffentlichungen), begleitet von
  nummerierten BNetzA-"Mitteilungen" mit vollständiger Dokumentenliste.
- Es existiert bereits Open-Source-Tooling für genau dieses Problem (Projekt
  Hochfrequenz): `edi_energy_scraper` (spiegelt edi-energy.de strukturiert
  nach Format-Version) und `kohlrahbi` (wandelt AHB-Tabellen aus PDF/DOCX in
  maschinenlesbare Daten um). Kein Muss, aber guter Referenzpunkt/Inspiration
  statt bei Null anzufangen.
- Rechtlich unkritisch: Diese Dokumente sind von BNetzA/BDEW explizit zur
  branchenweiten Umsetzung veröffentlicht — anders als SAP Notes (Ebene 2)
  keine vergleichbare Zugriffsbeschränkung.

### 11.2 Pipeline-Architektur (KI erst am Ende, nicht am Anfang)

Zentrale Design-Entscheidung zur Token-/Kostenkontrolle: klassische,
kostenlose Verfahren filtern zuerst, die Anthropic-API wird nur auf das
wirklich Neue angesetzt.

```text
1. Monitoring          [kein LLM] Datei-Hash/Checksumme vs. letzten bekannten
                        Stand. Unveraendert -> Pipeline stoppt, 0 Tokens.
2. Strukturelle         [kein LLM] AHB-Tabellen (PIs, Codes, Pflichtfelder)
   Extraktion           in strukturierte Zeilen umwandeln (Parsing, an
                        Kohlrahbi-Ansatz angelehnt).
3. Struktureller Diff   [kein LLM] Klassischer Zeilenvergleich alte vs. neue
                        extrahierte Tabelle -> nur echte Aenderungen bleiben.
4. LLM-Analyse          [Anthropic API] NUR die geaenderten Zeilen aus Schritt 3
                        werden geschickt (>95% weniger Tokens als Volltext-
                        Analyse). Aufgabe: Kategorisieren, Risiko/Aufwand
                        schaetzen, Kurzbeschreibung fuer Kurator formulieren.
5. Kuration             [Mensch] Kurator prueft/korrigiert den Vorschlag in
                        der Kuratoren-UI, bevor er live fuer Kunden sichtbar wird.
```

Weitere Kostenhebel: Prompt Caching für feste Kontextteile (Schema,
Kategorien, Risikoraster), Batch API statt Echtzeit-Einzelaufrufe (Kuration
ist nicht zeitkritisch), kleineres Modell (z.B. Haiku) für einfache
Kategorisierung, größeres nur bei mehrdeutigen Fällen.

**Wichtig für die Umsetzung:** Der Anthropic-API-Key gehört ins **Atlas-
Backend** als Umgebungsvariable (z.B. `ANTHROPIC_API_KEY`), erstellt über
console.anthropic.com — unabhängig vom claude.ai-Chat-Zugang.

### 11.3 Datenmodell (Vorschlag)

```text
RegulatoryChange (Ebene 1 - Core, herstellerneutral)
├── titel, beschreibung, kategorie
│   (neuer_prozess | neues_pflichtfeld | neuer_code | neue_qualitaetsregel | neuer_testfall)
├── betroffene_process_group_id, betroffener_pi_id (Verknuepfung zu bestehendem Katalog)
├── risiko (hoch/mittel/niedrig), aufwand (hoch/mittel/niedrig)
├── quelle_url (Link auf BNetzA-Mitteilung/edi-energy.de-Dokument)
├── status (entwurf | veroeffentlicht)
└── regulatory_version_id (Verknuepfung zur betroffenen/neuen Version)

TechnologySystem (Ebene 2 - optionaler Pack, z.B. "SAP Utilities")
TechnologyReleaseNote (nur Referenz+Titel+eigene Kurzfassung+Link, kein Volltext)
RegulatoryChangeTechnologyMapping (Verknuepfung: Aenderung <-> Note)
```

### 11.4 Kuratoren-Oberfläche (Konzept, Vorschau bereits gezeigt)

Rein intern, nicht Teil der Kunden-Ansicht. Formular zum Anlegen einer
`RegulatoryChange` (Titel, Kategorie, betroffene Prozessgruppe/PI,
Risiko/Aufwand, Beschreibung, Quelle) plus Liste bestehender Änderungen
(Karten mit Risiko-Farbcodierung und Status-Badge "Entwurf"/"Veröffentlicht").

### 11.5 Kunden-Ansicht (Zielbild, aus der ursprünglichen Idee)

Kunde klickt auf ein Release (z.B. "Release Oktober 2027") und sieht: Anzahl
regulatorischer Änderungen, betroffene Prozesse, Risiko-Einstufung,
geschätzter Aufwand, betroffene Teams, Anzahl neuer Testfälle — und (sobald
Ebene 2/Technology Packs dazugebucht sind) die konkret betroffenen
Herstellerinformationen (z.B. "SAP: 8 relevante Notes").

**Der eigentliche Delta-Impact für einen Kunden:** Von den Requirements des
Kunden mit Status "implementiert" bleiben X gültig, Y werden durch
`RegulatoryChange`-Einträge neu benötigt (unabhängig vom bisherigen Stand),
Z entfallen. Score-Prognose: "Euer Abdeckungsgrad würde unter dem neuen
Stand von aktuell A% auf geschätzt B% fallen."

### 11.6 Zusätzliche Geschäftsidee: Atlas API

Da es keine offizielle BNetzA/BDEW-API gibt, könnte Atlas diese Lücke selbst
füllen — nicht nur als Dashboard, sondern als **eigene API**, die Kunden-
Systeme (Jira, SAP, interne Tools) programmatisch abfragen können ("gib mir
alle regulatorischen Änderungen der letzten 6 Monate für Lieferbeginn Gas
als JSON"). Eigenständiger Produktbaustein, ergänzend zur UI — festhalten
für die Produkt-/Pricing-Diskussion, noch nicht Teil der technischen
Umsetzung in der nächsten Session.

### 11.7 Nächste Schritte (für die neue Session/Claude Code)

1. `RegulatoryVersion`-Konzept erweitern: mehrere Versionen parallel im
   System (aktuell nur eine).
2. Datenmodell aus 11.3 implementieren (Backend).
3. Kuratoren-UI (Formular + Liste) bauen, siehe 11.4.
4. Diff-Logik zwischen zwei Versionen (klassisch, kein LLM) als Vorstufe.
5. Anthropic-API-Anbindung für Schritt 4 der Pipeline (11.2) — Prompt-Design
   für Kategorisierung/Risiko-Einschätzung/Kurzbeschreibung.
6. Kunden-Ansicht "Formatumstellungs-Impact" (11.5) inkl. Score-Delta.

### 11.8 MVP-Scope-Entscheidung: reale Demo-Daten statt Live-Monitoring

Finale Entscheidung (nach Testlauf des ersten Umsetzungsversuchs): Kein
allgemeiner/wiederkehrender Monitoring-Job gegen BNetzA/BDEW im MVP. Zu
fragil und nicht der Kern dessen, was für die Demo gezeigt werden muss.

Stattdessen: Die beiden bereits bekannten, echten BNetzA-Mitteilungen als
feste Seed-/Demo-Daten, damit die Delta-Analyse mit echtem Inhalt statt
erfundenen Platzhaltern arbeitet:

- **Mitteilung Nr. 55** (Entwurf/Konsultation) — Vorstufe
- **Mitteilung Nr. 56** (verbindliche Endfassung, gültig ab 01.10.2026) —
  Zielversion, Quelle:
  https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_56/Mitteilung_Nr_56.html

Als `RegulatoryVersion 2` angelegt, neben der bestehenden GeLi Gas 2.0
(01.08.2025). Ein bis drei `RegulatoryChange`-Beispieleinträge dazu manuell
kuratiert (z.B. neue Anwendungsübersicht der Prüfidentifikatoren 4.0,
Änderungen an Codeliste-Konfigurationen), nicht automatisch extrahiert.

Korrektur am Sidebar-Bereich: heißt **"Formatänderungen"** (nicht "Kuration
(intern)"/"Kuration"), Layout ist ein **Kanban-Board** (Zu prüfen / Entwurf /
Veröffentlicht), kein Formular+Liste. Kein "Jetzt prüfen"-Button für
automatisches Nachladen — das manuelle Anlegen über das Formular reicht für
den MVP. Ein späterer automatisierter Monitoring-Job (Abschnitt 11.7,
Punkt 1) bleibt als Ausbaustufe im Backlog, ist aber nicht Teil dieser
Umsetzung.

### 11.9 Fachliche Zielspezifikation der Analyse-Engine

Es liegt eine detaillierte fachliche Spezifikation vor (12-Phasen-Modell aus
Projektleiter-Perspektive), die beschreibt, wie eine regulatorische
Veröffentlichung vollständig analysiert werden soll. Diese ist **nicht** als
Auftrag an ein Coding-Werkzeug zu verstehen, sondern als:

1. **Systemprompt-Design für die Analyse-Engine** — also für das LLM, das
   später im Atlas-Backend über die Anthropic-API läuft (Schritt 4 der
   Pipeline aus 11.2).
2. **Fachliche Zielspezifikation** für das Datenmodell.

Besonders wertvolle Elemente, die ins Datenmodell übernommen werden sollten:

- **Durchgängige Traceability-Kette:** Regulatorische Quelle → Änderung →
  Anforderung → Testfall → Testergebnis. Das ist der eigentliche
  Unterschied zu einer reinen Dokumentensammlung.
- **Dreiwertige Relevanz** statt binär: `relevant` / `nicht_relevant` /
  **`relevanz_unklar`**. Eine unklare Relevanz darf nie stillschweigend zu
  "nicht relevant" werden — sonst entstehen unbemerkte Lücken im Score.
- **Atomare Zerlegung von Änderungen:** nicht "UTILMD wurde geändert",
  sondern je ein Eintrag pro Pflichtfeld/Code/Bedingung. Passt exakt zur
  Granularität unseres bestehenden Requirement-Katalogs.
- **Trennung von Originalaussage und Interpretation** in jedem Analyse-
  ergebnis, plus explizites Kennzeichnen von Unsicherheiten und nicht
  auffindbaren Dokumenten (kein stillschweigendes Übergehen).
- **Keine Readiness-Bewertung ohne Kundendaten/Nachweise** — deckt sich mit
  unserem bestehenden Prinzip aus Abschnitt 22.

**Anpassung (Entscheidung vom heutigen Tag): Phase 1 dynamisch statt fest
vorgegeben.** Die ursprüngliche Fassung ging von einer fest vorgegebenen
Mitteilungsnummer ("im konkreten Fall: BNetzA Mitteilung Nr. 56") aus. Besser:
die Analyse-Engine ermittelt die aktuell relevante Mitteilung **selbst**,
statt dass ein Kurator die Nummer von Hand recherchieren und eintragen muss.

Das ist kein Widerspruch zur MVP-Scope-Entscheidung aus 11.8 (kein
automatischer Hintergrund-Monitoring-Job) — der Unterschied: Phase 1 läuft
weiterhin nur innerhalb eines vom Kurator bewusst angestoßenen einzelnen
Analyse-Laufs ("Atlas-Analyse starten"), nicht als wiederkehrender Cronjob.
Technisch über Web-Suche als Tool der Analyse-Engine machbar, bleibt im
"billigen" Teil der Pipeline (Übersichtsseite lesen + höchste Nummer
erkennen), nicht im teuren Volltext-Dokumententeil.

Angepasste Phase 1 (ersetzt die ursprüngliche feste Vorgabe):

```text
Phase 1 – Aktuelle BNetzA-Mitteilung selbst ermitteln

Ermittle zunächst eigenständig, welche BNetzA-Mitteilung zu Datenformaten
aktuell die für die anstehende Formatumstellung relevante ist -- die Nummer
wird NICHT vorgegeben.

Vorgehen:
1. Suche die offizielle Übersichtsseite der Bundesnetzagentur für
   "Gemeinsame Mitteilungen zu Datenformaten" (bundesnetzagentur.de/
   datenformate-energie oder gleichwertig).
2. Identifiziere die Mitteilung mit der höchsten Nummer, die für die
   angegebene Sparte (z.B. Gas) und den betrachteten Prozess relevant ist.
3. Prüfe, ob es sich um eine verbindliche Endfassung oder eine noch offene
   Konsultation handelt, und ob ggf. eine neuere Mitteilung dieselbe
   Konsultation bereits final abgeschlossen hat (Vorgänger-/Nachfolger-
   Beziehung, Beispiel: Mitteilung 55 -> 56).
4. Dokumentiere explizit: gefundene Mitteilungsnummer, warum diese als
   aktuell relevant eingestuft wurde, und wie sicher diese Einschätzung ist.
   Unsicherheit (mehrere infrage kommende Mitteilungen, unklare Sparten-
   Zuordnung) ausdrücklich kennzeichnen statt stillschweigend anzunehmen.

Danach unverändert weiter mit den bisherigen Phasen 2-12, jetzt bezogen auf
die selbst ermittelte Mitteilung.
```

Die übrigen elf Phasen (vollständiges Original-Dokument, siehe Chatverlauf
vom heutigen Tag) bleiben inhaltlich unverändert gültig als Zielspezifikation.

### 11.10 Kostenabschätzung und pragmatisches Vorgehen (Token-Budget)

**Das Problem bei naiver Umsetzung:** Die Dokumente einer Mitteilung (18+
Dokumente, AHBs mit mehreren hundert Seiten / 3–5 MB PDF) komplett an die
Anthropic-API zu schicken, liegt grob bei 150.000–250.000 Tokens **pro
großem AHB**. Über alle Dokumente einer Mitteilung: **2–4 Mio. Tokens** —
und für einen echten Versionsvergleich bräuchte man alte *und* neue Fassung,
also nochmal das Doppelte. Pro Analysedurchlauf ein spürbarer dreistelliger
Eurobetrag, wiederkehrend bei jeder Formatumstellung.

**Deshalb die Reihenfolge aus 11.2 — die KI steht bewusst an Schritt 4:**

| Schritt | Wer macht's | Tokenverbrauch |
|---|---|---|
| 1. Monitoring (gibt's was Neues?) | Hash-/Checksummen-Vergleich | 0 |
| 2. Extraktion (PDF/XLSX-Tabellen → strukturierte Zeilen) | Parser (kohlrahbi-Ansatz) | 0 |
| 3. Diff (alt vs. neu, zeilenweise) | Klassischer Textvergleich | 0 |
| 4. Fachliche Analyse | **Anthropic API** | nur die geänderten Zeilen |

Nach einer Formatumstellung ändern sich in einem AHB mit ~5.000
Tabellenzeilen typischerweise nur einige Dutzend bis wenige Hundert Zeilen.
Werden nur diese geschickt: **Zehntausende statt Millionen Tokens** — Cent-
statt Hunderter-Beträge pro Durchlauf.

**Ehrlicher Vorbehalt:** Diese Ersparnis funktioniert nur, wenn Schritt 2
(strukturierte Extraktion) tatsächlich existiert. Die ist aktuell **nicht
gebaut** und ist das eigentliche Arbeitspaket, kein Nebenschauplatz. Ohne
Extraktion bleibt nur "ganzes PDF an die API" — also genau das teure
Szenario.

**Empfohlenes Vorgehen (statt gleich der vollen Pipeline):**

Erst **ein einziges Dokument** durchspielen, bevor auf 18 Dokumente
hochskaliert wird. Gut geeignet: die **"Anwendungsübersicht der
Prüfidentifikatoren 4.0"** — liegt laut Mitteilung 55/56 auch als **XLSX**
vor (nicht nur PDF), ist also deutlich einfacher zu parsen als ein
vollständiger AHB. Daran lässt sich realistisch messen:

- wie viel nach Extraktion + Diff tatsächlich übrig bleibt
- was ein Analyse-Durchlauf real kostet
- ob die Ergebnisqualität für die Kuration ausreicht

Erst danach entscheiden, ob und wie auf die übrigen Dokumenttypen (AHB, MIG,
Codelisten) ausgeweitet wird.

---

## 12. Regulatorischer Stand & Assessment-Lifecycle (konsolidiertes Konzept)

Zu Ende gedachtes Konzept aus einer längeren Diskussionsrunde, ausgelöst durch
ein extern zugeliefertes Dokument zum "Regulatorischen Stand". Dies ist das
**Fundament**, das vor der Formatänderungen-Kundenansicht (Abschnitt 11)
gebaut werden muss, da letztere sonst auf der falschen Annahme "ein Kunde =
ein Assessment" aufbauen würde.

### 12.1 Grundprinzip: kein Assessment ohne regulatorischen Stand

Übernommen aus dem Zulieferer-Dokument: Jedes Assessment ist eindeutig einer
`RegulatoryVersion` zugeordnet (bei uns bereits vorhanden:
`regulatory_version_id`). Ein Score ist nur mit diesem Bezug aussagekräftig
("91 % — aber gegen welchen Stand?").

### 12.2 Zwei unabhängige Achsen — nicht nur die Zeit-Achse

Wichtige Ergänzung zum Zulieferer-Dokument, die dort fehlte: Atlas soll laut
ursprünglicher Positionierung EVUs sowohl bei **Formatumstellungen** als auch
bei **technologischem Wechsel** unterstützen (Abschnitt 1). Das
Zulieferer-Dokument deckt nur die Zeit-Achse (regulatorischer Stand) ab.

```text
                    Regulatorischer Stand (Zeit)
                    Basis-Version ──────── künftige Version
                        │                        │
Technologie-   Alt-System │  z.B. Compliance     │  z.B. Readiness
Kontext                   │  (heute)             │  (Formatumstellung)
    │          ───────────┼──────────────────────────────────
    ▼          Neu-System │  Migrations-         │  beides gleichzeitig
               (Migration)│  readiness           │  = höchstes Risiko
```

**Vorgeschlagene neue Entität** `TechnologyContext` (kundenspezifisch, nicht
zu verwechseln mit der herstellerweiten "Ebene 2"/Technology Packs aus
Abschnitt 11): `id`, `customer_id`, `name` (z.B. "SAP S/4HANA Utilities"),
`hersteller`, `status` (aktuell_im_einsatz | migration_laeuft | geplant),
`ziel_produktivsetzung` (Datum, optional).

**Status:** Konzeptionell festgehalten, bewusst **zurückgestellt** — wird
erst nach dem Fundament (12.3–12.6) umgesetzt, um den nächsten Schritt klein
zu halten. `Assessment.technology_context_id` (nullable) ist im Datenmodell
vorzusehen, aber vorerst ungenutzt.

### 12.3 Mehrere Assessments pro Kunde (strukturelle Voraussetzung)

Aktuell erstellt der Wizard genau ein Assessment pro Kunde. Das reicht nicht,
sobald mehrere `RegulatoryVersion`-Einträge existieren. Notwendig:

- Ein Kunde kann mehrere Assessments haben (gegen dieselbe oder
  unterschiedliche Versionen).
- Neuer Endpunkt: weiteres Assessment für einen **bestehenden** Kunden
  starten (Versionswahl, siehe 12.4), ohne neuen Kunden anzulegen.
- Einfache Liste "Assessment-Historie" pro Kunde (Version, Typ, Datum,
  Score) — zunächst als schlichte Aufzählung, keine Matrix-UI.

### 12.4 Versionswahl im Wizard statt implizite erste Version

Der Wizard fragt explizit: *"Gegen welchen Stand soll Atlas Ihre Qualität
messen?"* — Radio-Auswahl, dynamisch befüllt aus allen nicht-archivierten
`RegulatoryVersion`-Einträgen, z.B.:

```text
○ GeLi Gas 2.0 / UTILMD Gas G1.1 (aktueller Stand)
○ Mitteilung Nr. 56 / gültig ab 01.10.2026 (künftig)
```

Ersetzt die bisherige feste "erste Version"-Logik beim Anlegen eines
Assessments (sowohl im Wizard für neue Kunden als auch im Endpunkt aus 12.3
für bestehende Kunden).

### 12.5 Assessment-Typ: berechnet, nicht gespeichert

Wichtige Design-Entscheidung nach Diskussion: **kein** festes
`assessment_type`-Feld, das einmalig beim Erstellen gesetzt und dann
eingefroren wird — das würde bei Zeitablauf falsch werden (ein heute als
"Readiness" angelegtes Assessment gegen eine künftige Version ist nach deren
Stichtag faktisch der aktuelle Compliance-Nachweis, ohne dass sich am
Assessment selbst etwas geändert hätte).

**Stattdessen wird der Typ bei jeder Anzeige live aus dem Verhältnis
zwischen `RegulatoryVersion.gueltig_ab` und dem heutigen Datum abgeleitet:**

```text
- gueltig_ab liegt in der Zukunft                    -> "Readiness"
- gueltig_ab ist die aktuell gültige (neueste Version
  mit gueltig_ab <= heute)                            -> "Compliance"
- Version wurde seither von einer neueren abgelöst     -> "Historisch"
```

Die zugrunde liegenden Daten (Score, Requirement-Status vom
Erstellungszeitpunkt, siehe 12.6) bleiben dabei exakt eingefroren — nur das
**Label**, wie das Assessment gerade heißt, wandert automatisch mit dem
Kalender mit.

**Dashboard-Standardansicht:** Ein Kunde mit mehreren Assessments sieht in
"Übersicht" automatisch dasjenige, dessen live berechneter Typ gerade
"Compliance" ist. Falls keines existiert (z.B. nur ein inzwischen
"historisch" gewordenes Readiness-Assessment vorhanden), zeigt das Dashboard
das ehrlich an: *"Kein aktuelles Compliance-Assessment vorhanden — euer
letztes Assessment (gegen [Version]) ist mittlerweile historisch."*

### 12.6 Assessment-Lifecycle: "In Bearbeitung" → "Abgeschlossen"

Löst den Zielkonflikt zwischen "Score soll live berechenbar sein, während
der Kunde arbeitet" (z.B. 60 % → Lücken schließen → 78 %) und
"Nachvollziehbarkeit erfordert einen fixen Zeitpunkt-Nachweis" (Abschnitt
12.1/Zulieferer-Dokument Punkt 8, Unveränderlichkeit).

**Zwei Phasen pro Assessment:**

| Phase | Verhalten |
|---|---|
| **In Bearbeitung** (Default nach Erstellung) | Score live berechenbar, Requirement-Status frei editierbar — genau der "60% → 78%"-Arbeitsprozess |
| **Abgeschlossen** (nach explizitem Klick "Assessment abschließen") | Score-Snapshot eingefroren (Zeitstempel + Werte), Requirement-Status schreibgeschützt |

Nach Abschluss: **kein Wiederaufschrauben.** Will der Kunde weiteren
Fortschritt dokumentieren, startet er ein **neues** Assessment gegen
dieselbe Version (siehe 12.3) — ergibt automatisch eine saubere Historie:

```text
Assessment #1 (Version: Basis) — abgeschlossen 20.08.2026 — 78%
Assessment #2 (Version: Basis) — abgeschlossen 15.09.2026 — 91%
```

**Warnung statt Sperre beim Abschließen:** Kein Score-Schwellwert als
Voraussetzung (ein niedriger, aber bewusst gemeldeter Stand ist eine gültige
Aussage). Stattdessen Warnung, falls Requirements noch komplett unberührt
sind (Ausgangswerte `nicht_implementiert`/`nicht_getestet`/`offen`/`fehlt`),
z.B. *"12 von 133 Anforderungen wurden noch nicht bearbeitet. Trotzdem
abschließen?"* — unterscheidet "bewusst schlecht bewertet" von "schlicht
vergessen", lässt sich aber jederzeit übersteuern.

### 12.7 Zusammenspiel mit der Unveränderlichkeits-Regel (11.7/Abschnitt 8 Zulieferer-Dokument)

Zwei getrennte, sich ergänzende Stabilitätsgarantien:

- **Version fix pro Assessment** (12.1) verhindert, dass sich das
  *Referenzsystem* (der Requirement-Katalog) unter einem laufenden
  Assessment verschiebt. Requirements einer Version, gegen die bereits
  mindestens ein Assessment existiert (auch "in Bearbeitung"), werden
  schreibgeschützt im internen Kurations-Formular.
- **In Bearbeitung → Abgeschlossen** (12.6) verhindert, dass sich der
  *Score selbst* nach der offiziellen Momentaufnahme unbemerkt weiterbewegt.

### 12.8 Umsetzungsreihenfolge

| Schritt | Inhalt | Umfang |
|---|---|---|
| 1 (nächster Prompt) | 12.3 (mehrere Assessments), 12.4 (Versionswahl im Wizard), 12.5 (berechneter Typ), 12.7 (Immutability-Regel für Requirements) | mittel |
| 2 | 12.6 (Lifecycle In Bearbeitung/Abgeschlossen inkl. Warnung) | klein-mittel |
| 3 | Formatänderungen-Kundenansicht (Abschnitt 11, bisher zurückgestellter Phase-1-Prompt) — jetzt auf korrektem Fundament | mittel |
| 4 (später) | 12.2 TechnologyContext + Matrix-UI | größer, eigener Sprint |
| 5 (später) | Negative Testfälle kennzeichnen, Fristenprüfung, Export/Import-Visualisierung im Marktkommunikations-Dreieck (rollenabhängig) | jeweils klein, unabhängig einplanbar |
| 6 (bewusst zurückgestellt) | NB/MSB als wählbare Marktrolle — echte Scope-Erweiterung über "Lieferant" hinaus, eigene Entscheidung wert | groß |

### 12.9 UI-Konzept: Aktueller Score + Testlauf-Historie je Version

Ergänzung zu 12.3 (Assessment-Historie), konkretisiert für die Darstellung:
Nach Auswahl einer `RegulatoryVersion` zeigt die Übersicht zunächst einen
prominenten "aktuellen Score", darunter chronologisch (neueste zuerst) die
abgeschlossenen Testläufe dieser Version.

**Logik für den prominenten "aktuellen Score" oben:**

```text
Gibt es ein Assessment "in Bearbeitung" (siehe 12.6) für diese Version?
  → Ja: dessen live berechneter Score wird oben prominent gezeigt
        ("Aktueller Score: 52 % — noch nicht abgeschlossen")
  → Nein: der neueste ABGESCHLOSSENE Testlauf wird oben gezeigt, klar als
        fest gekennzeichnet ("Letzter abgeschlossener Stand: 40 % —
        05.09.2026"), plus Button "Neuen Testlauf starten"
Darunter: alle abgeschlossenen Testläufe dieser Version, chronologisch
absteigend. Der oben bereits prominent gezeigte abgeschlossene Testlauf
(Fall "Nein") erscheint in der Historie darunter nicht doppelt.
```

Liefert nebenbei die Grundlage für einen späteren, fast kostenlosen
Fortschritts-Trend (z.B. Sparkline 30 % → 40 % → 52 % unter der Historie) —
nicht jetzt bauen, aber ohne zusätzliches Datenmodell möglich, sobald die
Historie steht.

---

## 13. Multi-Tenancy (echte Kundentrennung)

Bisher übersehene, aber fundamentale Lücke: Aktuell gibt es **ein
gemeinsames Passwort** für die gesamte App — wer eingeloggt ist, sieht
alle Kunden, alle Assessments, alle Scores. Für die aktuelle Demo-Phase
unkritisch (faktisch "ein Tenant"), aber **zwingende Voraussetzung**, bevor
ein zweiter echter, zahlender Kunde angeschlossen wird — sonst könnte
Kunde A theoretisch die Compliance-Daten von Kunde B einsehen.

### 13.1 Nicht alles muss getrennt werden

Ein Teil der Daten ist bewusst geteiltes Plattform-Wissen, kein
kundenspezifisches Geheimnis:

| Datentyp | Sichtbarkeit |
|---|---|
| Requirement-Katalog, ProcessIdentifier, ProcessGroup | **geteilt** — jeder Gaslieferant testet gegen denselben regulatorischen Katalog |
| RegulatoryVersion, RegulatoryChange (Formatänderungen) | **geteilt** — eine Formatumstellung betrifft alle gleichermaßen |
| Customer, Assessment, AssessmentRequirement, ScoreResult, Finding | **muss getrennt werden** — das ist die eigentliche Kundendaten-Grenze |

Gängiges SaaS-Muster: geteilte Referenzdaten + isolierte Kundenwelt.

### 13.2 Technisch notwendige Bausteine

1. Neue Entität **`Tenant`** (Organisation) — jedes EVU bekommt eine.
2. **Echte individuelle Nutzerkonten** statt eines gemeinsamen Passworts
   oder eines geteilten Tenant-Passworts (Entscheidung vom heutigen Tag,
   siehe 13.4 — direkt der volle Schritt, keine Zwischenstufe mit nur
   einem Passwort pro Tenant). Jeder Nutzer gehört zu genau einem Tenant.
3. **`tenant_id`** auf `Customer` (und implizit auf allem, was daran hängt:
   `Assessment`, `AssessmentRequirement`, `ScoreResult`, `Finding`).
   Jede Datenbankabfrage muss konsequent danach filtern.
4. Der interne Kurations-Bereich (Formatänderungen/"Kanban-Board") bleibt
   **außerhalb** der Tenant-Logik — nur das eigene Atlas-Team, nie ein
   Kunde. Braucht eine eigene, von Tenant-Logins getrennte
   Berechtigungsstufe (z.B. eigene Rolle "Atlas-Intern" statt "Tenant-User").

### 13.4 Authentifizierungs-Architektur: individuelle Konten + SSO-Bereitschaft

Entscheidung vom heutigen Tag: Von Anfang an **echte individuelle
Nutzerkonten** bauen (E-Mail + Passwort pro Person), nicht die zuvor
diskutierte Zwischenstufe "ein Passwort pro Tenant". Zusätzlich wird die
Architektur von Anfang an **SSO-bereit** angelegt (analog zum
Login-Verhalten von claude.ai) — die tatsächliche Anbindung an einen
konkreten Anbieter (z.B. Microsoft Entra ID) wird aber **nicht** jetzt
gebaut, da aktuell kein konkreter Kundenanlass vorliegt (bewusst
vorausschauend, nicht getrieben).

**Login-Flow (wie bei claude.ai):**

```text
1. Nutzer gibt E-Mail ein
2. System ermittelt die Domain der E-Mail (z.B. "@stadtwerke-x.de")
3. Ist für den Tenant dieser Domain ein SSO-Anbieter hinterlegt?
   → Ja: Weiterleitung zum SSO-Anbieter (OIDC-Flow)
   → Nein: Passwort-Feld erscheint
```

**Was jetzt gebaut wird (Rahmen, klein und risikoarm):**
- `User`-Modell: E-Mail, Passwort-Hash, `tenant_id`
- `Tenant` bekommt ein Feld `sso_provider` (nullable: `keiner` | `entra` |
  `google` | `okta` | ...) und Konfigurationsfelder dafür (vorerst leer/
  unbenutzt)
- Login-Formular: E-Mail-first-Eingabe, danach bedingt Passwort-Feld ODER
  Hinweis "SSO noch nicht konfiguriert" als Platzhalter, falls
  `sso_provider` gesetzt, aber die eigentliche Anbindung noch fehlt

**Was bewusst NICHT jetzt gebaut wird (echter, nicht risikoarmer Aufwand):**
- Die tatsächliche OIDC-Anbindung an einen konkreten Provider (App-
  Registrierung beim Anbieter, Redirect-Handling, Token-Validierung).
  Grund: Ohne einen echten Test-Tenant beim jeweiligen Anbieter (z.B.
  eigener Azure-AD-Test-Account für Microsoft Entra) lässt sich diese
  Anbindung nicht seriös durchtesten — Aufwand ohne verlässliche
  Validierungsmöglichkeit. Wird gebaut, sobald ein konkreter Kunde SSO
  als Anforderung nennt.
- Unterstützung mehrerer SSO-Protokolle/Anbieter gleichzeitig (SAML
  zusätzlich zu OIDC) — nur relevant, falls ein Kunde ausschließlich SAML
  anbietet (typischerweise ältere interne Firmensysteme).

**Warum dieser Rahmen trotzdem jetzt sinnvoll ist:** Die trennende
Architektur-Entscheidung aus 13.2 Punkt 2 (Auth-Logik vs. Tenant-
Filterlogik sauber getrennt halten) sorgt dafür, dass die spätere Anbindung
eines echten SSO-Providers nur den Login-Teil ersetzt, ohne die
Tenant-Datenstruktur nochmal anzufassen.

### 13.3 Zeitpunkt

**Jetzt dokumentieren, aber nicht den laufenden Fundament-Prompt (Abschnitt
12.8, Schritt 1) unterbrechen** — beide betreffen strukturell dieselbe Ecke
des Datenmodells (Customer/Assessment), daher lohnt es sich, Multi-Tenancy
direkt im Anschluss anzugehen, bevor an derselben Stelle noch mehr
aufgebaut wird, das später nochmal angefasst werden müsste.

**Empfohlene Reihenfolge:**
1. Abschnitt 12.8 Schritt 1 (läuft bereits) — mehrere Assessments, Versionswahl, berechneter Typ, Immutability
2. **Multi-Tenancy (dieser Abschnitt)** — bevor der Katalog/die Assessment-Struktur weiter wächst
3. Abschnitt 12.8 Schritt 2 (Lifecycle In Bearbeitung/Abgeschlossen) und danach
4. Formatänderungen-Kundenansicht (Abschnitt 11)

Harte Voraussetzung: **vor** dem ersten echten zweiten zahlenden Kunden
muss Multi-Tenancy stehen — kein "kann man später nachziehen".

### 13.5 Hosting-Entscheidung: Railway vs. Azure/AWS (EU)

Frage aufgeworfen im Zusammenhang mit Multi-Tenancy/SSO — Klarstellung:
zwei unabhängige Teilfragen, oft fälschlich vermischt.

**Serverstandort ist bereits gelöst.** Railway bietet seit Anfang 2025 eine
EU-West-Region (Amsterdam) — aktuell bereits aktiv genutzt (siehe
Railway-Deployment-Screenshot: "EU West"). Zusätzlich ist Railway SOC 2
Type II und SOC 3 zertifiziert, GDPR-DPA selbstständig verfügbar. Reiner
Serverstandort ist damit **kein** Grund für einen Wechsel.

**Die tatsächlich relevante Überlegung: Railway ist ein US-Unternehmen**
(Sitz San Francisco), unterliegt damit US-Recht (Cloud Act) — unabhängig
vom Serverstandort. Das kann bei Sicherheits-/Beschaffungsprüfungen
deutscher Unternehmen (insbesondere kommunale Energieversorger mit
konservativen Vergabeprozessen) ein explizites Prüfkriterium sein, ebenso
wie die geringere Bekanntheit von Railway gegenüber etablierten
Hyperscalern in solchen Prüfungen.

**Wichtige Klarstellung, die den ursprünglichen Anlass der Frage betrifft:**
Der Hosting-Ort ist **unabhängig** von der SSO-Anbindung (13.4) — eine
Anbindung an Microsoft Entra ID erfordert nicht, dass Atlas selbst auf
Azure gehostet wird. OIDC funktioniert hosting-unabhängig.

**Entscheidung:** Kein Wechsel jetzt — kein konkreter Kundenanlass, reiner
Mehraufwand ohne aktuellen Nutzen (mehr DevOps-Komplexität als Railways
"git push"-Einfachheit). **Wird zum Entscheidungspunkt vor dem ersten
echten Enterprise-Vertrag**, insbesondere falls ein Kunde im
Beschaffungsprozess explizit einen etablierten Hyperscaler mit
BSI-C5-Testat verlangt. Falls dann gewechselt wird: **Azure App Service**
oder **AWS App Runner** in einer EU-Region (Frankfurt/West Europe) statt
roher VM-/Kubernetes-Infrastruktur, um die Railway-artige Einfachheit
möglichst zu erhalten.

---

## 14. Die vier großen Ausbaustufen (Gesamtarchitektur)

Konsolidierung aus zwei externen Konzeptbeiträgen: Atlas besteht aus vier
großen, unterscheidbaren Bausteinen. Drei davon sind bereits an anderer
Stelle in diesem Dokument detailliert ausgearbeitet — dieser Abschnitt
ordnet sie ein und ergänzt den vierten, bisher fehlenden Baustein.

### 14.1 Überblick

| Baustein | Frage, die Atlas beantwortet | Wo im Dokument |
|---|---|---|
| **1. Mandantenfähige Plattform** | Für wen arbeitet Atlas? | **Abschnitt 13** (Multi-Tenancy) — bereits detailliert |
| **2. EVU-Profil & Relevanzlogik** | Was ist für diesen Kunden relevant? | **Neu, siehe 14.2** |
| **3. Regulatory Intelligence / AI-Agent** | Was hat sich regulatorisch verändert? | **Abschnitt 11** — bereits detailliert |
| **4. Marktkommunikationssystem** | Was passiert tatsächlich in der Marktkommunikation? | **Abschnitt 10** (Stufe 2/3) + eigenständiges Briefing-Dokument für externen Experten |

Alle vier Bausteine hängen am gemeinsamen Fundament aus Abschnitt 12
(Regulatorischer Stand):

```text
                 REGULATORISCHER STAND
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   Regulatory       EVU-Profil     Marktkommunikation
   Intelligence         │              │
   (Abschnitt 11)        ▼              ▼
          │        Relevante        Echte
          │         Prozesse       Nachrichten
          │        (Abschnitt 14.2) (Abschnitt 10)
          └──────────────┼──────────────┘
                         ▼
                    ASSESSMENT
                    (Abschnitt 12)
                         │
                         ▼
               QUALITÄTSBEWERTUNG
```

Baustein 1 (Multi-Tenancy) ist die Voraussetzung, unter der alle anderen
Bausteine kundenspezifisch überhaupt sauber getrennt funktionieren —
deshalb bleibt es laut 13.3 der nächste Schritt nach dem laufenden
Assessment-Fundament.

### 14.2 Baustein 2 im Detail: EVU-Profil & Relevanzlogik (neu)

Bisher vereinfacht Atlas fest auf: *Gas → Lieferant → SLP → Lieferbeginn*.
Das reicht für den MVP, ist aber eine bewusste Verengung, keine
grundsätzliche Eigenschaft des Produkts.

**Zielbild:** Atlas leitet aus einem vollständigeren EVU-Profil automatisch
ab, welche Prozesse überhaupt relevant sind — der Nutzer wählt nicht selbst
aus einer langen Liste von Prozessen, sondern beantwortet Profilfragen,
und Atlas bestimmt daraus die relevante Teilmenge:

```text
EVU-Profil (z.B. Lieferant + Gas + SLP)
        ↓
Atlas-Relevanzlogik
        ↓
Relevante Prozesse (z.B. Lieferbeginn, Lieferende, Anmeldung,
Abmeldung, Stammdatenprozesse, ...)
```

**Profildimensionen, die dafür grundsätzlich in Frage kommen:**
- Marktrollen (Lieferant, Netzbetreiber, MSB, weitere)
- Sparten (Strom, Gas)
- Kundensegmente (SLP, RLM, weitere Konstellationen)

**Wichtiger Hinweis — das ist keine Neuerfindung, sondern eine
Verallgemeinerung von etwas, das bereits existiert:** Der Mechanismus
"Profil → Relevanzlogik → gefilterte Anforderungen" ist im Kleinen bereits
gebaut: `applies_to_slp`/`applies_to_rlm` auf jedem Requirement, die
Regel-Engine-Idee aus der ursprünglichen Spezifikation (Abschnitt 27 der
Erstspezifikation), sowie die dreiwertige Relevanz
(relevant/nicht_relevant/unklar) aus dem 12-Phasen-Analyse-Dokument
(Abschnitt 11.9). Baustein 2 erweitert dieses Prinzip von einer Dimension
(SLP/RLM) auf mehrere (zusätzlich Marktrolle, Sparte, ggf. weitere).

**Offener Punkt, der hier bewusst benannt werden muss, statt sich beiläufig
zu ergeben:** Marktrollen wie Netzbetreiber und MSB waren im Reifegradmodell
(Abschnitt 10, letzte Zeile der Umsetzungstabelle) explizit als **"bewusst
zurückgestellt … echte Scope-Erweiterung über 'Lieferant' hinaus, eigene
Entscheidung wert"** markiert. Baustein 2 setzt genau diese Erweiterung
voraus, wenn er wie im Zielbild vollständig umgesetzt wird. Das ist keine
Ablehnung der Idee — nur die Feststellung, dass hier eine bewusste
Scope-Entscheidung ansteht, kein Selbstläufer.

**Empfehlung zur Einführung: inkrementell, nicht in voller Breite auf
einmal.** Statt gleich alle Marktrollen/Sparten/Segmentkombinationen
abzubilden ("alle 150 Prozesse"), zuerst eine einzelne zusätzliche
Dimension einführen und validieren — z.B. RLM neben SLP, oder
Netzbetreiber neben Lieferant — bevor auf die volle Breite ausgerollt wird.
Gleiches MVP-Prinzip, das sich durch das gesamte bisherige Vorgehen zieht.

### 14.3 Empfohlene Reihenfolge der vier Bausteine

1. **Baustein 1 — Mandantenfähigkeit** (Abschnitt 13) — strukturelle/
   sicherheitsrelevante Grundlage, sollte stehen, bevor mehr
   kundenspezifische Logik draufgebaut wird. Direkt nach dem aktuell
   laufenden Assessment-Fundament (12.8).
2. **Baustein 2 — EVU-Profil & Relevanzlogik**, inkrementell (14.2) —
   fachlich der nächste sinnvolle Schritt, aber mit der NB/MSB-
   Scope-Entscheidung als bewusstem Zwischenschritt.
3. **Baustein 3 — Regulatory Intelligence** (Abschnitt 11) — Pipeline
   bereits detailliert geplant, Start nach Bestätigung durch einen ersten
   Pilotkunden (siehe 11.10).
4. **Baustein 4 — Marktkommunikationssystem** (Abschnitt 10, Stufe 2/3) —
   eigenständiges Briefing an externen Fachexperten bereits erstellt;
   komplexeste und technisch umfangreichste Ausbaustufe (Kommunikations-
   infrastruktur, EDIFACT-Verarbeitung, Sicherheit, Routing,
   Partneridentifikation), daher als eigener großer Track parallel zu den
   anderen drei behandeln, nicht sequenziell danach.

---

## 15. Gesamt-Feature-Übersicht & priorisierter Fahrplan

Konsolidierung aller bisher besprochenen und über das Dokument verstreuten
Einzelentscheidungen an einer Stelle — Antwort auf "wie viele Features
haben wir eigentlich vor, und in welcher Reihenfolge bauen wir sie."

**Gesamtzahl: 35 identifizierte Einzelbausteine**, davon 12 bereits gebaut,
6 aktuell in Umsetzung, 5 als nächste Schritte konkret geplant, 12 bewusst
zurückgestellt (jeweils mit definiertem Auslöser, nicht "irgendwann").

### 15.1 Bereits umgesetzt (12)

1. Wizard (Kundenprofil-Erfassung)
2. Score-Berechnung (Abdeckungsgrad + Qualitätsgrad, 4 Unterdimensionen)
3. Heatmap je Prozessgruppe
4. Marktkommunikations-Dreieck (Visualisierung)
5. Assessment-Bereich (Requirement-Status pflegen)
6. CSV-Import mit Matching-Engine
7. SAP-Cloud-ALM-Import (Grundgerüst — Authentifizierungsfluss korrekt
   implementiert, aber noch nicht gegen einen echten Tenant getestet)
8. Roadmap-Seite (Reifegradmodell-Anzeige)
9. Formatänderungen: interner Kanban-Board-Bereich
10. Formatänderungen: Kunden-Vorschau (Grundversion)
11. Passwortschutz (Login)
12. Railway-Deployment inkl. Cache-Busting-Fix

### 15.2 Aktuell in Umsetzung (6)

Ein zusammenhängender Auftrag, gerade bei Claude Code:

13. Mehrere Assessments pro Kunde + Versionswahl (12.3/12.4)
14. Live berechneter Assessment-Typ (12.5)
15. Immutability-Regel für den Requirement-Katalog (12.7)
16. Versionsauswahl aus dem Wizard herausgelöst, eigener Schritt (UX-Fix)
17. Versions-Kontext-Anzeige auf den Ergebnis-Seiten (UX-Fix)
18. Empty-State-Korrektur "Formatumstellungs-Impact" (UX-Fix)

### 15.3 Priorisierter Fahrplan — als Nächstes, in dieser Reihenfolge

19. **Multi-Tenancy** (Abschnitt 13.1–13.3) — Tenant-Entität, `tenant_id`-
    Filterung, getrennte Berechtigungsstufe für den internen Bereich
20. **Auth-Rahmen mit SSO-Bereitschaft** (13.4) — echte Nutzerkonten,
    E-Mail-first-Login, `sso_provider`-Platzhalterfeld — direkt zusammen
    mit 19, da dieselbe Code-Ecke betroffen ist
21. **Assessment-Lifecycle** "In Bearbeitung → Abgeschlossen" (12.6) —
    inkl. Warnung bei unberührten Requirements
22. **EVU-Profil & Relevanzlogik, erste zusätzliche Dimension** (14.2) —
    inkrementell, z.B. RLM neben SLP oder eine zweite Marktrolle,
    **nicht** sofort die volle Breite
23. **Formatänderungen-Kundenansicht ausbauen** (Abschnitt 11, ursprünglich
    als "Phase 2–4" zurückgestellt): Filter-Leiste, Detail-Drawer mit
    Quellen&Nachweise-Bereich, "Alle Änderungen anzeigen"-Umschalter mit
    dreiwertiger Relevanz (relevant/nicht relevant/unklar)

**Können jederzeit dazwischengeschoben werden, da unabhängig vom obigen
Pfad** (kleine, in sich abgeschlossene Ergänzungen):
- Negative Testfälle explizit kennzeichnen
- Fristenprüfung (neues Datenmodell-Feld + Prüflogik)
- Export/Import-Visualisierung im Marktkommunikations-Dreieck
  (rollenabhängig)
- Railway-Staging-Umgebung einrichten (empfohlen spätestens vor Schritt 19,
  da Multi-Tenancy ein strukturell riskanter Umbau ist)

### 15.4 Bewusst zurückgestellt (12) — jeweils mit definiertem Auslöser

| # | Baustein | Auslöser für den Start |
|---|---|---|
| 24 | Automatisierte Regulatory-Intelligence-Pipeline (Monitoring/Extraktion/Diff/KI, Abschnitt 11.2–11.3/11.10) | Bestätigung durch einen ersten Pilotkunden |
| 25 | Technology Intelligence / Technology Packs (SAP Notes etc., Ebene 2) | Nachfrage nach Baustein 24 |
| 26 | Atlas API als eigenständiges Produktangebot (11.6) | Eigene Pricing-/Produktentscheidung |
| 27 | Nachrichtensimulation Stufe 2/3 (Marktpartner-Simulator, Prozessketten-Prüfung) | Ergebnis des externen Fachexperten-Briefings — kann parallel zu 15.3 laufen |
| 28 | Echte SSO-Provider-Anbindung (Entra/Google/Okta, OIDC-Flow) | Konkreter Kunde verlangt SSO |
| 29 | NB/MSB als wählbare Marktrolle | Eigene Scope-Entscheidung, Voraussetzung für volle Breite von Baustein 22 |
| 30 | Jira/Xray/TestRail-Anbindung (Stufe 1b) | Zielkunde arbeitet nachweislich in einem dieser Tools |
| 31 | Hosting-Wechsel zu Azure/AWS (13.5) | Erster Enterprise-Vertrag verlangt es explizit |
| 32 | Zusätzliches SAML-Protokoll (neben OIDC) | Kunde bietet ausschließlich SAML an |
| 33 | Vollständige Katalog-Duplizierung pro Version (Ansatz A statt B, siehe 12) | Nur falls Ansatz B sich als unzureichend erweist |
| 34 | Fortschritts-Trend/Sparkline in der Assessment-Historie (12.9) | Kostenlos sobald Historie steht — jederzeit nachrüstbar |
| 35 | Bulk-CSV-Import auch für Formatänderungen-Kuration | Falls Kurationsmenge das manuelle Erfassen übersteigt |

### 15.5 Kernprinzip hinter der Reihenfolge

Durchgängiges Muster in diesem Dokument, hier nochmal explizit: **Strukturell
riskante/schwer nachträglich zu ändernde Bausteine zuerst** (Multi-Tenancy,
Auth-Architektur, Assessment-Fundament), **fachliche Verfeinerungen danach**
(EVU-Profil, Formatänderungen-Ausbau), **spekulative/teure/nicht ohne
echten Kunden testbare Bausteine zuletzt und mit explizitem Auslöser**
(SSO-Provider-Anbindung, automatisierte Pipeline, Hosting-Wechsel,
Nachrichtensimulation). Kein Baustein wird "weil er interessant ist"
vorgezogen, ohne dass entweder eine strukturelle Abhängigkeit oder ein
konkreter Kundenanlass das rechtfertigt.

---

# Teil C — Vertiefung: Marktkommunikationssystem / Nachrichtensimulation

*Detaillierte Ausarbeitung von Baustein 4 aus Teil B (Abschnitt 10/14) —* 
*ursprünglich als eigenständiges Briefing für einen externen Fachexperten formuliert.*

## 1. Kontext: Was ist Atlas

Atlas ist eine Plattform, die Energieversorgungsunternehmen (EVUs) zeigt,
wie gut ihre Marktprozesse funktionieren — im Vorfeld einer regulatorischen
Formatumstellung oder eines technologischen Wechsels. Aktueller Stand: ein
funktionierendes MVP für den Prozess **Lieferbeginn Gas** (SLP, Marktrolle
Lieferant), das auf **Selbstauskunft** basiert — der Kunde trägt selbst
ein, ob eine Anforderung implementiert/getestet ist, Atlas berechnet daraus
einen Score.

**Das Problem mit Selbstauskunft:** Sie bleibt eine Behauptung. Genau hier
setzt der nächste Entwicklungsschritt an, für den wir dich brauchen.

## 2. Der Auftrag: Nachrichtensimulation als objektive Prüfung

Ziel ist es, Selbstauskunft durch **objektiv geprüfte Ergebnisse** zu
ersetzen — indem Atlas selbst mit dem Kundensystem kommuniziert, statt nur
einer Eingabe zu vertrauen.

**Zentrale, bereits getroffene Architektur-Entscheidung — bitte als feste
Leitplanke behandeln:**

> Atlas bekommt **keinen Zugriff auf interne Backend-Systeme** der Kunden.
> Objektivität entsteht ausschließlich über die Marktkommunikation selbst
> (Nachrichtenaustausch), nicht über einen Blick ins System des Kunden.

Das ist kein technisches Detail, sondern der bewusste Wettbewerbsvorteil
des Produkts: geringere Vertrauenshürde beim Kunden, schnellere
Time-to-Market, ein echtes skalierbares Produkt statt eines
Custom-Integrationsprojekts pro Kunde.

**Ebenso festgelegt:** Es handelt sich um eine **private Sandbox**, keine
echte Teilnahme am produktiven Markt. Atlas wird nicht zum offiziell
registrierten Marktpartner mit eigener Marktpartner-ID/AS4-Zertifikat im
echten EDI@Energy-Netz. Der Kunde testet gegen eine von Atlas simulierte
Gegenstelle, außerhalb der echten Marktinfrastruktur.

## 3. Die vier fachlichen Bausteine

### 3.1 Nachrichten-Validierung
Das EVU schickt reale Marktnachrichten an Atlas (Transportweg noch offen,
siehe Abschnitt 5). Atlas prüft automatisiert gegen die offizielle
Formatspezifikation: Pflichtfelder, Segmentlogik, korrekte Version,
korrekter Prüfidentifikator.

### 3.2 Marktpartner-Simulator (inkl. aktiver Nachrichtenerzeugung)
Atlas simuliert die Gegenseite eines Prozesses (z.B. den Netzbetreiber bei
einem Lieferantenwechsel), sodass das EVU den kompletten Prozess
End-to-End testen kann, ohne einen echten Marktpartner zu brauchen.

**Wichtig, explizit als eigene Fähigkeit zu verstehen — nicht nur
"prüfen", sondern aktiv "erzeugen":** Atlas muss dafür selbst gültige
EDIFACT-/XML-Nachrichten **generieren** (z.B. die Bestätigung nach einer
Anmeldung) und an das Kundensystem zurücksenden. Nachrichtenerzeugung ist
also eine ebenso zentrale Fähigkeit wie Nachrichtenempfang/-validierung
aus 3.1 — nicht nur ein Nebeneffekt der Simulation.

### 3.3 Prozesskonsistenz statt Backend-Zugriff
Da Atlas nicht ins interne System des Kunden schauen kann, wird korrekte
interne Verarbeitung **indirekt über die gesamte Nachrichtenkette**
geprüft:

- Mehrere aufeinanderfolgende Nachrichten eines Prozesses werden gesendet
  (z.B. Anmeldung → Stammdatenänderung → Ablesung)
- Referenzdaten (Vertragskonto, Zählpunkt, Kundennummer) müssen über alle
  Schritte hinweg konsistent zurückkommen
- Zusätzlich werden bewusst fehlerhafte Testfälle geschickt (falsche
  Zählpunktnummer, doppelte Anmeldung) — ein System mit korrekter interner
  Logik muss diese sauber ablehnen

**Output für den Kunden:** ein Readiness-Ergebnis wie *"Prozess X ist zu
Y % konform, diese Fehler blockieren den Produktivbetrieb"* — das ist der
eigentliche Verkaufswert gegenüber der Geschäftsführung eines Kunden.

### 3.4 Eigenständiges Zusatzfeature: Testnachrichten zum Download

Zusätzlich zur oben beschriebenen **live laufenden** Simulation (3.1–3.3)
soll Atlas dem Kunden auch **unabhängig davon** fertige Testnachrichten
bereitstellen können — zum Herunterladen, damit der Kunde sie **in seinem
eigenen Testsystem** verwendet, ohne dass eine laufende Atlas-Session nötig
ist. Beispiel: Der Kunde will schnell prüfen, ob sein System einen
bestimmten Ablehnungscode korrekt verarbeitet — er lädt eine dazu passende
Beispiel-UTILMD-Nachricht (spec-konform, versionsbewusst wie in Abschnitt
4 beschrieben) herunter, statt sie selbst von Hand zu bauen. Dazu gehören
sowohl gültige Beispielnachrichten als auch bewusst fehlerhafte
Testfälle (siehe 3.3).

**Priorisierungs-Hinweis:** Dieser Baustein ist technisch deutlich
kleiner als der volle Marktpartner-Simulator (3.2/3.3) — er braucht
**keinen** Empfangs-Kanal, **keinen** Parser für eingehende Nachrichten
und **keine** Zustands-Logik für mehrstufige Sessions. Nur die
**Erzeugung** einzelner Nachrichten aus dem bereits vorhandenen
Requirement-Katalog. Empfehlung: als eigenständiger, früher Meilenstein
innerhalb von Baustein 4 behandeln — die Generierungslogik lässt sich
danach direkt für den vollen Simulator (3.2) wiederverwenden, statt sie
später separat zu bauen.

## 4. Was bereits existiert und wiederverwendet werden kann

- **Requirement-Katalog:** 133 Anforderungen über 16 Prüfidentifikatoren
  (PI 44001–44038) für Lieferbeginn Gas, inkl. Kritikalität, betroffener
  Prozessgruppe, Transaktionsgrund, Antwortcode. Das ist bereits die
  fachliche Testfallbibliothek — die Simulation sollte gegen diesen
  Katalog laufen, nicht einen neuen parallel aufbauen.
- **Assessment-Datenmodell:** `AssessmentRequirement` mit Status-Feldern
  (Implementierung, Test, Ergebnis, Nachweis) — vorgesehen ist bereits ein
  Feld `data_source` (`manuell` vs. `automatisiert`), damit später
  erkennbar bleibt, welcher Anteil eines Scores objektiv simuliert statt
  selbst eingetragen wurde.
- **Regulatorischer Stand:** Jede Prüfung ist einer `RegulatoryVersion`
  zugeordnet (z.B. "GeLi Gas 2.0" oder eine künftige Formatumstellung) —
  die Simulation muss wissen, gegen welchen Stand sie prüft.

**Wichtige, technisch verbindliche Konsequenz daraus (nicht nur Kontext,
sondern feste Anforderung):** Der Kunde wählt bereits beim Anlegen eines
Assessments den regulatorischen Stand aus (siehe Wizard-Flow in Atlas).
**Diese Auswahl bestimmt zwingend, gegen welche konkrete AHB-/MIG-Version
simuliert wird** — nicht nur, welcher Requirement-Katalog gilt. Beispiel:
Der Stand "GeLi Gas 2.0 / UTILMD Gas G1.1" verlangt andere
Segmentstrukturen/Pflichtfelder als eine spätere Version wie "UTILMD Gas
G1.2" (aus Mitteilung 56). Der Nachrichtengenerator/-parser darf daher
**nicht auf eine einzige, fest einprogrammierte Nachrichtenstruktur
ausgelegt sein** — er muss versionsbewusst arbeiten, d.h. pro
`RegulatoryVersion` das jeweils passende Segment-/Feldschema anwenden.
Das ist eine der zentralen Architekturfragen, die in Abschnitt 5 als
offene Frage 3 (Parser/Serializer) explizit mit gelöst werden muss.

## 5. Offene technische Fragen — hierfür brauchen wir deine Einschätzung

1. **Transportweg:** SFTP-Dateiaustausch, Upload-API, oder beides parallel
   anbieten? AS2/AS4 (der "echte" Standard in EDI@Energy) war bisher als
   spätere Ausbaustufe vorgesehen — zu aufwendig (Zertifikatsverwaltung,
   MDN-Quittungen) für den Objektivitätsgewinn im ersten Schritt, **und**
   bislang nicht seriös testbar.

   **Update, zu besprechen:** Der Testbarkeits-Vorbehalt ist mittlerweile
   überholt — es steht eine **AS4-Testumgebung eines MaKo-Software-
   Anbieters** (z.B. Schleupen, Seeburger) zur Verfügung. Der zweite Grund
   (Zertifikatsverwaltung/MDN-Quittungen sind unabhängig von der
   Testbarkeit echter Mehraufwand) besteht weiterhin unverändert. **Bitte
   im Kickoff-Gespräch gemeinsam entscheiden:** Ändert die jetzt vorhandene
   Testmöglichkeit die empfohlene Reihenfolge (AS4 doch schon in der ersten
   Phase mitdenken statt nachgelagert), oder bleibt es beim ursprünglichen
   Vorschlag (SFTP/API zuerst, AS4 als Ausbaustufe), nur eben jetzt mit
   einer konkreten Testmöglichkeit für den Zeitpunkt, an dem AS4 dran ist?
   Diese Entscheidung ist bewusst noch offen und nicht vorweggenommen.
2. **Format:** EDIFACT (klassisch), XML (neuerer Standard, teils
   kostenpflichtig über BDEW-Abo), oder beide unterstützen?
3. **Parser/Serializer — versionsbewusst:** Wie wird eine UTILMD-Nachricht
   zuverlässig geparst und wieder erzeugt, **abhängig von der jeweiligen
   `RegulatoryVersion`** (siehe Abschnitt 4)? Braucht es pro Version ein
   eigenes Schema/Template, oder lässt sich das generischer lösen (z.B.
   parametrisiert über die MIG-Struktur der jeweiligen Version)? Gibt es
   sinnvolle Bibliotheken/Vorarbeiten, auf die wir aufbauen können, statt
   bei null anzufangen?
4. **State-Machine-Design:** Wie wird eine mehrstufige Testsession
   (mehrere Nachrichten, Referenzdaten über Schritte hinweg) sauber
   modelliert und implementiert?
5. **Mapping-Layer:** Wie wird ein Simulationsergebnis konkret auf unseren
   bestehenden Requirement-Katalog (Abschnitt 4) abgebildet, sodass es
   automatisch den passenden `AssessmentRequirement`-Status setzt?
6. **Fehlerfall-Bibliothek:** Wie strukturieren wir die bewusst
   fehlerhaften Testfälle (Abschnitt 3.3) systematisch, statt sie ad hoc
   zu erfinden?

## 6. Nicht Teil dieses Auftrags (zur Abgrenzung)

Damit der Scope klar bleibt — folgende Themen laufen in Atlas parallel,
sind aber **nicht** Gegenstand dieser Zusammenarbeit:

- Regulatory Intelligence (automatisierte Analyse von BNetzA/BDEW-
  Veröffentlichungen) — eigenständiger Baustein, andere Arbeitsgruppe
- UI/Dashboard-Weiterentwicklung
- Multi-Tenancy / Nutzerverwaltung
- Echte Marktteilnahme (eigene Marktpartner-ID) — bewusst ausgeschlossen,
  siehe Abschnitt 2

## 7. Gewünschtes Ergebnis dieser Zusammenarbeit

Ein konkreter, priorisierter Umsetzungsplan für Stufe 2 ("Einzelnachrichten-
Simulation") und Stufe 3 ("Prozessketten-Simulation") des Atlas-
Reifegradmodells, mit:

- Empfehlung zu den offenen Fragen aus Abschnitt 5
- Grober Aufwandsschätzung pro Baustein
- Vorschlag für die Reihenfolge (was zuerst, was kann parallel laufen)
- Technische Architekturskizze (Komponenten, Schnittstellen zum
  bestehenden Backend)

---

# Teil D — Anhang: MVP-Referenz (archiviert)

*Technische Erstspezifikation des MVP (Lieferbeginn Gas) — nicht mehr aktiv* 
*erweitert, dient als historische Referenz, wie das laufende System entstanden ist.*

## 1. MVP-Scope in eigenen Worten

Wir bauen eine Bewertungsplattform, die einem Gaslieferanten zeigt, wie vollständig und wie
gut er den regulatorischen Prozess **Lieferbeginn Gas** (GeLi Gas 2.0 / UTILMD Gas G1.1,
Konsultationsstand 01.08.2025) beherrscht. Die Plattform soll dabei sowohl im Vorfeld einer
**regulatorischen Formatumstellung** (z.B. neue Konsultationsfassung, PID-Wechsel) als auch
im Vorfeld eines **technologischen Wechsels** (z.B. Systemwechsel, S/4HANA-Migration,
Umstieg auf MaKo Cloud) einsetzbar sein — in beiden Fällen stellt sich für die
Geschäftsführung dieselbe Frage: "Sind wir bereit für den Produktivbetrieb?"

Der Kunde beschreibt sein Profil (Marktrolle Lieferant, Sparte Gas, Segmente SLP/RLM,
geschäftliche Konstellation). Die Plattform leitet daraus automatisch ab, welche PIs,
Transaktionsgründe und Antwortcodes für ihn relevant sind, und lässt ihn pro Anforderung
einen Status (implementiert/getestet/nachgewiesen) eintragen.

Am Ende stehen **zwei getrennte Kennzahlen**:

- **Regulatorischer Abdeckungsgrad** — wie viel vom relevanten Soll-Katalog ist überhaupt
  adressiert?
- **Qualitätsgrad** — wie gut ist das, was adressiert ist, umgesetzt/getestet/nachgewiesen?

Diese Trennung ist die fachliche Kernidee und darf nicht zu einem einzigen Score verwischt
werden. Fachlich vollständig abgedeckt sind im ersten MVP nur die Prozessgruppen Anmeldung,
Abmeldeanfrage, Informationsmeldungen, Stornierung, Geschäftsdaten und Bestandsabgleich rund
um PI 44001–44038. Alles außerhalb (Strom, GPKE, andere Sparten) ist explizit **nicht**
Gegenstand des MVP.

---

## 2. Nutzerfluss (nummeriert)

1. Nutzer öffnet die Plattform, landet auf **Profilerfassung** (Wizard Schritt 1).
2. Nutzer wählt Marktrolle (fix: Lieferant), Sparte (fix: Gas), Kundensegment
   (Mehrfachauswahl SLP/RLM), geschäftliche Konstellation, regulatorischen Stand.
3. Klick auf **"Relevante Marktkommunikation ermitteln"** → Backend leitet relevante
   Prozesse/PIs ab (`derive-processes`).
4. Anzeige der **Dreiecksvisualisierung** (Neulieferant / Altlieferant / Netzbetreiber) mit
   klickbaren Verbindungen.
5. Nutzer klickt Verbindung **Neulieferant → Netzbetreiber**, Detailpanel öffnet sich
   (Prozess, Sender, Empfänger, PI, Kritikalität, Status, Beschreibung, "Assessment starten").
6. Nutzer startet Assessment für **Lieferbeginn Gas** → Backend leitet konkrete
   Anforderungen ab (`derive-requirements`), gefiltert nach SLP/RLM-Relevanz.
7. Nutzer sieht strukturierte **Assessment-Ansicht**: Prozessgruppen als Akkordeons, PIs
   als Karten, darunter Requirement-Zeilen.
8. Pro Requirement trägt der Nutzer Status ein (Relevanz, Implementierung, Test, Ergebnis,
   Nachweis) + optional Kommentar/Verantwortlicher/Datum/Evidence-Link.
9. Jede Statusänderung wird per API gespeichert (`PUT /assessment-requirements/{id}`).
10. Nutzer klickt **"Bewertung berechnen"** → Backend berechnet Abdeckungsgrad und
    Qualitätsgrad (`POST /assessments/{id}/calculate`).
11. Ergebnisansicht zeigt Hauptkennzahlen, Unterkennzahlen, Heatmap je Prozessgruppe,
    Findings-Liste mit Handlungsempfehlungen.
12. Nutzer kann das Assessment schließen und später erneut öffnen — Zustand ist persistiert.

---

## 3. Frontend-Seiten und Komponenten

### Seiten (React Router)
- `/` — Landing/Einstieg, Liste bestehender Assessments
- `/assessments/new` — Profil-Wizard (Schritt 1–4)
- `/assessments/:id/graph` — Marktkommunikations-Visualisierung
- `/assessments/:id/process/:processId` — Assessment-Detailansicht (Akkordeons/PI-Karten)
- `/assessments/:id/results` — Ergebnis-/Score-Ansicht mit Heatmap & Findings

### Komponenten (wie im Auftrag vorgegeben, hier mit Verantwortlichkeit)

| Komponente | Aufgabe |
|---|---|
| `ApplicationShell` | Layout, Navigation, Versionsbadge global sichtbar |
| `SidebarSteps` | Wizard-Fortschritt (Profil → Graph → Assessment → Ergebnis) |
| `ProfileForm` | Erfassung Marktrolle/Sparte/Segment/Konstellation/Regulierungsstand |
| `MarketCommunicationGraph` | Dreiecksvisualisierung mit klickbaren Kanten (SVG, evtl. via Visualizer-Pattern) |
| `ProcessDetailPanel` | Slide-in/Modal bei Kantenklick: Prozessdetails + CTA |
| `AssessmentOverview` | Container für alle Prozessgruppen eines Assessments |
| `ProcessGroupAccordion` | Eine Prozessgruppe (z.B. "Anmeldung") als aufklappbarer Block |
| `PiCard` | Ein PI mit Kritikalität, Kurz-Abdeckung, Klick öffnet Requirement-Liste |
| `RequirementRow` | Eine Anforderung mit Statusdropdowns, Kommentarfeld |
| `EvidencePanel` | Upload/Link-Erfassung pro Requirement (im MVP vereinfacht) |
| `ScoreCard` | Große Kennzahl (Abdeckungsgrad/Qualitätsgrad) mit Ring/Balken |
| `Heatmap` | Tabellarische Ampel je Prozessgruppe |
| `FindingsList` | Liste generierter Findings mit Schweregrad-Badge |
| `VersionBadge` | Zeigt aktiven regulatorischen Stand global an |
| `FilterBar` | Filter nach SLP/RLM/Kritikalität in der Assessment-Ansicht |

---

## 4. Backend-Module

```text
app/
├── main.py                 # FastAPI-Entry, Router-Registrierung
├── api/
│   ├── assessments.py       # /api/assessments, /scope, /derive-*
│   ├── reference_data.py    # /regulatory-versions, /processes, /pis, /requirements
│   ├── assessment_requirements.py  # PUT status, /calculate, /results, /findings
│   └── evidence.py          # Evidence CRUD
├── services/
│   ├── derivation_service.py   # Relevanzregeln → relevante Prozesse/Requirements
│   ├── scoring_service.py      # Abdeckungsgrad- & Qualitätsgrad-Berechnung
│   ├── findings_service.py     # Generiert Findings aus Assessment-Requirement-Status
│   └── mapping_service.py      # (spätere Ausbaustufe) Kundentestfall-Mapping
├── models/                  # SQLAlchemy-Modelle, 1:1 zum Datenmodell in Abschnitt 5
├── schemas/                 # Pydantic Request/Response-Schemas
├── rules/
│   └── relevance_rules.py + relevance_rules.json  # Regel-Engine (Abschnitt 27 im Auftrag)
├── seed/
│   ├── seed_data/*.yaml     # PIs, Transaktionsgründe, Antwortcodes, Requirements
│   └── seed_runner.py
└── db/
    ├── session.py
    └── alembic/              # Migrationen
```

Trennung: **API-Layer** (nur Validierung/Routing) → **Service-Layer** (Businesslogik,
insb. Scoring und Derivation) → **Model/Repository-Layer** (Persistenz). Die Scoring-Logik
lebt ausschließlich im `scoring_service.py`, nicht im Frontend — wie gefordert.

---

## 5. Relationales Datenmodell (Kurzfassung)

Entspricht den in Abschnitt 25 des Auftrags vorgegebenen Entitäten. Wichtigste Beziehungen:

```text
RegulatoryVersion 1─* Requirement
MarketProcess 1─* ProcessGroup 1─* ProcessIdentifier (PI)
ProcessIdentifier 1─* Requirement
TransactionReason, ResponseCode  ─* Requirement  (optionale FKs)
Requirement 1─* ReferenceTestCase
Customer 1─* Assessment 1─1 AssessmentScope
Assessment 1─* AssessmentRequirement (*─1 Requirement)
AssessmentRequirement 1─* Evidence
Assessment 1─1 ScoreResult
Assessment 1─* Finding (*─1 Requirement)
```

Kernpunkt: **`Requirement`** ist der Dreh- und Angelpunkt — verknüpft PI, Transaktionsgrund,
Antwortcode, Kritikalität/Gewicht, SLP/RLM-Relevanz, Bedingungslogik und regulatorische
Version. **`AssessmentRequirement`** ist die kundenspezifische Instanz davon mit dem
erfassten Status. Diese Trennung "Soll" (Requirement) vs. "Ist" (AssessmentRequirement) ist
die Grundlage für die spätere Score-Berechnung.

*(Vollständige Feldlisten wie im Auftrag Abschnitt 25 spezifiziert — werden 1:1 als
SQLAlchemy-Modelle übernommen, keine Abweichung nötig.)*

---

## 6. Bewertungslogik

### Regulatorischer Abdeckungsgrad
```text
coverage = Σ(gewicht_i · erfüllt_i) / Σ(gewicht_i)   für alle relevanten Requirements i
```
- „Relevant" = Requirement matcht Segment (SLP/RLM), Konstellation, regulatorische Version
  UND Bedingung (`condition_expression`) ist erfüllt.
- „Erfüllt" = `implementation_status` ist mindestens „implementiert" (binär oder gestuft,
  MVP: binär reicht, Ausbaustufe: gestufte Teilerfüllung).
- Nicht-relevante Requirements fließen **nicht** in den Nenner ein — “nicht implementiert”
  bleibt aber immer im Nenner, wenn das Requirement relevant ist (Kernregel aus Abschnitt 22).

### Qualitätsgrad
```text
quality = 0.35·implementation_quality + 0.35·test_quality
        + 0.20·evidence_quality + 0.10·actuality
```
Gewichte aus Abschnitt 22, **konfigurierbar** (nicht hartkodiert, liegen in
`scoring_config.yaml` oder DB-Tabelle `ScoreWeightConfig`, damit sie ohne Deployment
änderbar sind — löst die Anforderung "Gewichtung konfigurierbar, nicht fest im Frontend").
Jede Unterdimension wird analog aus dem Status der zugehörigen `AssessmentRequirement`-Felder
abgeleitet (z.B. `test_status = erfolgreich getestet` → Testqualität-Punkt).

### Findings-Generierung
Regelbasiert: für jedes relevante Requirement mit `implementation_status = nicht implementiert`
oder `evidence_status = fehlt` wird automatisch ein Finding mit Schweregrad = Kritikalität
des Requirements erzeugt. Zusätzliche Spezialregeln (z.B. ZC5-Pflichtdaten, Z35-Referenz)
werden als eigene Prüfregeln in `findings_service.py` hinterlegt.

---

## 7. Initiale Projektstruktur

```text
repo/
├── backend/
│   ├── app/                  (siehe Abschnitt 4)
│   ├── tests/
│   ├── pyproject.toml / requirements.txt
│   ├── alembic.ini
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/               # zentrale API-Client-Schicht (fetch-Wrapper + Typen)
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 8. Offene fachliche/technische Entscheidungen

Diese sollten wir vor der Implementierung kurz klären:

1. **Gestufte vs. binäre Erfüllung**: Zählt "implementiert" im MVP binär (ja/nein), oder
   soll schon jetzt eine Teilerfüllung (z.B. "teilweise implementiert" = 0,5) möglich sein?
   *Empfehlung: MVP binär, Datenmodell aber so anlegen, dass später Zwischenwerte möglich sind.*
2. **Evidence-Upload**: Laut Auftrag "vereinfacht oder simuliert" — reicht ein reines
   URL-/Textfeld ohne echten Dateispeicher für die Demo?
3. **Regel-Engine-Format**: JSON-Regeln direkt in DB-Tabelle oder als Datei im Repo geladen
   beim Seed? *Empfehlung: Datei-basiert für MVP (einfacher zu versionieren/reviewen),
   DB-Migration später möglich.*
4. **Authentifizierung**: Laut Auftrag explizit außerhalb des MVP-Scopes — heißt das,
   die Demo läuft komplett ohne Login (offener Zugriff), oder brauchst du zumindest einen
   einfachen Passwortschutz für die Geschäftsführungs-Demo?
5. **Visualisierung der Dreiecksbeziehung**: Als eigene React/SVG-Komponente im Frontend,
   oder soll ich das als interaktives Widget separat prototypen, bevor es ins Frontend
   übernommen wird?

---

## 9. Implementierungsplan (Arbeitspakete)

| # | Paket | Inhalt |
|---|---|---|
| 1 | Backend-Grundgerüst | FastAPI-Projekt, DB-Setup (SQLite lokal), Alembic-Init |
| 2 | Datenmodell | Alle SQLAlchemy-Modelle aus Abschnitt 5, erste Migration |
| 3 | Seed-Daten | YAML-Dateien für PIs 44001–44038, Transaktionsgründe, Antwortcodes, Requirements, Beispielkunde |
| 4 | Referenzdaten-API | GET-Endpunkte für Prozesse/PIs/Requirements |
| 5 | Regel-Engine & Derivation | `relevance_rules.json` + `derivation_service.py`, Endpunkte `derive-processes`/`derive-requirements` |
| 6 | Assessment-CRUD & Status | Assessment anlegen, Scope setzen, Requirement-Status per PUT speichern |
| 7 | Scoring-Service | Abdeckungsgrad + Qualitätsgrad-Berechnung, konfigurierbare Gewichte |
| 8 | Findings-Service | Regelbasierte Findings-Generierung |
| 9 | Backend-Tests | Unit-Tests für Scoring- und Derivation-Logik |
| 10 | Frontend-Grundgerüst | Vite+React+TS-Setup, Routing, API-Client-Schicht |
| 11 | Profil-Wizard | `ProfileForm`, Speichern des Kundenprofils |
| 12 | Marktkommunikations-Graph | `MarketCommunicationGraph` + `ProcessDetailPanel` |
| 13 | Assessment-Ansicht | `ProcessGroupAccordion`, `PiCard`, `RequirementRow`, Statuserfassung |
| 14 | Ergebnisansicht | `ScoreCard`, `Heatmap`, `FindingsList` |
| 15 | Demo-Testkunde | Seed mit bewusst lückenhaftem Profil (Abschnitt 29) |
| 16 | Docker/Deployment | Dockerfiles, docker-compose, `.env.example`, README |

**Vorschlag für die Reihenfolge unserer nächsten Schritte:** Wir klären kurz die 5 offenen
Fragen aus Abschnitt 8, dann starte ich mit Paket 1–3 (Backend-Grundgerüst + Datenmodell +
Seed-Daten), damit wir früh mit echten Daten gegen die API testen können, bevor das Frontend
entsteht.

---

