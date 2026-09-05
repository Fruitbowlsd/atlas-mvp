# Technischer Befund — Anwendungsübersicht der Prüfidentifikatoren 3.3 (Issue #54)

**Status: umgesetzt für Scoping A.** Der Befund entstand am STOP-Punkt nach §5 des
Auftrags — ohne Implementierung, Schemaänderung, Import oder LLM. Er ist unverändert
dokumentiert; die anschließende Freigabe lautete **„PID → `ProcessIdentifier`, sonst
nichts"**. Was daraus umgesetzt wurde und was ausdrücklich zurückgestellt bleibt, steht
in Abschnitt H am Ende dieses Dokuments.

Alle Zahlen stammen aus einem rein lesenden Durchlauf über **alle 82 Seiten** des
Dokuments, nicht aus einer Stichprobe.

---

## A. Dokument

| | |
|---|---|
| Datei | `backend/data/regulatory/PID_3_3_Konsultationsfassung_20250801.pdf` |
| SHA-256 | `6b4f5e362703d481a4e362f19abd43c197dc5d1b1643750b4a59cb92d9c7139a` |
| Seiten | 82 |
| Version laut Deckblatt | **3.3**, Konsultationsfassung, Publikationsdatum **01.08.2025** |
| Version laut Kopfzeile jeder Seite | „Anwendungsübersicht der Prüfidentifikatoren 3.3 01.08.2025" |
| Autor laut PDF-Metadaten | BDEW (`Producer: Microsoft® Excel® für Microsoft 365`) |
| Bezug | BNetzA, Mitteilung Nr. 52, Anlage `PID_3_3_Konsultationsfassung_20250801.pdf` (HTTP 200, 3.010.786 Bytes) |
| Ziel-`RegulatoryVersion` | `[1] GeLi Gas 2.0 / UTILMD Gas G1.1 (gültig ab 01.04.2026)` (`is_active = 1`) |

**Versionsprüfung bestanden** (§3): Die Version ist an zwei unabhängigen Stellen im
Dokument selbst belegt — Deckblatt (S. 1) und Fußzeile aller 82 Seiten. Es war kein
Ausweichen auf 3.1/3.0 nötig. Dasselbe Muster wie bei AHB Gas 1.1: das Deckblatt trägt
den Vermerk „Konsultationsfassung", die BNetzA führt das Dokument unter Mitteilung 54
als ab 01.04.2026 anzuwendend.

---

## B. Strukturbefund je Tabellenkonzept

Das Inhaltsverzeichnis (S. 2) nennt **fünf** Tabellen. Die empirische Prüfung bestätigt
genau diese fünf — sie sind über die Kopfzeile jeder Seite (`Anwendungsübersicht der <X>`)
sauber voneinander abgegrenzt und überlappen nicht.

| # | Tabellenkonzept | Seiten | Spalten | Datenzeilen |
|---|---|---|---|---|
| — | Legende Übertragungsweg (Einleitung) | 5 | 2 | 4 |
| 1 | **Prüfidentifikator zu Prozessschritt / API Webservice zu Prozessschritt** | 7–77 | 21 | **1370** |
| 2 | **Tupel-Übersicht** | 78–79 | 5 | 68 |
| 3 | **Objekteigenschaften** | 80 | 4 | 11 |
| 4 | **Erweiterte Zuordnungslogik** | 81 | 3 | 9 (+ 5 Nicht-Datenzeilen: Leerzeile, „Legende:", 3 Legendeneinträge) |
| 5 | Änderungshistorie | 82 | 6 | 5 |

### Abweichungen gegenüber den Hypothesen aus §2

| Hypothese (aus Version 3.1) | Befund in 3.3 |
|---|---|
| „Prüfidentifikator zu Prozessschritt" als eigene Tabelle | ✅ vorhanden — **aber** vereint mit dem API-Konzept in **einer** Tabelle |
| „API-Webservice zu Prozessschritt" als eigene Tabelle | ❌ **keine eigene Tabelle**. API-Webservices sind Zeilen *derselben* Tabelle 1, erkennbar an `Übertragungsweg = API` (27 Zeilen); ihre Spalte `Prüfidentifikator` ist durchgängig `--`, der Endpunktpfad steht in der Beschreibungsspalte |
| „Antwort auf Prüfidentifikator" als eigene Tabelle | ❌ **keine eigene Tabelle**. Es ist die **Spalte 4** von Tabelle 1, und sie heißt „**Reaktion** auf Prüfidentifikator" |
| „Zuordnung zu einem Objekt / Geschäftsvorfall" | ✅ als **Spalten 12/13** von Tabelle 1, nicht als eigene Tabellen |
| „Erweiterte Zuordnungslogik", eigene Tabelle mit drei Spalten | ✅ **bestätigt** — S. 81, exakt drei Spalten, Referenzcodes `EZ-01`…`EZ-09` |
| „Objekteigenschaft" | ✅ als Spalte 15 von Tabelle 1 **und** als eigene Tabelle 3 („Objekteigenschaften", `OE-01`…`OE-11`) |
| „Tupel-Übersicht" | ✅ bestätigt, Tabelle 2 |
| „Änderungshistorie" | ✅ vorhanden, S. 82 — **nicht verarbeitet** (§11) |

**Zusätzlich, in §2 nicht erwartet:** die Spalten `Übertragungsweg`, `API-Kennung`,
`Sparte Strom`, `Sparte Gas`, `Aktion`, `Kommunikation von`, `Kommunikation an`,
`Prozessschritt aus Kapitel` / `Bezeichnung aus Sequenzdiagramm` /
`Prozessschritt aus Sequenzdiagramm` sowie eine im gesamten Dokument **leere** Spalte
`Fußnote`.

### Tabelle 1 — Spaltenbelegung (alle 1370 Zeilen)

Die Kopfzeile ist auf **allen 71 Seiten byte-identisch** — genau eine Variante. Drei
Kopfzellen sind im PDF um 90° gedreht und kommen deshalb als Zeichensalat an
(`'m\no\nrtS\ne\ntra\np\nS'` = „Sparte Strom", `'e sa\ntra G\np\nS'` = „Sparte Gas",
`'e\nto\nn\nß\nu\nF'` = „Fußnote").

| # | Spalte | gefüllt | `--` | leer | versch. Werte |
|---|---|---|---|---|---|
| 0 | Lfd. Nr. | 1362 | 0 | **8** | 1362 |
| 1 | AHB | 1339 | 31 | 0 | 19 |
| 2 | Beschreibung des Anwendungsfalls aus dem AHB (EDIFACT) / API-Webservice (API) | 1369 | 1 | 0 | 374 |
| 3 | Prüfidentifikator | 1312 | 58 | 0 | **486** |
| 4 | Reaktion auf Prüfidentifikator | 212 | 1158 | 0 | 81 |
| 5 | Prozessbeschreibung | 1370 | 0 | 0 | 24 |
| 6 | Prozessschritt aus Kapitel | 136 | 6 | 1228 | 97 |
| 7 | Bezeichnung aus Sequenzdiagramm | 1228 | 0 | 142 | 246 |
| 8 | Prozessschritt aus Sequenzdiagramm | 1221 | 7 | 142 | 22 |
| 9 | Aktion | 1348 | 22 | 0 | 479 |
| 10 | Kommunikation von | 1370 | 0 | 0 | 58 |
| 11 | Kommunikation an | 1370 | 0 | 0 | 67 |
| 12 | Zuordnung zu einem Objekt | 513 | 857 | 0 | 30 |
| 13 | Zuordnung zu einem Geschäftsvorfall | 681 | 689 | 0 | 40 |
| 14 | Erweiterte Zuordnung | 59 | 1311 | 0 | 9 |
| 15 | Objekteigenschaft | 58 | 1312 | 0 | 11 |
| 16 | Sparte Strom | 1012 | 358 | 0 | 2 (`X`/`x`) |
| 17 | Sparte Gas | 358 | 1012 | 0 | 1 |
| 18 | Übertragungsweg | 1349 | 21 | 0 | 4 |
| 19 | API-Kennung | 27 | 1343 | 0 | 3 |
| 20 | Fußnote | **0** | 0 | 1370 | 0 |

---

## C. Antworten auf die Untersuchungsfragen (§4)

### §4.3 — Sortierung der Haupttabelle

**Weder nach PI-Nummer noch nach laufender Nummer sortiert.** Beides empirisch geprüft:

* `Prüfidentifikator` numerisch aufsteigend? **nein**
* `Lfd. Nr.` numerisch aufsteigend? **nein**

Die Tabelle folgt der Prozessreihenfolge — dieselbe Beobachtung wie in der benachbarten
Version 4.0. Die `Lfd. Nr.` ist keine Ordinalzahl, sondern eine **dünn besetzte,
stabile ID**: Werte von 1 bis 38890, aber nur 1362 davon vergeben (37528 Lücken), dafür
**duplikatfrei**. Die Änderungshistorie referenziert genau über diese IDs
(z. B. „Lfd.Nr.: 37000-38890"), die ID ist also der versionsübergreifende Anker des
Dokuments — für eine spätere Delta-Engine der relevante Schlüssel.

**Aber:** 8 Zeilen (S. 63 und S. 74) haben **gar keine** `Lfd. Nr.`. Es sind keine
Fortsetzungszeilen, sondern vollständig gefüllte Datenzeilen (z. B. S. 74: PI 44150,
44137, 44151, 44152, 44138). Die `Lfd. Nr.` scheidet damit als alleiniger Primärschlüssel
aus.

### §4.4 — Verweislogik der Erweiterten Zuordnungslogik

**Durchgängig konsistent, in beide Richtungen geschlossen.**

| Referenztyp | in Tabelle 1 verwendet | definiert | nicht auflösbar | definiert, aber ungenutzt |
|---|---|---|---|---|
| `EZ-xx` (Tabelle 4) | 9 versch., 59 Zeilen | 9 | **0** | **0** |
| `OE-xx` (Tabelle 3) | 11 versch., 58 Zeilen | 11 | **0** | **0** |
| `ZO-*` / `ZG-*` (Tabelle 2) | 61 versch., 1283 Vorkommen | 68 | **1** (`ZG-T33`) | 8 (davon 7 nur indirekt über Tabelle 4 erreicht) |

Die Tabelle 4 selbst referenziert 12 Tupel, **alle** in Tabelle 2 auflösbar. Von den 8
in Tabelle 1 nie direkt genannten Tupeln werden 7 (`ZG-T15`, `ZG-T18`, `ZG-T56`,
`ZG-T57`, `ZO-F3`, `ZO-T37`, `ZO-T40`) ausschließlich über die EZ-Indirektion erreicht —
die Verweiskette schließt sich also. Genau **ein** Tupel, `ZG-T4`, ist definiert und
nirgends referenziert.

**Zwei nicht auflösbare Verweise (§14 — nicht geraten, hier ausgewiesen):**

1. **`ZG-T33`** — in Tabelle 1 auf S. 24/25 **neunmal** in der Spalte „Zuordnung zu einem
   Geschäftsvorfall" verwendet (Lfd. Nr. 9290–9380, PI 21037/21038, IFTSTA AHB,
   Redispatch), aber **in der Tupel-Übersicht nicht definiert**. `ZO-T33` existiert;
   ob es sich um einen Tippfehler handelt, ist nicht entscheidbar und wird nicht geraten.
2. **PI 44108** — S. 74, Lfd. Nr. 38080, Spalte „Reaktion auf Prüfidentifikator"; dieser
   PI kommt in der gesamten Tabelle 1 nicht als eigener Anwendungsfall vor und ist auch
   der MIG G1.1 unbekannt.

**Die Zuordnungsspalten sind keine reinen Codefelder.** 42 Zellen enthalten
Bedingungslogik als Fließtext statt eines Codes, z. B.:

```
bei SG4 STS+E01++A04 dann ZO-T1
wenn nicht SG4 STS+E01++A04 dann ZG-T1 bei SG4 STS+E01++A04 dann ZG-T36
wenn SG29 FTX+Z08 vorhanden ZG-T41; wenn SG29 FTX+Z10 vorhanden ZG-T52; …
```

Dazu kommen Mehrfachtupel (`ZO-T14 und ZO-T21` — 50 Zeilen; `ZO-T14, ZO-T20 und ZO-T21`).
Diese Zellen in eine Codeliste zu zerlegen wäre fachliche Interpretation (§8).

### §4.5 — Verhältnis zu Prompt 1 (MIG-PI-Namen)

**Zentrales Ergebnis: PID und MIG liefern nicht konkurrierende Namen, sondern
verschieden zerlegte Information.**

| | Anzahl |
|---|---|
| eindeutige PIs in PID 3.3 | 486 |
| PIs in Atlas (aus Prompt 1 / Seed) | 91 |
| in beiden | **88** |
| nur in PID | **398** |
| nur in MIG/Atlas | **3** (`44096` TSIMSG/Deklarationsliste an MGV, `44097` an BKV, `44172` SDÄ Gas / Anfrage an MSB mit Abhängigkeit MSB an NB) |
| davon Bezeichnung **string-identisch** | **0** |

Die Bezeichnungen weichen bei **allen 88** gemeinsamen PIs ab, aber systematisch:

* **43 Fälle — reine Präfixdifferenz.** Die MIG stellt die Prozessfamilie voran, die PID
  führt sie in einer eigenen Spalte:
  `MIG "GeLi Gas / Anmeldung NN"` ↔ `PID "Anmeldung NN"` + `Prozessbeschreibung "GeLi Gas 2.0"`.
* **45 Fälle — darüber hinaus abweichender Wortlaut.** Hier zerlegt die PID zusätzlich die
  Rollenrichtung in eigene Spalten, die die MIG in den Namen einbaut:

  | PI | MIG (Prompt 1) | PID 3.3 |
  |---|---|---|
  | 44010 | `GeLi Gas / Abmeldeanfrage des NB` | `Abmeldungsanfrage des NB` |
  | 44060 | `WiM Gas / Antwort auf die MSB Geschäftsdatenanfrage` | `Antwort auf die Geschäftsdatenanfrage` |
  | 44148 | `SDÄ Gas / Anfrage an MSB mit Abhängigkeiten NB [Berechtigt] an MSB` | `Anfrage an MSB mit Abhängigkeiten` (+ `Kommunikation von = NB`, `an = MSB`) |
  | 44161 | `SDÄ Gas / Änderung vom MSB ohne Abhängigkeiten AG an AF` | `Antwort auf Änderung` |
  | 44180 | `SDÄ Gas / Anfrage der komplexen Marktlokationsstruktur LF an NB` | `Anfrage der Marktlokationsstruktur` |

**Die PID-Bezeichnung ist kein tauglicher Ersatz für den MIG-Namen**, weil sie ohne die
Nachbarspalten nicht eindeutig ist: `44147` und `44148` tragen beide die Beschreibung
„Anfrage an MSB mit Abhängigkeiten"; unterschieden werden sie erst durch
`Kommunikation von/an`. Empfehlung daher: **`ProcessIdentifier.name` unter keinen
Umständen aus der PID überschreiben** (Fall C aus Prompt 1 konsequent weitergeführt),
Abweichungen ausschließlich im Report ausweisen.

**Was die PID zusätzlich liefert und die MIG nicht:**

* **Die AHB-Zuordnung, und zwar je PI eindeutig.** Von 486 PIs hat **kein einziger**
  widersprüchliche Werte in der AHB-Spalte. 19 verschiedene Werte (`UTILMD AHB Strom`
  331×, `MSCONS AHB` 170×, `IFTSTA AHB` 159×, `UTILMD AHB Gas` 130×, …).
  **Achtung:** das ist eine Zuordnung auf **Dokument**ebene, **kein AHB-Kapitel**. Die
  in §2 formulierte Hypothese „inkl. Verweis auf das jeweilige AHB-Kapitel" ist damit
  **nicht bestätigt**. Kapitelangaben gibt es nur in Spalte 6 („Prozessschritt aus
  Kapitel", z. B. `Kap. B 5.1.3 Nr. 7`) — und die verweisen auf die
  **Prozessbeschreibung**, nicht auf das AHB.
* Übertragungsweg, Sparte, Zuordnungs-/Tupellogik, Reaktionsbeziehung, Prozessschritt.
* **Nicht** eindeutig je PI und deshalb *nicht* nach `ProcessIdentifier` übertragbar:
  `Kommunikation von` (113 von 486 PIs mehrdeutig), `Kommunikation an` (142),
  `Prozessbeschreibung` (100), `Zuordnung zu einem Objekt` (61),
  `…Geschäftsvorfall` (69). Rolle und Zuordnung hängen am **Prozessschritt**, nicht am PI.
  Die heute leeren Felder `sender_role`/`receiver_role` lassen sich aus der PID also
  **nicht** befüllen, ohne Information zu vernichten.

### §4.6 — Semantische Klassifikation und Verlustfrage

| Konzept | Klassifikation | Verlust bei Nicht-Modellierung |
|---|---|---|
| **T1 · PI ↔ AHB-Dokument** (Sp. 1+3, je PI eindeutig) | **passt in bestehendes Modell** als ergänzendes Attribut — `ProcessIdentifier` hat `message_type` (heute Default `"UTILMD"` für alle 91 Einträge, faktisch ungepflegt) | Atlas weiß nicht, in welchem AHB ein PI beschrieben ist. Für 398 heute unbekannte PIs fehlte damit der Einstiegspunkt in die AHB-Extraktion. Zugleich ist es die einzige belastbare Brücke zwischen PID und der bereits laufenden AHB-Pipeline. |
| **T2 · Prüfidentifikator (Nummer + Bezeichnung)** | **passt in bestehendes Modell** (`ProcessIdentifier`), Fall A/B/C aus Prompt 1 | 398 regulatorisch gültige PIs bleiben Atlas unbekannt — die Wissensbasis kennt nur den Gas-UTILMD-Ausschnitt und ist über Strom, MSCONS, IFTSTA, ORDERS/ORDRSP, REMADV, INVOIC, PARTIN, INSRPT, COMDIS, UTILTS blind. |
| **T3 · Prozessschritt-Zuordnung** (Sp. 5–11: Prozessbeschreibung, Kapitel/Sequenzdiagramm, Aktion, Kommunikation von/an) | **braucht neues Modell.** 1370 Zeilen, N:M zwischen PI und Prozessschritt (ein PI in bis zu 47 Schritten: PI 33001). Kein bestehendes Atlas-Modell bildet einen Prozessschritt ab. | Die gesamte Kette „Prozess → Prozessschritt → PI" fällt weg. Damit auch die Rolleninformation (Kommunikation von/an), die heute in Atlas für 75 von 91 PIs schlicht leer ist. Ohne dieses Konzept bleibt die PID eine Namensliste — genau das, was §2 ausschließt. |
| **T4 · Reaktionsbeziehung** (Sp. 4) | **braucht neues Modell** (gerichtete PI→PI-Kante), alternativ Attribut am Prozessschritt. 114 PI-Referenzen + 95 `x`-Zielmarken | Atlas kann nicht sagen, welche Antwortnachricht auf welche Anfrage gehört. Für Testfallableitung („Anfrage 44150 → erwartete Antwort 44151/44152") ist genau das der Kern. |
| **T5 · Tupel-Übersicht** (Tabelle 2, 68 Zeilen) | **grenzt an `CodeList`/`CodeListEntry`** — Code + Bezeichnung + Beschreibung —, aber mit vier fachlich getrennten Feldern (Segmentangabe, Tupel-Arität/Bedeutung, Bezeichnung der Datenelemente, Nachrichtentyp). In `CodeListEntry` gepresst würde die Segmentangabe verloren gehen. **Vorschlag: eigenes Modell.** | Die verbindliche Festlegung, **über welche EDIFACT-Datenelemente** ein eingehender Geschäftsvorfall zugeordnet wird (`ZO-T1 = SG5 LOC DE3225`), geht verloren. Das ist die einzige Stelle, an der die Regulierung Zuordnungsregeln maschinell prüfbar macht — und die einzige direkte Brücke von der PID zur MIG-Segmentgrammatik aus Prompt 4. |
| **T6 · Zuordnungslogik in Tabelle 1** (Sp. 12–15) | **braucht neues Modell** (Kante Prozessschritt → Tupel), plus Rohwertfeld für die 42 Freitext-Zellen | Die Verknüpfung „welcher Anwendungsfall wird über welches Tupel zugeordnet" fehlt; die Tupel-Übersicht wäre dann ein Glossar ohne Anwender. |
| **T7 · Erweiterte Zuordnungslogik** (Tabelle 4, 9 Zeilen) | **braucht neues Modell** — oder pragmatisch: Code + zwei Textfelder | Die Fallunterscheidungen für 59 Zeilen der Haupttabelle sind nicht mehr auflösbar; `EZ-01` bliebe ein toter Verweis. Umfang gering (9 Zeilen), Formelsprache aber eigen (`[5] ∧ [3] -> [ZG-T42] --> …`) und **nicht** ohne Interpretation zerlegbar. |
| **T8 · Objekteigenschaften** (Tabelle 3, 11 Zeilen) | **passt strukturell in `CodeList`/`CodeListEntry`** (Code `OE-01` + Beschreibung), mit einem Zusatzfeld für `Identifikator` und `Segment` | Die Präzisierung „welche Objekteigenschaft muss zusätzlich zum Tupel stimmen" fehlt; 58 Zeilen der Haupttabelle verlieren ihren Verweis. Geringer Umfang, klar abgegrenzt. |
| **T9 · Übertragungsweg / API-Kennung** (Sp. 18/19 + Legende S. 5) | **passt in `CodeList`** (4 Kürzel, geschlossene Werteliste) | Atlas weiß nicht, ob ein Anwendungsfall über AS4, Marktprozess-Weg, Redispatch-Weg oder API läuft — für Betriebs- und Migrationsfragen relevant, für die Nachrichteninhalte nicht. |
| **T10 · Sparte Strom/Gas** (Sp. 16/17) | **ergänzendes Attribut**; kein bestehendes Feld an `ProcessIdentifier` | Der Spartenbezug geht verloren. Wichtig, weil er sauber komplementär ist: **jede** der 1370 Zeilen ist genau einer Sparte zugeordnet (1012 Strom / 358 Gas, keine Zeile beides, keine Zeile keines). |
| **T11 · API-Webservice-Zeilen** (27 Zeilen, `Übertragungsweg = API`) | **braucht neues Modell** — kein PI, Identität ist der Endpunktpfad (`/steuerbefehl/konfiguration/`) + `API-Kennung` (`API00001`–`API00003`) | Der ab 3.1 neue, EDIFACT-freie Kommunikationsweg bleibt unsichtbar. Umfang heute klein (27 von 1370), regulatorisch aber ein Wachstumsfeld. |
| **T12 · Änderungshistorie** (Tabelle 5) | **§11 — ausgeklammert** | (siehe Abschnitt E) |

### §4.7 — Beziehungskette an echten Beispielen

Fünf Zeilen aus dem echten Dokument, vollständig durchgezeichnet:

**① Lfd. Nr. 38210 (S. 74) — Kette vollständig, inkl. Reaktions-PI**

```
Prozessbeschreibung  GeLi Gas 2.0
 └ Sequenzdiagramm   "Anfrage zur Stammdatenänderung vom MSB an NB (verantwortlich)", Schritt 4
    └ Aktion         "Antwort auf Änderung vom NB an LF"   (LF → NB, Sparte Gas, AS4)
       └ PI          44161            [Atlas kennt ihn: MIG "SDÄ Gas / Änderung vom MSB ohne Abhängigkeiten AG an AF"]
          └ Reaktion auf PI 44160     → auflösbar, 44160 ist Lfd. 38180 derselben Tabelle
             └ Zuordnung Geschäftsvorfall  ZG-T1
                └ Tupel-Übersicht     ZG-T1 = SG6 RFF+TN DE1154, 1-Tupel Vorgangsnummer, UTILMD
                   └ MIG-Grammatik (Prompt 4)  SG6/RFF/1154 → im Segmentlayout vorhanden
       └ AHB         "UTILMD AHB Gas"   ← nur Dokument, KEIN Kapitel
```
→ Kette trägt **bis zur MIG-Grammatik**. Sie bricht beim Übergang ins AHB: kein Kapitelverweis.

**② Lfd. Nr. 783 (S. 9) — Kette bricht bei der Erweiterten Zuordnung ab**

```
Prozessbeschreibung  "Prozesse zum Informationsaustausch … Herkunftsnachweisregister (HKN-R) … (UBA)"
 └ Prozessschritt aus Kapitel  "Kap. 2.3 Nr. 5"    (Kapitel der Prozessbeschreibung, nicht des AHB)
    └ Aktion         "Antwort Messwerte Abo"   (NB → RB HKN-R, Sparte Strom, Übertragungsweg MP)
       └ PI          13017 "Zählerstand (Strom)"     [Atlas unbekannt]
          └ Zuordnung Objekt = "--", Geschäftsvorfall = "--"
          └ Erweiterte Zuordnung  EZ-01
             └ Tabelle 4  "([5] ∧ [3]) -> [ZG-T42] --> [1] -> [ZO-T35] --> -> [ZO-T21] -->** ⊻ …"
                └ referenziert ZG-T42, ZO-T35, ZO-T14, ZO-T20, ZO-T21 — alle in Tabelle 2 auflösbar
```
→ Maschinell endet die Kette hier: die EZ-Formel ist **auflösbar, aber nicht deterministisch
zerlegbar**. Die Voraussetzungen `[1]`…`[6]` stehen als deutscher Fließtext daneben
(„wenn RFF+AGK (Konfigurations-ID) vorhanden"). Auswertbar wäre das nur mit Interpretation.

**③ Lfd. Nr. 7120 (S. 16) — Kette bricht in der Zuordnungsspalte selbst ab**

```
MaBiS → "Austausch der Lieferantenclearingliste zwischen NB und LF (inkl. Abonnierung)", Schritt 3
 └ Aktion "Rückmeldung zur LF-CL"  (LF → NB, Strom, AS4)
    └ PI 55066 "Korrekturliste zu Lieferantenclearingliste"      [Atlas unbekannt]
       └ Zuordnung Objekt            "bei SG4 STS+E01++A04 dann ZO-T1"
       └ Zuordnung Geschäftsvorfall  "wenn nicht SG4 STS+E01++A04 dann ZG-T1 bei SG4 STS+E01++A04 dann ZG-T36"
```
→ Die Zelle ist **kein Code**, sondern eine Bedingung. Der Tupelcode lässt sich per Regex
herausziehen, die Bedingung nicht ohne Interpretation. Betrifft 42 Zellen.

**④ Lfd. Nr. 9290 (S. 24) — Kette bricht an einem nicht definierten Tupel ab**

```
Kommunikationsprozesse Redispatch → "Ermittlung und Abstimmung der abrechnungsrelevanten
Ausfallarbeit – Prognosemodell", Schritt 2
 └ Aktion "Bestätigung Ausfallarbeit"  (BTR → NB, Strom, Übertragungsweg RD)
    └ PI 21038 "Ansicht BTR"   [Atlas unbekannt],  AHB "IFTSTA AHB"
       └ Zuordnung Geschäftsvorfall  ZG-T33
          └ Tupel-Übersicht:  ✗ NICHT VORHANDEN
```
→ Harter Abbruch, 9 Zeilen betroffen. Dokumentfehler, wird nicht geraten (§14).

**⑤ Lfd. Nr. 23350 (S. 46) — API-Zweig, Kette ohne Prüfidentifikator**

```
"API-Webdienste zur prozessualen Abwicklung von Steuerungshandlungen …"
 └ Endpunkt  /steuerbefehl/vorlaeufigePositiveAntwort/     API-Kennung API00001
    └ Prüfidentifikator  "--"      ← es gibt keinen
    └ Reaktion auf PI    "/steuerbefehl/konfiguration/, /steuerbefehl/initialZustand/"
                                    ← PI-Spaltenlogik, aber mit Endpunktpfaden gefüllt
    └ Erweiterte Zuordnung EZ-04 → ZG-T57 / ZG-T56 → Tabelle 2 (Nachrichtentyp "API-Webservice")
```
→ Die Kette trägt, aber **nicht über den Prüfidentifikator**. Ein Datenmodell, das den PI
als Schlüssel voraussetzt, kann diese 27 Zeilen nicht aufnehmen.

**Zusammenfassung der Abbruchstellen**

| Übergang | trägt? |
|---|---|
| Prozessbeschreibung → Prozessschritt | ✅ 1370/1370 (1228 über Sequenzdiagramm, 136 über Kapitel, 6 ohne beides) |
| Prozessschritt → PI | ✅ 1312/1370 (58 Zeilen ohne PI: 27 API-Zeilen, 31 Prozessschritte ohne Anwendungsfall) |
| PI → Reaktions-PI | ⚠️ 114 Referenzen, davon **1 nicht auflösbar** (44108); 2 Zellen enthalten API-Pfade, 1 Zelle drei PIs auf einmal |
| PI → AHB | ⚠️ nur bis **Dokument**ebene — kein Kapitel, keine Verbindung zur AHB-Kapitelstruktur aus Prompt 0 |
| Zuordnungsspalte → Tupel | ⚠️ 1283 Vorkommen auflösbar, **9 Zeilen über `ZG-T33` nicht**; 42 Zellen mit Bedingungsfreitext |
| Tupel → MIG-Segment | ✅ Segmentangabe im Format `SG6 RFF+TN DE1154` — direkt anschlussfähig an das Segmentlayout aus Prompt 4 |
| EZ-Verweis → Tabelle 4 | ✅ 59/59 |
| OE-Verweis → Tabelle 3 | ✅ 58/58 |
| → Anforderung / Testfall | ❌ nicht im Dokument. Die PID endet beim Anwendungsfall. |

**Fazit zur Leitfrage:** Die Kette
`Prozess → Prozessschritt → PI → Nachricht → MIG-Grammatik` ist im Dokument
**tatsächlich vorhanden und rekonstruierbar**. Der Übergang `→ AHB-Anwendung` trägt nur
auf Dokumentebene, und `→ Anforderung → Testfall` ist nicht Gegenstand der PID.

### §4.8 — Verhalten von `page.extract_tables()`

**Deutlich freundlicher als MIG und AHB.** Das Dokument ist aus Excel erzeugt und hat
echte Zellgitter.

* Alle 1370 Zeilen der Tabelle 1 haben **exakt 21 Zellen** — keine einzige ragged row.
* **Mehrzeilige Zellen kommen als `\n` innerhalb der Zelle an**, nicht als Folgezeile.
  Das MIG-Problem aus Prompt 1 (Fortsetzungszeile zusammenführen) existiert hier **nicht**.
* **Keine Zeile läuft über einen Seitenumbruch.** Geprüft: 0 Zeilen mit ≤ 3 gefüllten Zellen.
* Die Kopfzeile wiederholt sich auf jeder der 71 Seiten identisch und ist stets Zeile 0.

**Aber: der Zeilenumbruch innerhalb einer Zelle zerreißt Wörter ohne Trennzeichen.**
`'Geschäftsprozesse\nfür EEG-\nÜberführungszeitre\nihen V1.0'`,
`'Marktraumumstell\nung'`, `'Netzbetreiberwech\nsel'`. Beim Zusammenfügen mit Leerzeichen
entsteht „Überführungszeitre ihen"; beim Zusammenfügen ohne Leerzeichen bricht
„Prozesse zum Informationsaustausch" korrekt zusammen, aber echte Wortgrenzen
verschwinden. **Es gibt keine deterministische Regel für beide Fälle** — dasselbe
Problem wie bei der MIG-Änderungshistorie in Prompt 1. Konsequenz für den Parser:
**Rohwert mit `\n` speichern**, nicht normalisieren.

Folgefehler: dieselbe Bedingung kommt in zwei Schreibweisen vor —
`'… FTX+Z07/Z09 vorhanden --'` (6×) und `'… FTX+Z07/Z09 vorhand en --'` (2×). Eine
Deduplizierung über normalisierten Text würde sie fälschlich zusammenführen.

### Weitere Auffälligkeiten im Rohwert (§8 — nicht korrigieren, nur ausweisen)

| Fund | Umfang |
|---|---|
| Sparte Strom als `x` statt `X` | 12 Zeilen (S. 67/68, Lfd. 35010–35130) |
| `Prozessbeschreibung` `MaBiS` (183×) vs. `MABIS` (1×) | 1 Zeile |
| PI 55672 mit zwei Schreibweisen: `Abr.-Daten BK-Abr. erz. Malo` / `… erz.. MaLo` | 2 Zeilen — einziger PI mit uneinheitlicher Beschreibung |
| Tabelle 4: `[7\|` statt `[7]` in EZ-04…EZ-07 | 4 Zeilen |
| Spalte `Fußnote` dokumentweit leer | 1370 Zeilen |
| Kopfzellen-Artefakt `'__'` vor „Tupel", „Identifikator Beschreibung", „Erweiterte Zuordnungslogik" | Tabellen 2, 3, 4 |
| Tabelle 4 enthält unterhalb der Daten einen **Legendenblock** (5 Zeilen: Leerzeile, „Legende:", `->`, `-->`, `**`) | muss als Nicht-Datenbereich erkannt werden |

### §4.9 — Umfangseinschätzung

**Vollumfang in einem Arbeitsschritt ist nicht ratsam.** Nicht wegen der Datenmenge
(1370 Zeilen sind weniger als die 388 CodeListEntry aus Prompt 3 an Aufwand), sondern
weil **fünf der zwölf Konzepte ein neues Datenmodell brauchen** (T3, T4, T6, T7, T11) und
Abschnitt §10 des Auftrags eigenständige Schemaänderungen ausschließt. Ein Import, der
nur die modellierbaren Teile aufnimmt, ist sofort machbar; alles Weitere setzt eine
Modellentscheidung voraus, die dieser Befund vorbereitet, aber nicht trifft.

---

## D. Scoping-Vorschlag

### Vorschlag A — in diesem Schritt umsetzen (kein Schemaeingriff nötig)

1. **Prüfidentifikatoren aus Tabelle 1 → `ProcessIdentifier`**, Fall A/B/C aus Prompt 1
   unverändert: 398 neue PIs anlegen, **88 bestehende unangetastet lassen** (Name,
   Prozessgruppe, Rollen), Abweichungen als `existing_name_preserved` und zusätzlich als
   **MIG↔PID-Diskrepanz mit beiden Werten** ausweisen (§9).
   *Nicht* befüllt werden `sender_role`/`receiver_role` — der Befund zeigt, dass die PID
   sie nicht je PI eindeutig festlegt.
2. **Vollständige Formprüfung über alle fünf Tabellenkonzepte** — inklusive der in §16
   geforderten Meldung „Tabellenkonzept nicht erkannt", falls eine künftige Version eine
   sechste Tabelle oder eine geänderte Kopfzeile mitbringt.
3. **Vollständiger, verlustfreier Lesevorgang aller fünf Tabellen im Report**, auch für
   die noch nicht modellierbaren Konzepte, samt der beiden nicht auflösbaren Verweise
   (`ZG-T33`, PI 44108) und der 42 Freitext-Zuordnungszellen.

Ergebnis: Atlas kennt danach 489 statt 91 Prüfidentifikatoren, die Formprüfung ist
versionsfest, und der Befund über die Beziehungsstruktur ist reproduzierbar aus Code
heraus belegt — ohne eine einzige Schemaänderung.

### Vorschlag B — als eigener Folgeschritt zurückstellen

| zurückgestellt | Begründung |
|---|---|
| **Prozessschritt-Modell** (T3) inkl. Rollen und Reaktionsbeziehung (T4) | Das ist der eigentliche Wert der PID und verdient eine eigene ADR — analog zu `adr_001_mig_nachrichtengrammatik.md` für Prompt 4. Ein N:M-Modell zwischen Prozess, Prozessschritt und PI berührt `ProcessGroup`, `Requirement` und die Delta-Logik. |
| **Tupel-Übersicht** (T5) + **Zuordnungslogik** (T6) + **Erweiterte Zuordnung** (T7) | Fachlich eine Einheit; getrennt importiert entstünden tote Verweise. Der Anschluss `SG6 RFF+TN DE1154` an das Segmentlayout aus Prompt 4 ist der interessanteste Teil — und genau deshalb kein Nebenprodukt eines PI-Imports. |
| **Objekteigenschaften** (T8) | Klein und `CodeList`-nah, aber ohne T6 ohne Anwender. Sinnvoll gemeinsam mit T5–T7. |
| **Übertragungsweg** (T9) als `CodeList` | 4 Werte, trivial — aber ohne Zeilenbezug (T3) ohne Aussage. |
| **API-Webservices** (T11) | Braucht ein Modell ohne PI-Schlüssel. 27 Zeilen; separat sauberer als in einen PI-Import gezwängt. |
| **Änderungshistorie** (T12) | Per §11 ausgeklammert. |

Falls stattdessen ein größerer Zuschnitt gewünscht ist: **A + T5 + T8 + T9** wäre die
nächstgrößere sinnvolle Stufe (Tupel-Übersicht, Objekteigenschaften und Übertragungsweg
als Wertelisten), setzt aber die Entscheidung voraus, ob die Tupel-Übersicht in
`CodeList`/`CodeListEntry` darf, obwohl dabei die Segmentangabe zwei Felder in eines
pressen müsste.

---

## E. Änderungshistorie (§11 — nur vermerkt, nicht verarbeitet)

| | |
|---|---|
| Ort | S. 82, Tabelle 5 |
| Spalten | `Änd-ID`, `Ort`, `Änderungen` (zweizeiliger Kopf: `Bisher` / `Neu`), `Grund der Anpassung`, `Status` |
| Datenzeilen | 5 (Änd-IDs 10000, 26756, 26061, 26062, 26063) |
| Umfang | eine Seite |

**Nicht verarbeitet.** Sie ist für eine spätere Delta-Engine bemerkenswert wertvoll,
weil sie sich präzise auf `Lfd. Nr.`-Bereiche der Haupttabelle bezieht („Lfd.Nr.:
37000-38890", „lfd.Nr. 25780 - 26040") und je Änderung Bisher-/Neu-Wert **und** Begründung
führt — der Dokumentstand liefert damit sein eigenes Diff mit. Das ist eine eigenständige
Aufgabe, hier bewusst nicht vorbereitet (gleiche Begründung wie die Ausklammerung der
EBD-Diagramme in Prompt 3).

---

## F. Modellerweiterungen — Vorschläge, hier NICHT umgesetzt (§10)

Kein neues Modell eingeführt. Zur Entscheidung vorgelegt:

1. **`ProcessStep`** — Prozessbeschreibung, Kapitel- *oder* Sequenzdiagramm-Bezug,
   Schrittnummer, Aktion, Kommunikation von/an, Sparte, Übertragungsweg, `Lfd. Nr.` als
   versionsübergreifende Quell-ID. Kernentität für die Beziehungskette; N:M zu
   `ProcessIdentifier`.
2. **`ProcessStepReaction`** oder Attribut an `ProcessStep` — gerichtete Reaktionskante
   PI → PI, plus Zielmarke `x`.
3. **`AssignmentTuple`** — Tupel-Kennzeichnung, Segmentangabe (mehrzeilig!), Arität/
   Bedeutung, Bezeichnung der Datenelemente, Nachrichtentyp. Anschlusspunkt an die
   MIG-Grammatik aus Prompt 4.
4. **`ExtendedAssignment`** — `EZ-xx`, Logikausdruck (Rohtext), Voraussetzungen (Rohtext).
5. **`ObjectProperty`** — `OE-xx`, Identifikator, Beschreibung, Segment. Alternativ als
   `CodeList` „PID Objekteigenschaften".
6. **Ergänzendes Feld an `ProcessIdentifier`** für die AHB-Dokumentzuordnung. Das
   vorhandene `message_type` (Default `"UTILMD"`, bei allen 91 Einträgen ungepflegt) wäre
   der naheliegende Ort — die PID belegt den Wert je PI eindeutig. **Empfehlung: nicht
   ohne separate Entscheidung überschreiben**, weil `message_type` heute faktisch ein
   Default und kein gepflegter Wert ist und ein stiller Wechsel der Semantik
   („EDIFACT-Nachrichtentyp" → „AHB-Dokument") Verwirrung stiftet.

   > **Nachtrag zur Umsetzung.** Diese Empfehlung war zu weit gefasst. Sie trennt nicht
   > zwischen dem *AHB-Dokumentbezug* (`"UTILMD AHB Strom"`, inklusive Sparte) und dem
   > darin enthaltenen *EDIFACT-Nachrichtentyp* (`UTILMD`). Nur Ersteres wäre eine
   > Umwidmung von `message_type`; Letzteres ist genau die Bedeutung des Feldes. Umgesetzt
   > wurde deshalb der Nachrichtentyp (siehe Abschnitt H); der vollständige
   > AHB-Dokumentbezug samt Sparte bleibt zurückgestellt.

---

## G. Was dieser Schritt bewusst NICHT getan hat

* keine Datenbankänderung, kein Schemaeingriff, kein Import
* kein Parser implementiert
* kein LLM zur Interpretation eingesetzt
* keine Bezeichnung aus der PID über eine bestehende gelegt
* keine Freitext-Zuordnungszelle in Codes zerlegt
* kein `ZG-T33` auf `ZO-T33` „korrigiert"
* keine der bestehenden Extraktionen (AHB, MIG-PI, OBIS, EBD, MIG-Segmentlayout) berührt

**Nächster Schritt: Freigabe mit Scoping-Entscheidung (§5).**


---

## H. Umsetzung (nach Freigabe Scoping A)

Freigegeben und umgesetzt wurde **ausschließlich Vorschlag A**: Prüfidentifikator und
Bezeichnung aus Tabelle 1 nach `ProcessIdentifier`, ohne jeden Schemaeingriff.

| | |
|---|---|
| Modul | `backend/app/regulatory_extraction_pid.py` |
| CLI | `backend/app/import_pid.py` |
| Tests | `backend/tests/test_regulatory_extraction_pid.py` (37) |
| `ProcessIdentifier` vorher/nachher | **91 → 488** |
| neu angelegt | 397 (mit Nachrichtentyp, 16 verschiedene) |
| bestehend, unverändert | 88 |
| Konflikt, nicht importiert | 1 (`55672`, zwei Schreibweisen in derselben Quelle) |

### Zusätzliche Regel der Freigabe: kein PID-Feld geht stillschweigend verloren

Der Importreport führt eine **Verlustbilanz je Spalte** — alle 21 Spalten mit ihrer
Belegung und dem Vermerk, ob sie ins Modell wandern oder für eine spätere Modellierung
vorgemerkt sind. `PidRow` hält jede Zeile vollständig im Rohwert, nicht nur die beiden
übernommenen Spalten. Die vier zurückgestellten Tabellenkonzepte werden gelesen und
gezählt, damit ihr Umfang belegt bleibt.

### Zwei Entscheidungen, die der Befund erzwungen hat

**`message_type` wird aus der AHB-Spalte gefüllt — alle 16 Formate, nicht nur UTILMD.**
Der Modell-Default wäre `"UTILMD"` und für die meisten der 397 neuen PIs falsch. Ein
erster Stand dieser Umsetzung ließ das Feld deshalb leer; auf den Hinweis, dass Atlas
*alle* Formate braucht, wurde nachgemessen — und der Befund trägt die Ableitung klar:

| | |
|---|---|
| PIs mit mehreren AHB-Werten | **0 von 486** |
| PIs mit Muster `<TYP> AHB[ Sparte]` | 484 |
| Rest (`SSQNOT zur Übermittlung von Mehr-/Mindermengen`) | 2 — führende sechs Zeichen ebenfalls der Typ |
| Widersprüche gegen die 88 bereits bekannten PIs | **0** |
| verschiedene Nachrichtentypen | **16** |

UTILMD 277 · ORDERS 46 · ORDRSP 40 · IFTSTA 35 · MSCONS 25 · PARTIN 14 · INVOIC 11 ·
INSRPT 8 · UTILTS 8 · QUOTES 5 · REQOTE 5 · REMADV 4 · PRICAT 3 · ORDCHG 3 ·
COMDIS 2 · SSQNOT 2

Die AHB-Spalte nennt das Anwendungshandbuch, dessen Name mit dem EDIFACT-Nachrichtentyp
beginnt. Die führenden sechs Großbuchstaben zu entnehmen ist strukturell, nicht
interpretiert — und es füllt das Feld mit **genau seiner Bedeutung**, statt es zum
AHB-Dokumentbezug umzuwidmen. Damit ist die Sorge aus Abschnitt F.6 gegenstandslos: dort
ging es um den Dokumentbezug samt Sparte, hier um den Nachrichtentyp allein. Die Sparte
aus „UTILMD AHB Strom" wandert nicht mit; sie gehört zum zurückgestellten
Prozessschritt-Konzept.

Bewusst **ohne Positivliste** der Typen (§16): ein in einer künftigen Version neu
hinzukommendes Format wird übernommen, ohne den Parser zu pflegen — der Importreport
führt jeden abgeleiteten Typ mit Anzahl auf, ein neuer fällt dort auf. Bestehende PIs
werden auch hier nicht überschrieben; ein Widerspruch zwischen Atlas-Bestand und PID
würde als Konflikt gemeldet (im Stand 3.3: keiner).

**Rollen bleiben leer.** „Kommunikation von/an" steht in der PID, hängt aber am
Prozessschritt: 113 bzw. 142 von 486 PIs führen mehrere verschiedene Werte. Einen davon
zu setzen hieße raten.

### Weiterhin zurückgestellt

Prozessschritt-Modell, Reaktionsbeziehung, Tupel-Übersicht, Zuordnungslogik, Erweiterte
Zuordnung, Objekteigenschaften, Übertragungsweg, API-Webservices, Änderungshistorie.
Die Modellvorschläge in Abschnitt F stehen unverändert zur Entscheidung.

**Die vier Bruchstellen der Beziehungskette wurden bewusst nicht repariert.** Fehlender
AHB-Kapitelverweis, undefiniertes `ZG-T33`, PI `44108` nur als Reaktionsziel und 42
Freitext-Zuordnungen sind regulatorische Realität, kein Extraktionsfehler. Sie stehen im
Importreport und legen nahe, dass ein künftiges Beziehungsmodell einen Status wie
*eindeutig / mehrdeutig / nicht auflösbar / nur indirekt ableitbar* führen sollte.
