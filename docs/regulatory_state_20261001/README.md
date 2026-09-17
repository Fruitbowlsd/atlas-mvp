# Regulatory State 01.10.2026 — Rechercheartefakte

Ticket: #64. Recherche zum vollständigen regulatorischen Stand der Marktkommunikation zum
Stichtag **01.10.2026**. Es sind ausschließlich Rechercheartefakte zur menschlichen Prüfung:
keine Schemaänderung, kein Import, kein Schreibvorgang in die Datenbank.

| Etappe | Inhalt | Status | Artefakte |
|---|---|---|---|
| 0 | Fundament: Mitteilung 56 erfassen, BK6/BK7, Aktualität | **abgeschlossen** | [`etappe0_fundament.md`](etappe0_fundament.md), [`etappe0_rohliste_mitteilung56.json`](etappe0_rohliste_mitteilung56.json) |
| 1 | Pilot UTILMD (AHB/MIG Strom + Gas) | **abgeschlossen**, Schema und 9a-Vorschlag zur Bestätigung | [`etappe1_utilmd.md`](etappe1_utilmd.md), [`etappe1_utilmd_provenienz.json`](etappe1_utilmd_provenienz.json), [`provenienz_schema.json`](provenienz_schema.json), [`vorschlag_regulatory_state_modell.md`](vorschlag_regulatory_state_modell.md) |
| 2 | Übrige EDIFACT-Nachrichtentypen Strom | offen | — |
| 3 | Übrige EDIFACT-Nachrichtentypen Gas | offen | — |
| 4 | PID, Codelisten, Allgemeine Festlegungen | offen | — |
| 5 | Entscheidungsbaum-Diagramme | offen | — |
| 6 | Übertragungsweg / AS4 / API / XML | offen | — |
| 7 | Konsolidierung, Widersprüche, Regulatory-State-Objekt, Vorschlag `RegulatoryVersion` | offen | — |
| 8 | Übergabebericht | offen | — |

## Bestätigte Grundlagen

* Provenienzschema: [`provenienz_schema.json`](provenienz_schema.json) (v0 bestätigt am 17.09.2026; v0.1 ergänzt `ersetzt_durch`); Rollen: [`rollendefinition.md`](rollendefinition.md)
* Modell: Regulatory State als Ebene oberhalb von `RegulatoryVersion`, 1:n ([`vorschlag_regulatory_state_modell.md`](vorschlag_regulatory_state_modell.md)), bestätigt am 17.09.2026, **noch nicht umgesetzt**

## Offene Produktentscheidungen

* **P-1:** Für den 01.10.2026 gibt es keine Strom-`RegulatoryVersion` (siehe #64). Wird in Etappe 7 und 8 ausdrücklich aufgeführt.

## Quellenabzüge (`quellen/`)

| Datei | Quelle | Abruf (UTC) | SHA-256 |
|---|---|---|---|
| `bnetza_mitteilungsliste_bk6_bk7_20260917.txt` | BNetzA, Liste „Mitteilungen zu den Datenformaten“ (Textauszug) | 2026-09-17 17:10 | `f4a2910586158bf709d4a86dbe4d384cbd9f521e30a16806997a36bda0e10c87` |
| `bnetza_mitteilung_55_20260202.txt` | BNetzA Mitteilung 55 (Textauszug) | 2026-09-17 17:10 | `a0be986b8e3d9009eafee506d199a05e8553c6c53b422ad1448690838fbfaff8` |
| `bnetza_mitteilung_56_20260401.txt` | BNetzA Mitteilung 56 (Textauszug) | 2026-09-17 17:10 | `2637b3a7445ada5fb71af0cbaa879a6bc521726d29120c9990ba865786dcd0b4` |
| `bnetza_mitteilung_57_20260731.txt` | BNetzA Mitteilung 57 (Textauszug) | 2026-09-17 17:10 | `80f2c11cea78e96997339d91a18c5d3f10f961a033e07a9739e89f1d00e25c7a` |
| `bdew_mako_api_documents_20260917.json` | `https://www.bdew-mako.de/api/documents` (unverändert) | 2026-09-17 17:12:32 | `016a6f8c8944eed721af08e6c97c55e4740ed056996cba482e70467401fb709f` |
| `bdew_mako_api_topicgroups_20260917.json` | `https://www.bdew-mako.de/api/topicGroups` (unverändert) | 2026-09-17 17:12 | `e384fecdb8ee756e0b094ec885449a941bdf49147cd3d006fa9383e04dd9aec6` |

Die Textauszüge der BNetzA sind aus dem HTML-Hauptbereich erzeugt, Linkziele der Anlagen
stehen in eckigen Klammern. Die PDF-Anlagen selbst sind nicht eingecheckt. URL und SHA-256
stehen in der Rohliste.
