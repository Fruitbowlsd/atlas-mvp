# Etappe 5 — Entscheidungsbaum-Diagramme (EBD)

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 18.09.2026
**Grundlage:** Auftragsfassung vom 18.09.2026, Abschnitt 4B und 6/6a, 11a–11e.
**Status:** Etappe 5 abgeschlossen.

Artefakt: [`etappe5_ebd_provenienz.json`](etappe5_ebd_provenienz.json) (1 Datensatz,
5 Fassungen, Schema v0.6).

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| Dokumente belegt | **1** (Entscheidungsbaum-Diagramme und Codelisten 4.3) |
| erfasste Fassungen | 5 (3 PDF, 2 informatorische Word-Fassungen) |
| offene Fälle neu | **1** (O-17: Codelisten-Kennung S_0088 ohne Ziel) |
| Widersprüche zwischen Quellen | **0** |
| **O-16 erledigt** | ja, vorgezogen (Abschnitt 5) |

## 2. Ergebnis

| | |
|---|---|
| Dokument | Entscheidungsbaum-Diagramme und Codelisten für die Antwortnachrichten |
| Version | **4.3** (Vorgänger 4.2, gültig bis 30.09.2026) |
| Mitteilung | 56, veröffentlicht 01.04.2026, verbindlich ab **01.10.2026**, gültig bis offen |
| Maßgebliche Fassung | **konsolidierte Lesefassung mit Fehlerkorrekturen, Stand 23.06.2026** (BDEW 8408), 831 Seiten, SHA-256 `bf589a7a…af048730` |
| Ergänzend | Basisfassung (BDEW 8314, 832 S.) — bytegleich mit der Anlage der Mitteilung 56 |
| Aufnahme | Kriterium **A** (Anlage der Mitteilung 56) und **C** (285 EBD-Kennungen aus der PID referenziert) |
| In Konsultation | 4.4 (Mitteilung 57, für 01.04.2027) |

**Inhalt der maßgeblichen Fassung (Abschnitt 4B):** 364 EBD-Kennungen (`E_xxxx`) und 103
Codelisten-Kennungen (`G_`, `GS_`, `S_`). Gegenüber der Basisfassung kommt eine EBD-Kennung
hinzu (**E_0265**), die Codelisten-Kennungen bleiben unverändert.

**Besonderheit gegenüber AHB und MIG:** Die konsolidierte Fassung führt hier **beides**
zusammen — 24 Einträge mit Status „Genehmigt“ (die Änderungen gegenüber 4.2) und 12
Fehlerkorrektur-Einträge (11.12.2025, 31.03.2026, 23.06.2026). Bei AHB und MIG ist die
Historie der konsolidierten Fassung auf die Fehlerkorrekturen verkürzt. Die Basisfassung
bleibt trotzdem als `ergaenzend` erfasst.

Das Dokument bestätigt die Regel aus Abschnitt 7 selbst, auf Seite 2: „Die zusätzlich
veröffentlichte Word-Datei dient als informatorische Lesefassung … Die PDF-Datei ist das
gültige Dokument.“

## 3. Querprüfung PID → EBD (zugehörige Prozesse und Prüfidentifikatoren)

Aus der **maßgeblichen** PID-Fassung (Stand 12.08.2026) wurde die Spalte „EBD-Code / Code
Codeliste“ über Spaltenpositionen ausgelesen: 1.352 Tabellenzeilen, darin 296 distinkte
Kennungen (285 EBD, 11 Codelisten).

| Prüfung | Ergebnis |
|---|---|
| Von der PID referenzierte EBD-Kennungen, in 4.3 vorhanden | **285 von 285 (100 %)** |
| Von der PID referenzierte Codelisten-Kennungen, in 4.3 vorhanden | 10 von 11 — **eine fehlt** (O-17) |
| EBD-Kennungen in 4.3, die keine PID-Zeile referenziert | **79** |

Die 79 nicht referenzierten EBD sind über keinen Prüfidentifikator erreichbar. Das ist keine
Fehlfunktion des Dokuments, aber es begrenzt, was Atlas später über die PID an EBD anbinden
kann — für die fachliche Analyse (Abschnitt 12) vorgemerkt.

## 4. O-17 (neu): Codelisten-Kennung S_0088 ohne Ziel

Die PID führt in Zeile 26100 für den Prüfidentifikator **55024** (UTILMD AHB Strom) die
Kennung **S_0088**. Diese Kennung existiert:

* **nicht** in EBD und Codelisten 4.3 (dort laufen die `S_`-Kennungen bis S_0087),
* **nicht** in einem der übrigen am Stichtag maßgeblichen Dokumente (Volltextsuche über alle
  geladenen AHB, MIG und Codelisten),
* nur in der PID selbst, und zwar in beiden Fassungen (Basis und Stand 12.08.2026) — die
  Fehlerkorrekturen haben daran nichts geändert.

Der Verweis bleibt **unaufgelöst**. Er wird nicht auf eine ähnliche Kennung „korrigiert“;
Dokumentfehler sind regulatorische Realität, kein Extraktionsfehler.

## 5. O-16 erledigt: PID-Basisfassung gegen maßgeblichen Stand

Die Sparten- und Referenzauswertungen aus Etappe 3 und 4 stammten aus der PID-Basisfassung.
Sie wurden jetzt gegen den maßgeblichen Stand 12.08.2026 wiederholt:

| | Basis (01.04.2026) | maßgeblich (Stand 12.08.2026) |
|---|---|---|
| ausgewertete Tabellenzeilen | 1.344 | 1.352 |
| UTILMD AHB Gas | 131 Zeilen / 0 Strom / 131 Gas | 132 / 0 / **132** |
| alle übrigen 17 AHB-Werte | unverändert | unverändert |
| UTILTS AHB | 26 / 26 / **0** | 26 / 26 / **0** |

**Keine Aussage aus Etappe 3 kippt.** UTILTS bleibt ohne Gas-Anwendungsfall, die 13
„beide“-Belege bleiben bestehen, SSQNOT bleibt Gas. Der Unterschied sind eine zusätzliche
Gas-Zeile bei UTILMD AHB Gas und sieben Zeilen, in denen die Extraktion kein AHB-Feld liest.
O-16 ist damit beantwortet und muss in Etappe 7 nicht erneut geprüft werden.

## 6. Abgrenzung

* Die Entscheidungslogik selbst (Prüfschritte, Antwortcodes, Cluster) wird hier **nicht**
  extrahiert — das ist fachliche Analyse nach Abschnitt 12.
* Der „Änderungsantrag EBD 1.5“ bleibt draußen (Etappe 4, Negativbeleg): ein Formular, keine
  regulatorische Festlegung.
* Mitteilung 57 kündigt für 4.4 an, den Antwortcode A99 in einzelnen EBD zu streichen und
  die Prüflogik von E_0622 für Einspeisefälle zu überarbeiten. Für den Stichtag ohne Wirkung.

**Ticket:** #64
