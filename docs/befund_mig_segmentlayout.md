# Technischer Befund — MIG Gas Segmentlayout (Issue #52)

**Status: STOP-Punkt nach §6 des Auftrags.** Es wurde nichts implementiert, kein Schema
geändert, nichts importiert. Dieser Befund ist Grundlage für die Architekturentscheidung
zu Frage A und Frage B; erst nach expliziter Freigabe folgt Code.

Alle Zahlen stammen aus einem rein lesenden Durchlauf über **alle 168 Seiten** des
Dokuments, nicht aus einer Stichprobe. Kein LLM beteiligt.

---

## A. Dokument

| | |
|---|---|
| Datei | `backend/data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf` |
| SHA-256 | `f5191a473b650dd6e5de2a673f97b6db685f57de8f6b8d2da7d6ccebb2bfe634` |
| Abgleich mit Prompt 1 | **identisch** — entspricht `_SHA256` in `backend/tests/test_regulatory_extraction_mig.py:54` |
| Version laut Dokument | UTILMD G1.1, Publikationsdatum 01.10.2025, UN D.11A S3 |
| Ziel-`RegulatoryVersion` | `[1] GeLi Gas 2.0 / UTILMD Gas G1.1 (gültig ab 01.04.2026)` (`is_active = 1`) |

Es liegt **dieselbe Datei** wie in Prompt 1 vor. Kein Versions-Fallback nötig.

---

## B. Dokumentaufbau

| Abschnitt | Seiten |
|---|---|
| Titel / Disclaimer | 1–2 |
| **Nachrichtenstruktur** (Übersichtstabelle) | 3–8 |
| Diagramm | 9–10 |
| **Segmentlayout** (Detailtabellen) | 11–167 |
| Änderungshistorie | 168 |

### Zwei Tabellenarten, zwei Extraktionswege

**Die Nachrichtenstruktur-Übersicht ist für `pdfplumber` keine Tabelle.** `extract_tables()`
liefert dort 2-spaltige Zeilen, in denen die komplette Textzeile in einer Zelle steht
(`'0010 00003 UNH M M 1 1 0 Nachrichten-Kopfsegment'`). Sie muss als Text zeilenweise
geparst werden. Die Segmentlayout-Detailtabellen sind dagegen echte Tabellen mit
Zellstruktur. Das ist relevant für die Modulstruktur, nicht für die Fachlichkeit.

---

## C. Strukturbefund Segmentlayout (§5.1, §5.2, §5.5)

### §5.1 — Anzahl Segmente

**148 Segmente** auf 157 Seiten. Kein Segment ohne Detailtabelle, keine Detailtabelle
ohne Segment.

Verteilung der Segmentcodes (19 verschiedene):

```
CCI 28   CAV 28   DTM 21   RFF 18   NAD 14   SEQ 14   STS  5   QTY  4
FTX  3   PIA  3   LOC  2   UNH  1   BGM  1   CTA  1   COM  1   IDE  1
IMD  1   AGR  1   UNT  1
```

**755 Datenelemente** insgesamt in den Detailtabellen.

### §5.2 — Konsistenz der Tabellenform

Der Aufbau je Segment ist über alle 148 Segmente **identisch**:

```
Zähler Nr Bez St MaxWdh St MaxWdh Ebene Name     <- Kopf des Segmentkopfblocks
0180        SG4  C 99999 R 99999 1  Vorgangs-Identifikation      <- 0..n Segmentgruppenzeilen
0350        SG6  C 99    D 1     2  Referenz Vorgangsnummer …
0360 00039  RFF  M 1     M 1     2  Referenz Vorgangsnummer …    <- die Segmentzeile
Standard | BDEW                                  <- Bannerzeile
Bez | Name | St | Format | St | Format | Anwendung / Bemerkung   <- Detailkopfzeile
RFF                                              <- Segmentcodezeile
C506 | Referenz            | M | …               <- Datenelemente
1153 | Referenz, Qualifier | M | an..3 | M | an..3 | TN Transaktions-Referenznummer
1154 | Referenz, Ident.    | C | an..70| R | an..70| Vorgangsnummer
Bemerkung:                                       <- Freitext
Beispiel:                                        <- EDIFACT-Beispiel
```

Die **Spaltenzahl** schwankt (Layoutartefakt, wie schon in Prompt 1 beobachtet), die
**Spaltenrollen nicht**:

| Spalten | Bez | Name | St(Std) | Format(Std) | St(BDEW) | Format(BDEW) | Anwendung | Vorkommen |
|---|---|---|---|---|---|---|---|---|
| 10 | 0 | 1 | 4 | 5 | 6 | 7 | 8 | 147 Seiten |
| 7 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 6 Seiten (13, 38, 39, 42, 52, 53) |
| 11 | 0 | 1 | 4 | 5 | 6 | 7 | 8 | 1 Seite (32) |

Der Spaltenindex ist **je Tabelle aus der Kopfzeile zu bestimmen** — exakt das Verfahren,
das `regulatory_extraction_mig.header_column_index()` seit Prompt 1 anwendet. Damit ist
die Form dokumentweit konsistent.

Der Segmentkopfblock ist in **allen 148 Fällen** gleich geformt: Statuszelle passt
ausnahmslos auf `St MaxWdh St MaxWdh Ebene`.

**Ergebnis eines vollständigen Testparsers: 0 nicht klassifizierbare Zeilen** im gesamten
Bereich S.11–167. Es gibt keine abweichende Segmentform, die zu `SKIP` führen müsste.

9 Seiten sind reine Fortsetzungsseiten ohne eigenen Segmentkopf
(13, 33, 38, 39, 42, 52, 53, 65, 148).

### §5.5 — Mehrzeilige Zellen

Mehrzeiligkeit ist **nicht die Ausnahme, sondern die Regel** — und betrifft drei Spalten:

| Spalte | Befund |
|---|---|
| `Anwendung / Bemerkung` | 362 einzeilig, 91 mehrzeilig, davon Maxima **144 / 116 / 58 / 50** Zeilen |
| `Name` (Datenelement) | 600 einzeilig, 134 zweizeilig, 21 dreizeilig |
| `Name` (Segmentkopf) | 6 Segmente über zwei Zeilen umbrochen |

Die **Zusammenführungslogik aus Prompt 1 trägt unverändert**: pdfplumber zieht je
Textzeile eine eigene Tabellenzeile; eine Zeile ohne `Bez` ist Fortsetzung der
vorangegangenen. Verifiziert an der größten Zelle des Dokuments (S.51 `RFF` Nr 00038
DE1154, 144 Zeilen) — siehe §G.

Anpassungsbedarf: Die Fortsetzung muss **spaltenweise** erfolgen (`Name` und `Anwendung`
können unabhängig voneinander umbrechen), nicht wie in Prompt 1 nur für eine Zielspalte.

---

## D. §5.6 — Segmentidentität (Architekturbefund)

**Frage: Reicht der Segmentcode als Identität?**

**Nein — eindeutig widerlegt.** Gezielte Suche nach gleichen Segmentcodes in
unterschiedlichen Segmentgruppen:

```
DTM: (root), SG4, SG4/SG6
NAD: SG2, SG4/SG12
RFF: SG1, SG4/SG6, SG4/SG8, SG4/SG12
```

**Aber auch Segmentcode + Segmentgruppenpfad reicht nicht.** Dieselbe Kombination tritt
bis zu 28-mal auf:

| Segmentcode + Pfad | Vorkommen |
|---|---|
| `CCI` in `SG4/SG8/SG10` | **28×** |
| `CAV` in `SG4/SG8/SG10` | **28×** |
| `SEQ` in `SG4/SG8` | 14× |
| `DTM` in `SG4` | 13× |
| `NAD` in `SG4/SG12` | 12× |
| `RFF` in `SG4/SG8` | 8× |
| … 16 mehrfach belegte Kombinationen insgesamt | |

Diese 28 `CCI`-Vorkommen sind fachlich **verschiedene grammatische Positionen**
(Marktgebiet, Bilanzkreis, Gasqualität, Prognosegrundlage …), nicht Wiederholungen
desselben Segments.

**Was eindeutig ist:** die Spalte `Nr` ("Laufende Segmentnummer im Guide"), z.B. `00038`.

* 148 Segmente, **148 verschiedene `Nr`** — dokumentweit eindeutig, keine Dublette.
* `Nr` ist im Segmentlayout **streng aufsteigend** und entspricht der Nachrichtenreihenfolge.

**Vorhandene Felder auf `MessageSegment`:** `segment_code`, `position` (Integer),
`segmentgruppe` (String, z.B. `"SG4"`), `ahb_zeile` (String), `kardinalitaet`,
`wiederholbar`. Es gibt **keinen Parent-/Group-Bezug** und **keinen Pfad** — `segmentgruppe`
hält genau eine Gruppe, nicht `SG4/SG8/SG10`. Ein Feld für die dokumenteigene Segmentnummer
(`Nr`) existiert ebenfalls nicht; `ahb_zeile` ist laut Modellkommentar die AHB-Zeilennummer
und damit fachlich etwas anderes.

> **Modelllücke 1:** Weder der Segmentgruppen-**Pfad** (`SG4/SG8/SG10`) noch die
> dokumenteigene Segmentnummer (`Nr`) haben im heutigen `MessageSegment` einen Platz.
> Ohne beides ist die grammatische Position eines Segments nicht rekonstruierbar und
> ein späterer Validator/Generator kann 28 verschiedene `CCI`-Positionen nicht
> auseinanderhalten. **Kein Feld wurde angelegt** — Entscheidung bei der Freigabe.

---

## E. §5.7 — Detailtabellen vs. Nachrichtenstruktur-Übersicht

Dies ist der überraschendste Befund: **Der Segmentkopfblock jeder Detailtabelle enthält
die Übersichtsinformation vollständig mit** — inklusive der umschließenden
Segmentgruppenzeilen (siehe Beispiel in §C).

Empirischer Abgleich beider Tabellenarten über das gesamte Dokument:

| Prüfung | Ergebnis |
|---|---|
| Segmente in der Übersicht | 148 |
| Segmente im Segmentlayout | 148 |
| `Nr` aus Segmentlayout in Übersicht auffindbar | **148 / 148** |
| Abweichungen in `Zähler`, `Bez`, Status(Std), Status(BDEW), MaxWdh(Std), MaxWdh(BDEW), `Ebene` | **0** |
| Segmentgruppenpfad aus Detailtabellen vs. aus Übersicht rekonstruiert | **0 Abweichungen** |
| Reihenfolge Segmentlayout == Reihenfolge Übersicht | **ja** |
| Distinkte SG-Kontexte Übersicht / Detailtabellen | 10 / 10, mengengleich |

**Antworten auf die drei Fragen aus §5.7:**

1. **Kann die generische Nachrichtengrammatik vollständig aus den Detailtabellen
   rekonstruiert werden?** — **Ja.** Reihenfolge (`Nr` aufsteigend), Verschachtelungsebene
   (`Ebene`), Wiederholbarkeit (`MaxWdh` Standard und BDEW), Status beider Spalten und der
   vollständige Segmentgruppenpfad stehen alle im Segmentkopfblock der Detailtabellen.

2. **Was liefert die Übersicht zusätzlich?** — Fachlich **nichts**. Sie ist vollständig
   redundant. In 6 Fällen ist ihr `Inhalt` sogar *kürzer* (umbruchbedingt abgeschnitten)
   als der Name in der Detailtabelle, z.B. Nr 00028: Übersicht
   `"Transaktionsgrundergänzung für Lieferende bei"` vs. Detailtabelle (nach
   Zusammenführung) `"Transaktionsgrundergänzung für Lieferende bei befristeter Anmeldung"`.

3. **Deterministische, dokumentweit stabile Verknüpfbarkeit?** — **Ja, über `Nr`**:
   148/148, eindeutig, keine mehrdeutige Stelle. `Bez` (Segmentcode) taugt dafür wegen
   der Mehrfachvorkommen aus §D **nicht**.

**Vorschlag (nicht umgesetzt):** Extraktion **allein aus den Detailtabellen**, die
Übersicht als **unabhängige Gegenprobe** verwenden (148 `Nr` müssen matchen, Status/MaxWdh/
Ebene/Pfad müssen übereinstimmen) und Abweichungen als Formfehler melden. Das nutzt beide
Tabellen, ohne das Datenmodell für die Übersicht zu erweitern.

---

## F. Frage A — pi_id-Konvention (§4)

### Befund 1: Ist `pi_id = NULL` mit dem AHB-Code verträglich?

**Ja, was den Schreibpfad angeht.** Geprüft wurde der gesamte Bestand:

* `regulatory_extraction.py:1183` setzt `pi_id=pi_catalog.get(pi)` und **schreibt dort
  bereits heute `NULL`**, wenn ein PI nicht im kuratierten Katalog steht (Zeile 1176 ff.
  gibt dazu eine Warnung aus). `pi_id = NULL` ist im Bestand also ein etablierter Zustand,
  kein Novum.
* `_existing_import()` und `_delete_previous_import()` (`regulatory_extraction.py:957–996`)
  filtern **ausschließlich** auf `(regulatory_version_id, quelle_hash)`. Da MIG und AHB
  verschiedene Dateien mit verschiedenen Hashes sind, kann ein MIG-Import die
  AHB-Zeilen weder sehen noch löschen. **Kein Konflikt.**
* Konsumenten: außerhalb von `models.py`, `regulatory_extraction.py` und `migrations.py`
  greift **kein** Modul auf `MessageDefinition`/`MessageSegment`/`MessageField` zu — weder
  API-Router, noch `services.py`, `diff.py`, `ai_analysis.py`, `matching.py`, noch das
  Frontend. Es gibt also **keine bestehende Annahme "jede MessageDefinition hat einen PI"**,
  die verletzt würde.

### Befund 2: Ist eine generische Definition eindeutig identifizierbar? — **Nein.**

Der Constraint lautet (`models.py:374–379`, dupliziert als Index in `migrations.py:195`):

```sql
UNIQUE (regulatory_version_id, nachrichtentyp, pi_nummer, quelle_kapitel)
```

Zwei Probleme, beide empirisch belegt:

**(a) NULL hebt den Constraint auf.** Ein generischer Datensatz hat `pi_nummer = NULL` und
— da die MIG keine Kapitelnummerierung hat (Befund aus Prompt 1) — auch
`quelle_kapitel = NULL`. In SQL sind NULLs untereinander nicht gleich, der Constraint
greift also nie. Gegen die echte `atlas.db` (Kopie) getestet:

```sql
INSERT … VALUES (1,'UTILMD','D:11A:UN:G1.1','gas',NULL,NULL,'hashA');
INSERT … VALUES (1,'UTILMD','D:11A:UN:G1.1','gas',NULL,NULL,'hashA');  -- identisch
-- Ergebnis: Zeilen mit pi_nummer IS NULL: 2   (kein Fehler)
```

Beide Zeilen wurden akzeptiert. Das gilt für SQLite **und** PostgreSQL gleichermaßen
(Letzteres kennt zwar `NULLS NOT DISTINCT`, der Index verwendet es nicht). Ein zweiter
Importlauf würde also **stillschweigend duplizieren** — die Idempotenzforderung aus §19
wäre allein durch den Constraint nicht erfüllt.

**(b) `sparte` ist nicht Teil des Schlüssels.** Selbst mit befülltem `pi_nummer` könnte der
Constraint "UTILMD Gas MIG G1.1" und "UTILMD Strom MIG S2.2" nicht trennen. Zur
Befüllung: `sparte` ist im Bestand zuverlässig gesetzt (88/88 = `'gas'`, 0 NULL) und hat
den Modell-Default `'gas'` — als Schlüsselbestandteil wäre es also brauchbar, ist aber
heute nicht drin.

> **Modelllücke 2:** `pi_id = NULL` bzw. `pi_nummer = NULL` bietet **keinerlei**
> Eindeutigkeitsschutz. Die vom Auftrag als Vorschlag genannte Konvention ist fachlich
> richtig (sie trennt generisch von PI-spezifisch sauber und ist am Bestand ablesbar),
> löst aber die Identitätsfrage nicht.

### Vorschläge zu Frage A (Entscheidung liegt beim Auftraggeber)

| Option | Inhalt | Bewertung |
|---|---|---|
| **A1** | `pi_nummer`/`pi_id` bleiben NULL; Idempotenz **im Importer** über `(regulatory_version_id, quelle_hash)` sichern — genau wie `_delete_previous_import()` es für die AHB tut | Keine Schemaänderung. Schützt gegen Doppelimport derselben Datei; ein *inhaltlich* doppelter Datensatz aus einer anderen Datei bliebe möglich. |
| **A2** | zusätzlich `sparte` in den Unique-Index aufnehmen | Löst (b), nicht (a). Erfordert Index-Neubau. |
| **A3** | statt NULL einen expliziten Marker in `pi_nummer` schreiben (z.B. `"(generisch)"`) | Löst (a) und macht den Constraint wirksam — **verfälscht aber ein Provenienzfeld mit einem erfundenen Wert** und widerspricht §9. Nicht empfohlen. |
| **A4** | additives nullable Feld `MessageDefinition.grammatik_quelle` (`"MIG"`/`"AHB"`) + Index darauf | Sauberste Trennung, additiv, analog zum bisherigen Vorgehen. Schemaänderung nötig. |

**Empfehlung: A1 als Minimum** (deckt die reale Idempotenzanforderung), **A4 falls die
Unterscheidbarkeit auch auf Datenbankebene erzwungen werden soll**.

---

## G. Frage B — Standard- vs. BDEW-Status (§4)

### Vollständige Enumeration (nicht Stichprobe): alle 755 Datenelemente

**Statuswerte Spalte "Standard":**

| Wert | Vorkommen | Bedeutung laut Legende des Dokuments (auf jeder Seite) |
|---|---|---|
| `M` | 249 | „EDIFACT: M=Muss/Mandatory" |
| `C` | 506 | „EDIFACT: C=Conditional" |

**Statuswerte Spalte "BDEW":**

| Wert | Vorkommen | Bedeutung laut Legende |
|---|---|---|
| `M` | 219 | Muss/Mandatory |
| `R` | 250 | „Anwendung: R=Erforderlich/Required" |
| `D` | **97** | „D=Abhängig von/Dependent" |
| `N` | **189** | „N=Nicht benutzt/Not used" |

Die Legende definiert zusätzlich `O=Optional`; **`O` kommt im Dokument G1.1 nirgends vor**
(0 Treffer). Umgekehrt kommt `M` in der BDEW-Spalte vor, obwohl die Legende `M` nur unter
EDIFACT führt. Beides ist für einen wiederverwendbaren Extraktor relevant: `O` muss
verarbeitbar sein, auch wenn es hier fehlt.

**Alle auftretenden Kombinationen (vollständig, 6 von theoretisch 8):**

| Standard | BDEW | Vorkommen | Fachliche Lesart |
|---|---|---|---|
| `C` | `R` | 247 | EDIFACT optional, BDEW macht es verpflichtend |
| `M` | `M` | 219 | beidseitig Pflicht |
| `C` | `N` | 162 | EDIFACT optional, BDEW verbietet die Nutzung |
| `C` | `D` | **97** | EDIFACT optional, BDEW: **bedingt** |
| `M` | `N` | **27** | **EDIFACT-Pflichtfeld, das BDEW nicht benutzt** |
| `M` | `R` | 3 | beidseitig verpflichtend, andere Begründung |

Zusätzlich auf Segment- und Segmentgruppenebene (dieselben zwei Spalten im Kopfblock):

* Segmente (148): Standard `M` 76 / `C` 72 — BDEW `M` 75 / `D` **52** / `R` 21
* Segmentgruppen (10): Standard `C` 10 — BDEW `D` 8 / `R` 2

### Echte Beispiele

| Seite | Segment | DE | Bezeichnung | Std | BDEW | Format Std → BDEW | Anwendung |
|---|---|---|---|---|---|---|---|
| 11 | UNH Nr 00003 | 0073 | Erste und letzte Übermittlung | `C` | `D` | `a1` → `a1` | „C Beginn / F Ende" |
| 17 | NAD Nr 00008 | 1131 | Codeliste, Code | `C` | `N` | `an..17` → *(leer)* | „Nicht benutzt" |
| 37 | STS Nr 00027 | 4405 | Status, Code | `M` | `N` | `an..3` → *(leer)* | „Nicht benutzt" |
| 40 | STS Nr 00028 | 4405 | Status, Code | `M` | `N` | `an..3` → *(leer)* | „Nicht benutzt" |
| 72 | CCI Nr 00056 | 7037 | Merkmal, Code | `M` | `R` | `an..17` → `an..17` | „Marktgebiet" |
| 13 | BGM Nr 00004 | 1004 | Dokumentennummer | `C` | `R` | `an..70` → **`an..35`** | „EDI-Nachrichtennummer …" |

### Lässt sich das verlustfrei auf ein `pflicht: Boolean` abbilden? — **Nein.**

Drei unabhängige Gründe:

1. **`D` ist ein echter dritter Zustand.** „Abhängig von/Dependent" heißt: die Pflichtigkeit
   hängt von einer anderen Bedingung ab. Weder `true` noch `false` gibt das wieder. Betrifft
   **97 Datenelemente, 52 Segmente und 8 von 10 Segmentgruppen**.
2. **`N` ist kein „nicht Pflicht", sondern ein Verbot.** „Nicht benutzt" schließt das Feld
   aus. Auf `pflicht = false` abgebildet wäre es von einem erlaubten optionalen Feld
   ununterscheidbar — für einen Validator ist das der Unterschied zwischen „darf fehlen"
   und „darf nicht vorkommen". Betrifft **189 Datenelemente**.
3. **Es sind zwei Spalten, nicht eine.** In **536 von 755 Fällen (71,0 %)** trägt die
   BDEW-Spalte einen anderen Wert als die Standard-Spalte. Die 27 Fälle `M`/`N` sind der
   schärfste Beleg: der EDIFACT-Standard fordert das Feld, BDEW verbietet es. Welcher Wert
   auch immer in ein einziges `pflicht` geschrieben würde — die jeweils andere Aussage
   ginge verloren.

Zum Vergleich: `MessageSegment` hat für die AHB-Extraktion bereits `pflichtigkeit: String`
neben `pflicht: Boolean` bekommen, **genau weil Muss/Soll/Kann nicht in ein Boolean passt**
(Modellkommentar `models.py:429–433`). `MessageField` hat `pflichtigkeit` ebenfalls, dort
aber mit AHB-Semantik („X wenn im PI genutzt").

### Weitere Zwei-Spalten-Befunde derselben Art

Das Standard/BDEW-Paar betrifft **nicht nur den Status**:

| Merkmal | Abweichung Standard vs. BDEW |
|---|---|
| **Format** (Datenelement) | **173 von 755** (22,9 %) weichen ab, z.B. `an..70` → `an..35` (S.13 BGM DE1004), `an..256` → `an..35` (S.18 CTA DE3412) |
| **MaxWdh** (Segment) | **69 von 148** (46,6 %) weichen ab, z.B. DTM Nr 00005 `9` → `1`, COM Nr 00010 `9` → `5` |

`MessageField` hat für das Format `datentyp: String` + `laenge: Integer` — **ein** Paar für
**zwei** Formatangaben. Zusätzlich geht in dieser Zerlegung die Unterscheidung
variabel/fest verloren: alle 17 vorkommenden Formate sind
`a1, an..14, an..17, an..2, an..256, an..3, an..35, an..512, an..6, an..70, an..8, an..9,
n..13, n..2, n..35, n..6, n5` — `n5` (genau 5) und `n..6` (bis zu 6) würden beide zu
`datentyp='n'` + `laenge=5/6`.

`MessageSegment` hat `kardinalitaet: String` + `wiederholbar: Boolean` — ebenfalls **ein**
Paar für **zwei** MaxWdh-Angaben.

> **Modelllücke 3:** Die MIG führt Standard- und BDEW-Angaben für **Status, Format und
> MaxWdh** parallel. Das heutige Schema hat für jedes dieser drei Merkmale nur einen
> Platz. Ohne additive Felder muss je Merkmal eine der beiden regulatorischen Aussagen
> verworfen werden — was §9 und dem übergeordneten Grundsatz widerspricht.

### Vorschläge zu Frage B (Entscheidung liegt beim Auftraggeber)

Die im Auftrag genannte Option (a) — nur BDEW in `pflicht`, Standard als Freitext in
`bedingung` — **wird nicht empfohlen**: sie verliert `D` und `N` (siehe oben) und legt
strukturierte Information in ein Freitextfeld.

| Option | Inhalt |
|---|---|
| **B1** (entspricht (b) im Auftrag, empfohlen) | Additive nullable Spalten, analog zur AHB-Erweiterung: `MessageField.status_standard`, `status_bdew`, `format_standard`, `format_bdew`; `MessageSegment.status_standard`, `status_bdew`, `max_wdh_standard`, `max_wdh_bdew`. `pflicht` wird weiter befüllt (Konvention z.B. BDEW ∈ {`M`,`R`} → `true`), bleibt aber eine **abgeleitete Bequemlichkeitsspalte**, nicht die Wahrheit. Bestehende Leser unverändert. |
| **B2** | Nur `status_bdew`/`status_standard` additiv, Format und MaxWdh weiterhin verdichtet | Löst Frage B im Wortsinn, lässt Modelllücke 3 für Format/MaxWdh offen. |
| **B3** | Beide Sichten als getrennte Zeilen | Verdoppelt die Zeilen und bricht die 1:1-Beziehung Feld↔Datenelement. Nicht empfohlen. |

---

## H. §5.4 — Codeliste-Referenzen

**Fundstelle:** Referenzen auf Codelisten stehen ausschließlich im Datenelement **DE1131
„Codeliste, Code" des Segments `STS`** — 51 Referenzzeilen, 50 verschiedene IDs.

**Form:** `G_0002 Codeliste Gas Nr. G_0002`, `GS_001 Codeliste Gas und Strom Nr. GS_001`.

**Verknüpfbarkeit mit dem Bestand aus Prompt 3 (EBD-Codelisten):** Die importierten
`CodeList.name` haben die Form `G_0002_Antwort auf Änderungsmeldung zur Bestandsliste-Gas`.
Das Präfix vor dem ersten `_` nach der ID ist deterministisch abgleichbar.

| | |
|---|---|
| distinkte Referenz-IDs im MIG | 50 |
| davon gegen importierte `CodeList` auflösbar | **45** |
| **nicht auflösbar** | **5**: `G_0018`, `G_0032`, `G_0033`, `G_0042`, `G_0045` |

Beispiel: `GS_001` → `CodeList 'GS_001_Ablehnung auf Stammdaten zur verbrauchenden Marktlokation'`.

> **Modelllücke 4:** `MessageField.codelist_id` ist ein **einzelner** Fremdschlüssel.
> DE1131 referenziert in *einer* Zelle **50 Codelisten**. Eine 1:1-FK kann das nicht
> abbilden. Selbst wenn man eine auswählte, wäre die Auswahl geraten.

**Vorschlag (nicht umgesetzt):** `codelist_id` für diese Felder **NULL lassen** und den
kompletten Referenztext unverändert im Anwendungstext erhalten (§9). Die auflösbaren
45 Referenzen zusätzlich maschinenlesbar zu hinterlegen, würde eine n:m-Zwischentabelle
erfordern — das wäre ein neues Modell und ist nach §10 nicht ohne Freigabe zulässig.
Alternativ: nur dort `codelist_id` setzen, wo ein Feld **genau eine** Codeliste
referenziert — das kommt in G1.1 allerdings **nicht** vor.

---

## I. Weitere Inhalte ohne Platz im Modell

Je Segment enthält die Detailtabelle zwei Freitextblöcke, die **kein** bestehendes Feld
aufnimmt:

| Block | Umfang | Beispiel |
|---|---|---|
| `Bemerkung:` | **131 von 148** Segmenten, 518 Zeilen | „Dieses Segment wird zur Angabe des Dokumentendatums verwendet." |
| `Beispiel:` | **148 von 148** Segmenten, 209 Zeilen | `DTM+137:199904081315?+00:303'` |

`MessageSegment.bedingung` ist laut Modellkommentar für „aufgelöste Fußnoten" der AHB
vorgesehen — fachlich etwas anderes. `MessageField.beispielwert` existiert, ist aber ein
Feld-, kein Segmentattribut.

> **Modelllücke 5:** Anwendungshinweis (`Bemerkung`) und EDIFACT-Beispiel je Segment haben
> keinen Platz. Gerade das Beispiel ist für einen späteren Nachrichtengenerator die
> unmittelbarste Referenz — es zu verwerfen wäre ein realer Verlust.

---

## J. §18 — Regressionsanker: RFF Nr 00038 (Prüfidentifikator)

Das aus Prompt 1 bekannte Segment, gegengeprüft mit dem vollständigen Testparser:

```
Segment RFF   Nr 00038   Zähler 0360   Pfad SG4/SG6   Status "M 1 M 1 2"
  Name: Prüfidentifikator
  DE C506  Referenz                  St M/M   Fmt ''/''
  DE 1153  Referenz, Qualifier       St M/M   Fmt 'an..3'/'an..3'   → "Z13 Prüfidentifikator"
  DE 1154  Referenz, Identifikation  St C/R   Fmt 'an..70'/'n5'     → 144 Zeilen
```

Abgleich der PI-Liste in DE1154 gegen den **bestehenden Extraktor aus Prompt 1**
(`extract_pi_entries()` auf derselben Datei):

| | |
|---|---|
| Prompt 1: Einträge / Seiten | 91 / S. 51–53 |
| Vollständiger Parser: Einträge aus DE1154 | **91** |
| Schlüsselmengen identisch | **ja** |
| Wertabweichungen | **0** |
| Stichprobe | `44001` → „GeLi Gas / Anmeldung NN"; `44182` → „SDÄ Gas / Ablehnung der Anfrage der komplexen Marktlokationsstruktur NB an LF" |

**Kein Widerspruch zu Prompt 1.** Die Zusammenführungslogik trägt auch für die größte
Zelle des Dokuments. Bemerkenswert nebenbei: `Format(BDEW)` ist hier `n5` — die MIG
schränkt das Feld auf genau 5 Ziffern ein, während der Standard `an..70` erlaubt. Ein
weiteres konkretes Beispiel für Modelllücke 3.

---

## K. Bestehende Funktionalität

Baseline vor jeder Änderung: **`112 passed`** (`backend/tests/`, 628 s).
Es wurde **keine** Datei des Bestands geändert; dieser Befund ist das einzige neue
Artefakt im Branch.

---

## L. Zusammenfassung — was zu entscheiden ist

| # | Frage | Befund | Vorschlag |
|---|---|---|---|
| **A** | pi_id-Konvention | `pi_id = NULL` ist mit dem AHB-Code verträglich, bietet aber **keinen Eindeutigkeitsschutz** (empirisch: 2 identische Zeilen akzeptiert). `sparte` fehlt im Constraint. | **A1** (Idempotenz über `quelle_hash` im Importer), optional **A4** (`grammatik_quelle`) |
| **B** | Standard vs. BDEW | Standard ∈ {`M`,`C`}, BDEW ∈ {`M`,`R`,`D`,`N`} (Legende kennt zusätzlich `O`, kommt nicht vor). **Nicht** verlustfrei auf Boolean abbildbar: `D` = dritter Zustand (97×), `N` = Verbot ≠ optional (189×), 71,0 % Spaltenabweichung inkl. 27× `M`/`N`. | **B1** (additive nullable Spalten für Status, Format, MaxWdh) |
| **1** | Segmentidentität | Segmentcode allein reicht **nicht**; Code + SG-Pfad reicht **auch nicht** (28× `CCI` in `SG4/SG8/SG10`). Eindeutig ist nur `Nr` (148/148). | Additive Felder für `Nr` und Segmentgruppen-Pfad |
| **2** | Übersicht vs. Detailtabellen | Detailtabellen enthalten alles; Übersicht ist vollständig redundant (0 Abweichungen). Verknüpfung über `Nr` deterministisch und dokumentweit stabil. | Extraktion aus Detailtabellen, Übersicht als Gegenprobe |
| **3** | Codelisten | 50 IDs, 45 auflösbar, 5 offen. Ein Feld referenziert 50 Listen — `codelist_id` (1:1) unzureichend. | `codelist_id` NULL lassen, Rohtext erhalten |
| **4** | Bemerkung / Beispiel | 131 bzw. 148 Segmente betroffen, kein Platz im Modell. | Entscheidung erbeten |

**Ohne Freigabe zu diesen Punkten wird kein Extraktionscode geschrieben.**
