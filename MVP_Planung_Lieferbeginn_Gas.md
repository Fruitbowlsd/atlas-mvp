# MVP-Planung: Assessment-Plattform Lieferbeginn Gas

Planungsstand vor Implementierungsbeginn — Antwort auf die "Erste Aufgabe".

**Aktueller Stand & Entscheidung (Update):** Das MVP (Stufe 1 — Selbstauskunft,
siehe Abschnitt 10) ist gebaut, getestet und auf Railway deployt. Entscheidung:
Wir bauen als Nächstes am bestehenden Dashboard weiter, statt direkt in
Stufe 2/3 (Nachrichten-Simulator) einzusteigen. Stufe 2/3 bleiben als
geplante Ausbaustufen im Backlog (siehe Abschnitt 10), werden aber aktuell
nicht umgesetzt.

**Update 2 — Regulatory Intelligence als nächste konkrete Ausbaustufe:**
Entscheidung, das Feature "Formatumstellung im Voraus analysieren" (Delta
zwischen zwei regulatorischen Versionen, Impact auf Kundenscore) jetzt zu
implementieren — inklusive einer echten Anthropic-API-Anbindung im Backend
für die KI-gestützte Kategorisierung/Zusammenfassung von Änderungen
(siehe Abschnitt 11). Ab hier wird die Umsetzung in einer neuen Session/mit
Claude Code fortgesetzt (nicht mehr im selben Chat).

**Für den Start der nächsten Session benötigt:**
- Zugriff auf das bestehende Repo (`atlas-mvp`, siehe GitHub `Fruitbowlsd/atlas-mvp`)
- Ein eigener Anthropic API-Key (console.anthropic.com), als Umgebungsvariable
  im Backend zu hinterlegen (z.B. `ANTHROPIC_API_KEY`) — nicht der claude.ai-Zugang
- Dieses Planungsdokument als Kontext (Abschnitt 11 beschreibt die Pipeline
  und das Datenmodell im Detail)

---

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
