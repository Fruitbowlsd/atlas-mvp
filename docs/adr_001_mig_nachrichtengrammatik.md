# ADR-001 — Datenmodell für die generische MIG-Nachrichtengrammatik

**Status:** Entwurf zur Freigabe. **Keine Implementierung, kein Schema geändert, kein Import.**
**Kontext:** Issue #52, Grundlage ist [`befund_mig_segmentlayout.md`](befund_mig_segmentlayout.md).
**Betrifft:** `MessageDefinition`, `MessageSegment`, `MessageField`, Codelisten-Verknüpfung.

---

## Leitsatz dieser Entscheidung

> **Raw Regulatory Data zuerst. Atlas-Semantik danach.**

Was die MIG als eigene Information führt, erhält in Atlas einen eigenen Platz. Abgeleitete
Bequemlichkeitsfelder (`pflicht`) bleiben erhalten, sind aber **nicht** die regulatorische
Wahrheit. Wo das Modell eine Dokumentinformation nicht trägt, wird additiv erweitert — nicht
vereinfacht.

---

## Nachtrag zum Befund: Ist `Nr` eine stabile Identität?

Diese Frage war im Befund offen und ist der einzige Punkt, für den nachgearbeitet wurde
(weiterhin rein lesend).

**Antwort: Nein. `Nr` ist eine dokumentweit eindeutige, aber ausgabengebundene Positionsnummer.**

### Beleg 1 — `Nr` ist lückenlos

148 Segmente tragen `Nr` **00003 … 00150 ohne eine einzige Lücke**. Eine stabile Identität
würde beim Entfernen eines Segments eine Lücke hinterlassen. Ein lückenloser Lauf ist das
Signum eines bei jeder Ausgabe neu vergebenen Zählers.

### Beleg 2 — die Änderungshistorie beweist die Neunummerierung

S. 168, Änderung 26043 (Status „Genehmigt"):

```
26043 | SG4 IMD++Z36 Identifikationslogik | bisher: nicht vorhanden | neu: vorhanden
```

In G1.1 wurde ein Segment **hinzugefügt**. Bei lückenloser Nummerierung verschiebt das
**jede nachfolgende `Nr`**. `Nr` ist damit nachweislich nicht versionsstabil.

### Beleg 3 — das Dokument adressiert selbst nicht über `Nr`

Die Änderungshistorie benennt Fundstellen als `SG2 MP-ID Empfänger NAD+MR DE3055` und
`SG4 IMD++Z36`, Querverweise im Fließtext lauten `SG4 DTM+Z10`, `SG8 RFF+Z18 / Z19`,
`SG5 LOC`. **`Nr` kommt als Verweisform im gesamten Dokument nicht vor** (1 Treffer, und
der ist die Legendenzeile selbst).

### Beleg 4 — es gibt trotzdem keine bessere Alternative

Alle inhaltsbasierten Schlüsselkandidaten wurden über alle 148 Segmente durchgezählt:

| Schlüsselkandidat | eindeutig |
|---|---|
| Segmentcode | 19 / 148 |
| Segmentgruppenpfad + Code | 25 / 148 |
| Pfad + Code + Qualifier (aus dem EDIFACT-Beispiel) | 114 / 148 |
| Name allein | 121 / 148 |
| Code + Name | 132 / 148 |
| Pfad + Code + Name | 134 / 148 |
| Pfad + Code + Zähler + Name | 134 / 148 |
| **`Nr`** | **148 / 148** |

Warum kein Inhaltsschlüssel reicht: die Segmentgruppe `SG8` wiederholt sich **14-mal**
(Daten der Marktlokation, der Messlokation, der Zähleinrichtung, des Mengenumwerters,
Smartmeter-Gateway …). Jede Instanz enthält dieselben `RFF`-, `CCI`- und `CAV`-Positionen
mit identischem Namen — z.B. „Referenz auf die ID einer Messlokation" 4×, „Identifikation /
Nummer des Gerätes" 5×. **Welche Instanz gemeint ist, steht in keiner Spalte.** Es ergibt
sich allein aus der Dokumentreihenfolge und dem eröffnenden `SEQ`-Segment. Das aufzulösen
wäre EDIFACT-Fachwissen, also Interpretation — nach §9/§16 unzulässig.

### Konsequenz für die Entscheidung

`Nr` wird übernommen — **als dokumentgebundener Positionsschlüssel, nicht als
versionsübergreifende Identität.** Gültigkeitsbereich: eine `MessageDefinition`,
also `(regulatory_version_id, quelle_hash)`.

Die versionsübergreifende Zuordnung („ist dieses Segment in G1.2 dasselbe wie in G1.1?")
ist damit **ausdrücklich nicht** gelöst und wird auch nicht vorweggenommen. Sie gehört in
die Delta-Engine, die dafür den vollständigen Inhaltstupel (Pfad, Code, Zähler, Name,
Qualifier, Reihenfolge) zur Verfügung hat — genau deshalb werden diese Merkmale alle
gespeichert. Ein künstlicher, jetzt erfundener Stabilschlüssel würde eine Stabilität
behaupten, die das Dokument nicht hergibt.

---

## Entscheidung 1 — Generische Definition (Frage A)

**Beschluss:** Generische MIG-Definitionen entstehen als eigene `MessageDefinition`-Zeilen
mit `pi_id = NULL` **und** `pi_nummer = NULL`. Es wird **kein** Ersatzwert erfunden.

Identität einer generischen Definition:

```
RegulatoryVersion + Nachrichtentyp + Sparte + Version   (+ Herkunft = MIG)
```

**Umsetzung der Eindeutigkeit — Partial Unique Index, gegen die echte Datenbank verifiziert:**

```sql
CREATE UNIQUE INDEX uq_message_definition_generisch
  ON message_definitions (regulatory_version_id, nachrichtentyp, sparte, version)
  WHERE pi_nummer IS NULL;
```

Testergebnis auf einer Kopie von `atlas.db` (SQLite 3.51):

| Fall | Ergebnis |
|---|---|
| erste generische Zeile (UTILMD/gas/G1.1) | angelegt |
| zweite identische generische Zeile | **abgewiesen** — `UNIQUE constraint failed` |
| parallele Strom-MIG (UTILMD/strom/S2.2) | angelegt |
| die 88 bestehenden AHB-Zeilen | **unberührt** (`WHERE pi_nummer IS NULL` schließt sie aus) |

Damit ist die im Befund gezeigte NULL-Lücke geschlossen, **ohne** den bestehenden Index
anzufassen und **ohne** ein Provenienzfeld mit einem erfundenen Wert zu verfälschen.
Die Klausel funktioniert in SQLite (≥ 3.8) und PostgreSQL identisch.

**Zusätzlich, additiv:** `MessageDefinition.grammatik_quelle` (`VARCHAR`, nullable) mit dem
Wert `"MIG"` für generische Zeilen. Bestandszeilen bleiben `NULL`; die AHB-Extraktion wird
dafür **nicht** angefasst (§21). Das Feld macht die Herkunft lesbar, ohne dass ein Leser
`pi_nummer IS NULL` interpretieren muss.

**Idempotenz:** im Importer, nach dem bewährten Muster von
`regulatory_extraction._delete_previous_import()` — Vorbestand zu
`(regulatory_version_id, quelle_hash)` löschen, neu schreiben. Da MIG- und AHB-Datei
verschiedene Hashes haben, kann ein MIG-Lauf AHB-Zeilen weder sehen noch löschen.

---

## Entscheidung 2 — Status, Format, MaxWdh (Frage B)

**Beschluss:** `pflicht: Boolean` ist **nicht** die regulatorische Wahrheit. Beide Sichten
werden unverändert als Rohwerte gespeichert. `pflicht` bleibt als abgeleitete
Kompatibilitätsspalte erhalten, damit bestehende Leser nicht brechen.

### `MessageField` — additiv, nullable

| Feld | Typ | Inhalt | Beispiel |
|---|---|---|---|
| `status_standard_raw` | VARCHAR | Status-Spalte „Standard", unverändert | `M`, `C` |
| `status_bdew_raw` | VARCHAR | Status-Spalte „BDEW", unverändert | `M`, `R`, `D`, `N` |
| `format_standard_raw` | VARCHAR | Format-Spalte „Standard", unverändert | `an..70` |
| `format_bdew_raw` | VARCHAR | Format-Spalte „BDEW", unverändert | `n5` |
| `anwendung_raw` | TEXT | zusammengeführte Zelle „Anwendung / Bemerkung" | 144 Zeilen bei DE1154 |

**Bewusst als `_raw` und als String**, nicht zerlegt in `datentyp`/`laenge`: die Zerlegung
verlöre die Unterscheidung fest/variabel (`n5` = genau 5 vs. `n..6` = bis zu 6). Alle 17 im
Dokument vorkommenden Formate bleiben so wörtlich erhalten. `datentyp`/`laenge` bleiben
unberührt und werden von der MIG-Extraktion **nicht** befüllt — eine Ableitung wäre
Interpretation.

### `MessageSegment` — additiv, nullable

| Feld | Typ | Inhalt | Beispiel |
|---|---|---|---|
| `status_standard_raw` | VARCHAR | Segmentstatus „Standard" | `M`, `C` |
| `status_bdew_raw` | VARCHAR | Segmentstatus „BDEW" | `M`, `R`, `D` |
| `max_wdh_standard` | VARCHAR | maximale Wiederholung „Standard" | `9`, `99999` |
| `max_wdh_bdew` | VARCHAR | maximale Wiederholung „BDEW" | `1`, `5` |

`kardinalitaet` und `wiederholbar` bleiben unberührt und werden von der MIG-Extraktion
nicht befüllt (ein Feld für zwei Angaben).

### Abgeleitete Belegung von `pflicht`

Festgelegte, dokumentierte Konvention — **eine Atlas-Konvention, keine Dokumentaussage**:

| `status_bdew_raw` | `pflicht` | Begründung |
|---|---|---|
| `M` | `true` | Muss |
| `R` | `true` | Erforderlich |
| `D` | `false` | bedingt — **nicht** als Pflicht lesbar |
| `N` | `false` | nicht benutzt — **nicht** als „optional" lesbar |
| `O` | `false` | optional (in G1.1 nicht vorkommend) |

`D` und `N` fallen in `pflicht` zusammen, obwohl sie fachlich gegensätzlich sind (bedingt
erlaubt vs. verboten). **Genau deshalb ist `pflicht` nicht die Wahrheit** — die
Unterscheidung steht ausschließlich in `status_bdew_raw`. Jeder spätere Validator MUSS
`status_bdew_raw` lesen, nicht `pflicht`.

Die Vollständigkeit der Werteliste wird geprüft, nicht angenommen: trifft der Extraktor
einen Statuswert außerhalb von `{M, C, R, D, N, O}`, wird die Zeile nicht importiert,
sondern im Report ausgewiesen (§14).

---

## Entscheidung 3 — Segmentposition und Segmentgruppenpfad

**Beschluss:** Die Positionsmerkmale werden **vollständig und roh** übernommen. Es wird
**keine** künstliche Identität konstruiert.

### `MessageSegment` — additiv, nullable

| Feld | Typ | Inhalt | Beispiel |
|---|---|---|---|
| `mig_nr` | VARCHAR | Spalte `Nr`, dokumentgebundener Positionsschlüssel | `00038` |
| `mig_zaehler` | VARCHAR | Spalte `Zähler`, Position im UN/CEFACT-Standard | `0360` |
| `segmentgruppen_pfad` | VARCHAR | vollständiger Pfad, `/`-getrennt | `SG4/SG6` |
| `ebene` | INTEGER | Spalte `Ebene` | `2` |

* `position` (Integer, bestehend) hält die Dokumentreihenfolge 1…148. Da `Nr` streng
  aufsteigend ist, sind beide Reihenfolgen identisch.
* `segmentgruppe` (bestehend) erhält das **innerste** Element des Pfads (`SG6`) — damit
  bleibt das Feld für bestehende Leser sinnvoll belegt, ohne dass der Pfad verlorengeht.
* `ahb_zeile` bleibt **leer**. Es ist laut Modellkommentar die AHB-Zeilennummer und wäre
  mit `Nr` verwechselbar.

**Ausdrücklich nicht Teil dieser Entscheidung:** die Auflösung von Gruppeninstanzen
(welche der 14 `SG8`-Wiederholungen gemeint ist). Das Dokument kodiert sie nicht; sie
ergibt sich nur aus der Reihenfolge. Die Reihenfolge wird gespeichert — die Interpretation
nicht vorweggenommen.

---

## Entscheidung 4 — Detailtabellen und Nachrichtenstruktur

**Beschluss:** Extraktion **aus den Detailtabellen** (S. 11–167). Diese enthalten
nachweislich alles: Zähler, Nr, Segmentgruppenpfad, Status und MaxWdh beider Sichten,
Ebene, Name, Datenelemente.

Die Nachrichtenstruktur-Übersicht (S. 3–8) wird **ebenfalls geparst, aber als Gegenprobe**,
nicht als zweite Datenquelle. Prüfung bei jedem Lauf:

* 148 `Nr` müssen beidseitig übereinstimmen
* `Zähler`, `Bez`, Status(Std), Status(BDEW), MaxWdh(Std), MaxWdh(BDEW), `Ebene` müssen gleich sein
* der rekonstruierte Segmentgruppenpfad muss gleich sein
* die Reihenfolge muss gleich sein

Abweichungen → **Formfehler**, Ausweis im Report, kein stiller Import (§6/§14). Das ist
eine echte Absicherung: der Befund hat für G1.1 **0 Abweichungen** gemessen, jede künftige
Abweichung ist damit ein belastbares Signal.

**Verknüpfung über `Nr`, nicht über `Bez`** — `Bez` ist mit 19 Werten für 148 Segmente
mehrdeutig.

Kein eigenes Modell für die Übersicht. Wo sie abweichende Namen liefert (6 Fälle, dort
umbruchbedingt gekürzt), gilt die Detailtabelle.

---

## Entscheidung 5 — Codelisten: n:m

**Beschluss:** Die 1:1-Annahme `MessageField.codelist_id` ist fachlich falsch — ein
einzelnes Feld (`STS` DE1131) referenziert **50 Codelisten**. Es wird eine
Zwischentabelle eingeführt.

```
MessageField ──< message_field_code_lists >── CodeList
```

| Spalte | Typ | Inhalt |
|---|---|---|
| `message_field_id` | FK → `message_fields.id` | |
| `codelist_id` | FK → `code_lists.id` | nur bei auflösbarer Referenz |
| `referenz_raw` | VARCHAR | Rohtext, z.B. `G_0002 Codeliste Gas Nr. G_0002` |
| `referenz_id` | VARCHAR | extrahierte ID, z.B. `G_0002` |

* **Auflösbare Referenzen** (45 von 50) erhalten `codelist_id`.
* **Nicht auflösbare** (`G_0018`, `G_0032`, `G_0033`, `G_0042`, `G_0045`) werden als Zeile
  mit `codelist_id = NULL` angelegt und im Report ausgewiesen. Die Referenz geht nicht
  verloren und wird auflösbar, sobald die betreffende Codeliste importiert ist — ohne den
  Parser anzufassen.
* Auflösungsregel, deterministisch: Präfix der Referenz (`G_0002`) gegen
  `CodeList.name LIKE 'G_0002_%'` derselben `RegulatoryVersion`. Trifft die Regel mehr als
  eine Codeliste, wird **nicht geraten**, sondern `codelist_id = NULL` gesetzt und der Fall
  gemeldet.

`MessageField.codelist_id` bleibt bestehen und unberührt (bestehende Leser), wird von der
MIG-Extraktion aber **nicht** befüllt — bei 50 Referenzen wäre jede Auswahl geraten.

Dies ist eine Relationstabelle, kein paralleles Modell zu `MessageField`/`CodeList` (§10).

---

## Entscheidung 6 — Bemerkung und Beispiel

**Beschluss:** Beides wird als eigenständige Information erhalten. 131 von 148 Segmenten
tragen eine Bemerkung, **148 von 148** ein EDIFACT-Beispiel — das sind keine Randnotizen.

### `MessageSegment` — additiv, nullable

| Feld | Typ | Inhalt | Beispiel |
|---|---|---|---|
| `anwendungshinweis` | TEXT | Block `Bemerkung:`, Zeilen zusammengeführt | „Dieses Segment wird zur Angabe des Dokumentendatums verwendet." |
| `beispiel_edifact` | TEXT | Block `Beispiel:`, unverändert inkl. Escapes | `DTM+137:199904081315?+00:303'` |

Bewusst **nicht** in `bedingung` (AHB-Fußnotensemantik) und **nicht** in
`MessageField.beispielwert` (Feld- statt Segmentattribut) gepresst. Das EDIFACT-Beispiel
ist für einen späteren Generator die unmittelbarste Referenz und wird wörtlich erhalten —
einschließlich der Release-Zeichen (`?+`).

---

## Zusammenfassung: Schemaänderungen dieser Entscheidung

Alle Änderungen sind **additiv und nullable**, nach dem Muster der bestehenden
AHB-Erweiterung in `migrations.py`. Kein bestehendes Feld ändert Typ oder Bedeutung.

| Tabelle | neue Felder |
|---|---|
| `MessageDefinition` | `grammatik_quelle` |
| `MessageSegment` | `mig_nr`, `mig_zaehler`, `segmentgruppen_pfad`, `ebene`, `status_standard_raw`, `status_bdew_raw`, `max_wdh_standard`, `max_wdh_bdew`, `anwendungshinweis`, `beispiel_edifact` |
| `MessageField` | `status_standard_raw`, `status_bdew_raw`, `format_standard_raw`, `format_bdew_raw`, `anwendung_raw` |
| **neu** | Tabelle `message_field_code_lists` |
| **neu** | Partial Unique Index `uq_message_definition_generisch` |

**Unberührt:** `pflicht`, `pflichtigkeit`, `kardinalitaet`, `wiederholbar`, `datentyp`,
`laenge`, `codelist_id`, `bedingung*`, `ahb_zeile`, der bestehende Unique-Index, sowie
sämtlicher Code der AHB-, MIG-PI-, OBIS- und EBD-Extraktion.

---

## Offene Punkte für die Freigabe

1. **Feldnamen** — `*_raw`-Suffix für die Rohwerte: bewusst gewählt, um „Raw Regulatory
   Data zuerst" im Schema sichtbar zu machen. Falls eine andere Namenskonvention gewünscht
   ist, jetzt festlegen.
2. **`grammatik_quelle`** — ob Bestandszeilen der AHB nachträglich auf `"AHB"` gesetzt
   werden sollen. Vorschlag: **nein** (§21, keine unnötige Änderung am Bestand); `NULL`
   bedeutet „nicht aus der MIG".
3. **`message_field_code_lists`** — Bestätigung, dass eine Relationstabelle als Erweiterung
   des bestehenden Modells gilt und nicht als paralleles Modell nach §10.
4. **`ebene` als INTEGER** — im Dokument `0`…`4`. Falls die Rohwert-Doktrin auch hier
   strikt gelten soll, wäre `VARCHAR` konsequenter.

Nach Bestätigung dieser vier Punkte ist die Entscheidung implementierungsreif. Reihenfolge
dann: Schema-Erweiterung → Formprüfung → Extraktor → Regressions- und Idempotenztest →
echter Import → Ergebnisreport.
