# Vorschlag — Verhältnis `Regulatory State` ↔ `RegulatoryVersion` (Abschnitt 9a)

**Ticket:** #64 · **Status:** vom Nutzer **bestätigt am 17.09.2026**. **Noch keine Schemaänderung durchgeführt.**

---

## 1. Empfehlung

**`Regulatory State` wird eine neue Ebene oberhalb von `RegulatoryVersion`, mit einer
1:n-Beziehung.** Ein Regulatory State je Stichtag. `RegulatoryVersion` bleibt das
spartenbezogene Produkt-Release, an dem Assessments, Requirement-Katalog und
MessageDefinitions hängen. Es erhält eine **optionale** Referenz auf den State, aus dem es
abgeleitet ist.

```text
RegulatoryState  (1 je Stichtag, spartenübergreifend, regulatorische Tatsache)
  ├── RegulatoryStateDocumentVersion  (n)  ── zeigt auf ──►  RegulatoryDocumentVersion
  │        + maßgebliche Fassung, Auswahlbegründung            │
  │                                                            ├── RegulatoryDocument (versionsunabhängig)
  │                                                            └── RegulatoryDocumentFile (Fassungen, SHA-256)
  └── RegulatoryVersion  (0..n)   ◄── regulatory_state_id (nullable)
           Sparte, is_active, summary  ── Assessment, Requirement, MessageDefinition, CodeList, …
```

Die Variante **1:1-Alias** (`RegulatoryVersion.regulatory_state_id` mit genau einer
Version je State) empfehle ich **nicht**.

---

## 2. Begründung aus dem Ist-Bestand

Grundlage ist `docs/befund_regulatorischer_wissensbestand_ist.md` (Abschnitt D.1) und
`backend/app/models.py`.

| # | Befund im Ist-Modell | Folge für 1:1-Alias | Folge für 1:n (Empfehlung) |
|---|---|---|---|
| 1 | `RegulatoryVersion.sector` ist Pflichtfeld. Die RVs sind **spartenbezogen**: RV 1 = Gas, RV 2 = Gas, RV 3 = Strom. | Ein State (z. B. 01.10.2026) umfasst Strom **und** Gas (Mitteilung 56: „spartenübergreifend“). 1:1 erzwingt entweder eine Sparten-RV „beide“ oder zwei States je Stichtag. Beides widerspricht Abschnitt 15 (ein State je Stichtag). | State 01.10.2026 → RV Gas + RV Strom. Die Sparte bleibt dort, wo sie heute steht. |
| 2 | RV 1 (Gas G1.1, ab 01.04.2026) und RV 3 (Strom S2.1, ab 06.06.2025) sind **beide Teil desselben regulatorischen Stands 01.04.2026**, haben aber verschiedene `valid_from`. | Nicht abbildbar: ein State kann nicht zwei RVs haben. | Beide RVs können auf denselben State zeigen, sobald es ihn gibt. |
| 3 | Der Requirement-Code ist **je RV** eindeutig (`uq_requirement_code_per_version`). `Assessment.regulatory_version_id` ist Kundenbezug. `is_active` und `summary` sind **Produktsemantik** (Default für neue Assessments, kuratierte Release-Notiz). | Regulatorische Tatsache (State, unveränderlich nach Bestätigung) und Produktsteuerung (RV, aktiv/inaktiv, kuratiert) würden in einem Objekt vermischt. | Getrennte Lebenszyklen: der State wird bestätigt und bleibt bestehen, die RV wird für Kunden aktiviert. |
| 4 | MessageDefinitions hängen an der RV und tragen `quelle_hash` (SHA-256 der Originaldatei). | — | Der Hash verbindet später eindeutig mit `RegulatoryDocumentFile.sha256`, ohne Umbau der MessageDefinitions. |
| 5 | RV 3 (Strom 06.06.2025) liegt **vor** jedem State, den Atlas aufbauen soll (Abschnitt 13: erster State ist 01.10.2026). | Pflichtbezug unmöglich. | `regulatory_state_id` ist nullable, historische RVs bleiben unverändert. |

**Zusatzargument aus Etappe 1:** Die maßgebliche Einheit ist nicht die Dokumentversion,
sondern die **Fassung** (z. B. UTILMD AHB Gas 1.2 Stand 06.08.2026). Sie ändert sich
**innerhalb** einer Version zwischen Veröffentlichung und Stichtag, mit neuen Seiten- und
Kapitelnummern. Das kann nur eine eigene Ebene unter dem State tragen, nicht ein
Versionsstring an der RV.

---

## 3. Skizze der Objekte (nur Konzept, keine Migration)

| Objekt | Kernfelder | Entspricht im Provenienzschema v0 |
|---|---|---|
| `RegulatoryState` | name, stichtag, basis_mitteilung, ergaenzende_quelle, status (ENTWURF / BESTÄTIGT / ABGELÖST), vorgaenger_state_id | Datei-Kopf (`stichtag`) |
| `RegulatoryDocument` | dokument_schluessel, dokumenttyp, kategorie, nachrichtentyp, sparte, bdew_topic_id | `dokument` |
| `RegulatoryDocumentVersion` | document_id, version, veroeffentlicht_am, gueltig_ab, gueltig_bis (+ Art, Belege), mitteilung, dokumentstatus, vorgaenger_id | `dokumentversion` |
| `RegulatoryDocumentFile` | document_version_id, fassungstyp, fehlerkorrekturstand, quelle, url, sha256, seiten, deckblatt, abruf | `fassungen[]` |
| `RegulatoryStateDocumentVersion` | state_id, document_version_id, massgebliche_file_id, regelschritte, begruendung, fragenkatalog | `auswahl`, `fragenkatalog`, `hinweise` |
| `RegulatoryVersion` (bestehend) | **+ regulatory_state_id (nullable)**, sonst unverändert | — |

Grundsätze:

* **Nichts wird überschrieben (Abschnitt 10).** Ein neuer State (01.04.2027) legt neue
  Verknüpfungen an. Dokumentversionen und Fassungen werden wiederverwendet, wenn sie
  fortgelten.
* **Fortgeltende Dokumente** (z. B. COMDIS 1.0h aus Mitteilung 54) erscheinen im State
  01.10.2026 als Verknüpfung mit `dokumentstatus = verbindlich_fortgeltend`. Das ist die
  Semantik von `get_effective()` aus dem Befund 01.04.2026.
* **Gültig-bis** ist ein belegtes Datum mit Art (`ausdruecklich` / `abgeleitet` / `offen`).
  Es wird beim Folgestand ergänzt, nie durch Löschen ersetzt.

## 4. Zuordnung der bestehenden RVs (falls bestätigt)

| RV | heute | `regulatory_state_id` |
|---|---|---|
| 1 | GeLi Gas 2.0 / UTILMD Gas G1.1, ab 01.04.2026, aktiv | NULL (State 01.04.2026 wird nach Abschnitt 13 nicht aufgebaut) |
| 2 | Mitteilung 56 / ab 01.10.2026, Gas, inaktiv | → State „Marktkommunikation 01.10.2026“ |
| 3 | UTILMD Strom 2.1, ab 06.06.2025 | NULL |
| — | **fehlt:** Strom-RV für 01.10.2026 | **offene Produktentscheidung P-1** (Ticket #64), wird in Etappe 7/8 ausdrücklich aufgeführt |

## 5. Zu bestätigen

1. 1:n (State über spartenbezogenen RVs) statt 1:1-Alias.
2. `regulatory_state_id` nullable, bestehende RVs werden nicht umgedeutet.
3. Die Fassung (Datei mit SHA-256) wird eine eigene Ebene unter der Dokumentversion, die
   maßgebliche Fassung eine Eigenschaft der State-Verknüpfung.
4. Umsetzung erst nach Etappe 8 (Übergabebericht). Bis dahin bleiben die JSON-Artefakte die
   einzige Ablage.
