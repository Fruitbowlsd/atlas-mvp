# Etappe 2 — Übrige EDIFACT-Nachrichtentypen

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 17.09.2026
**Status:** Etappe 2 abgeschlossen. Die Regelerweiterung O-11 ist am 17.09.2026 **bestätigt**.

Artefakte:

* [`etappe2_edifact_provenienz.json`](etappe2_edifact_provenienz.json): 32 Datensätze, validiert gegen [`provenienz_schema.json`](provenienz_schema.json) **v0.3**
* [`rollendefinition.md`](rollendefinition.md): außerordentliche Veröffentlichung als eigener Typ; O-11 und O-12 zu einem Punkt zusammengeführt

---

## 1. Zuschnitt: Warum Etappe 2 alle spartenübergreifenden Dokumente umfasst

Außer UTILMD trägt **kein** EDIFACT-Dokument eine Spartenangabe im Titel, weder bei der
BNetzA noch bei BDEW. Für Strom und Gas gilt also dieselbe Datei. Diese Dokumente in Etappe
2 (Strom) und Etappe 3 (Gas) doppelt zu erfassen, ergäbe zwei identische Datensätze. Deshalb:

* **Etappe 2** erfasst jedes spartenübergreifende EDIFACT-Dokument **einmal**, mit
  `sparte = beide`.
* **Etappe 3 (Gas)** behandelt nur, was gasspezifisch ist: SSQNOT (O-5), Festlegung GeLi
  Gas 3.0 (O-6) und die Frage, welche der „beide“-Dokumente in Gas tatsächlich angewendet
  werden. UTILMD Gas ist in Etappe 1 erledigt.

Umfang: 21 Dokumente aus Mitteilung 56 und **11 fortgeltende Dokumente**, die in Mitteilung
56 nicht vorkommen (Rohliste Etappe 0, Abschnitt 6.3).

## 2. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| Dokumente vollständig belegt | **32 / 32** (21 geändert durch M56, 11 fortgeltend) |
| erfasste Fassungen | **171**: 32 maßgeblich, 28 ergänzend, 7 ersetzt, 76 informativ, 28 nicht verbindlich |
| PDF geladen und gehasht | 45 (alle freien PDF-Fassungen der Stichtagsversionen) |
| offene Fälle **gelöst** | O-1 (gewertet), O-2, O-3, dazu 3× „UNGEKLÄRT“ aus dem Befund 01.04.2026 (CONTRL MIG, INSRPT AHB, INSRPT MIG) und der Vorgänger von ORDCHG MIG |
| offene Fälle **neu** | **0** (O-11 am 17.09.2026 bestätigt, umfasst das frühere O-12); 1 Rest aus O-3 ohne Einfluss |
| Widersprüche BNetzA ↔ BDEW | **0** |

## 3. Ergebnis: Welche Fassung gilt am 01.10.2026?

| Dokument | Version | Mitteilung | gültig ab | Status | maßgebliche Fassung | S. | SHA-256 | Vorgänger | in Konsultation (M57) |
|---|---|---|---|---|---|---|---|---|---|
| APERAK AHB | **1.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8321) ⚠ O-1 | 55 | `6c1aef93…31f1dfc0` | 1.0 | 1.1a |
| APERAK MIG | **2.2** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8328) | 27 | `d4255b19…415fc83f` | 2.1i | 2.2a |
| IFTSTA AHB | **2.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8336) | 76 | `884ddab1…05291818` | 2.0h | 2.1a |
| IFTSTA MIG | **2.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8339) | 144 | `f54ab9a9…5a924332` | 2.0g | 2.1a |
| INVOIC AHB | **1.0b** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8342) | 83 | `6f8218ab…2ca3de5a` | 1.0a | — |
| MSCONS AHB | **3.2** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8345) | 156 | `e6f93364…a3c850ed` | 3.1g | — |
| MSCONS MIG | **2.5** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8348) | 51 | `1be2e52b…f98bde25` | 2.4c | — |
| ORDCHG AHB | **1.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8351) | 10 | `87536bd8…cb8e7842` | 1.0a | — |
| ORDCHG MIG | **1.2** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8355) | 15 | `b0e46ffc…1715f4a6` | 1.1 | — |
| ORDERS AHB | **1.1b** | 56 | 01.10.2026 | verbindlich | **konsolidiert Stand 29.06.2026** (BDEW 8419) | 132 | `6b8826a8…dbd42ac1` | 1.1a | 1.1c |
| ORDERS MIG | **1.4c** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8362) | 144 | `d7c1f804…44538690` | 1.4b | — |
| ORDRSP AHB | **1.1b** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8363) | 74 | `220ca24c…551173a7` | 1.1a | 1.1c |
| ORDRSP MIG | **1.4c** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8367) | 42 | `947756af…ef3747f4` | 1.4b | — |
| PARTIN AHB | **1.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8370) | 88 | `d2e2ee08…9c1c287f` | 1.0f | — |
| PARTIN MIG | **1.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8373) | 64 | `a90c3fdf…7b68f489` | 1.0f | — |
| PRICAT AHB | **2.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8376) | 27 | `4c7e4c4d…0520e655` | 2.0f | — |
| PRICAT MIG | **2.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8379) | 31 | `553a608a…fafba46c` | 2.0e | — |
| QUOTES AHB | **1.1a** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8382) | 41 | `237c1caf…64d8d6e0` | 1.1 | 1.2 |
| QUOTES MIG | **1.3c** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8385) | 109 | `60d14847…0880b362` | 1.3b | 1.4 |
| REQOTE AHB | **1.2** | 56 | 01.10.2026 | verbindlich | **konsolidiert Stand 29.06.2026** (BDEW 8425) | 31 | `1e3e7104…da89ec09` | 1.1 | — |
| UTILTS AHB | **1.1** | 56 | 01.10.2026 | verbindlich | Basis (BDEW 8403) | 48 | `b0b8ae1b…adff0477` | 1.0 | — ¹ |
| COMDIS AHB | **1.0h** | 54 | 01.04.2026 | fortgeltend | Basis (BDEW 8125) | 12 | `5c72326a…37146dac` | — | — |
| COMDIS MIG | **1.0g** | 54 | 01.04.2026 | fortgeltend | Basis (BDEW 8128) | 21 | `674a8c42…6b4e8037` | — | — |
| REMADV AHB | **1.0a** | 54 | 01.04.2026 | fortgeltend | Basis (BDEW 8154) | 27 | `a0e23c0a…99f7cd64` | — | — |
| REMADV MIG | **2.9e** | 54 | 01.04.2026 | fortgeltend | Basis (BDEW 8157) | 35 | `0076cc6d…0a72e964` | — | — |
| INVOIC MIG | **2.8e** | 51 | 01.10.2025 | fortgeltend | Basis (BDEW 7873) | 74 | `ffb74414…1efad8a9` | — | — |
| REQOTE MIG | **1.3c** | 51 | 01.10.2025 | fortgeltend | Basis (BDEW 7906) | 60 | `6447176d…6279c631` | — | — |
| CONTRL AHB | **1.0** | 51 | 01.10.2025 | fortgeltend | **außerordentl. Veröff. Stand 11.12.2025** (BDEW 8193) ⚠ O-11 | 30 | `6ad48c23…e7f3f551` | — | 1.0a |
| UTILTS MIG | **1.1e** | 46 (+47) | 06.06.2025 | fortgeltend | **konsolidiert Stand 13.12.2024** (BDEW 7707) | 75 | `b1a8bb10…da93929c` | — | — ¹ |
| CONTRL MIG | **2.0b** | 24 (+27) | 01.10.2022 | fortgeltend | **außerordentl. Veröff. Stand 11.12.2025** (BDEW 8195) ⚠ O-11 | 17 | `1c795e92…0ce3abb9` | — | 2.0c |
| INSRPT AHB | **1.1g** | 24 (+27) | 01.10.2022 | fortgeltend | **außerordentl. Veröff. Stand 11.12.2025** (BDEW 8197) ⚠ O-11 | 24 | `1f770b7b…e986eee2` | — | — |
| INSRPT MIG | **1.1a** | 24 (+27) | 01.10.2022 | fortgeltend | **außerordentl. Veröff. Stand 26.07.2024** (BDEW 7319) ⚠ O-11 | 31 | `c587cda2…b2bf3534` | — | — |

¹ Mitteilung 57 (Konsultation für 01.04.2027) kündigt an, die UTILTS vollständig durch
API-Webdienste zu ersetzen.

**Gültig bis** ist bei allen 32 offen: Keine verbindliche Mitteilung nach Nr. 56 löst eine
dieser Versionen ab. **Vorgänger** führe ich nur für die 21 durch Mitteilung 56 geänderten
Dokumente (gültig bis 30.09.2026, abgeleitet). Die Vorgeschichte der 11 fortgeltenden
Dokumente wird nach Abschnitt 13 nicht rekonstruiert.

**Warum „fortgeltend“ trägt (Frage 2):** Die Version wurde in einer früheren verbindlichen
Mitteilung veröffentlicht. Mitteilung 56 nennt sie nicht. Keine spätere verbindliche
Mitteilung ersetzt sie. BDEW führt sie am Stichtag mit offenem `validTo`. Die Paarung mit
dem jeweiligen AHB passt (Abschnitt 5). Für die fortgeltenden Dokumente gibt es keine
Mitteilung, die den 01.10.2026 ausdrücklich bestätigt. Gültigkeit durch Fortschreibung ist
die Funktionsweise des Änderungsmanagements (Befund 01.04.2026).

## 4. Neuer Fassungstyp: außerordentliche Veröffentlichung (O-11, bestätigt)

> **Stand nach den Rückmeldungen vom 17.09.2026:** Regel bestätigt. Der Typ ist ab Schema v0.3 eigenständig
> geführt (`ausserordentliche_veroeffentlichung` mit eigenem Feld `stand_ausserordentlich`,
> getrennt von `fehlerkorrekturstand`), jede Fassung trägt ein Pflichtfeld
> `mitteilungsbezug`, und das frühere O-12 ist in O-11 aufgegangen. Einzelheiten und ein
> durchgerechnetes Beispiel stehen in [`rollendefinition.md`](rollendefinition.md).

Aufgetreten bei CONTRL AHB 1.0, CONTRL MIG 2.0b, INSRPT AHB 1.1g und INSRPT MIG 1.1a. Nach
Regel 7 der Rollendefinition habe ich den Typ **nicht still eingeordnet**, sondern am
Dokument geprüft:

* **Deckblatt:** „Außerordentliche Veröffentlichung [wegen Layoutanpassung]“, eigenes
  Stand-Datum, **gleiche Version**, „Ursprüngliches Publikationsdatum“.
* **Historie kumuliert**, z. B. CONTRL MIG 2.0b Stand 11.12.2025: „Fehler (06.12.2021)“ (der
  frühere konsolidierte Stand), „Anpassung (26.07.2024)“ (Layout), „Anpassung (11.12.2025)“
  (Segmentzähler ohne Präfix, laut Änd-ID 26091 ohne Implementierungsaufwand). INSRPT AHB
  11.12.2025 enthält zusätzlich eine Fehlerkorrektur (Änd-ID 26090, Deckblattdatum).
* **Keine BNetzA-Mitteilung** kündigt diese Fassungen an. Zwischen Mitteilung 54 (01.10.2025)
  und 55 (02.02.2026) gibt es keine Mitteilung, und das Wort „außerordentlich“ kommt in
  Mitteilung 54 bis 57 nicht vor.

**Vorläufig angewandte Regel (v0.2):** Außerordentliche Veröffentlichungen und konsolidierte
Fehlerkorrekturfassungen bilden eine gemeinsame Stand-Reihe je Version. Der neueste Stand
als PDF ist maßgeblich, ältere Stände sind `ersetzt`. Die Datensätze tragen dazu einen
Hinweis `offene_frage` mit `auswirkung_auf_auswahl = true`.

**Bestätigt am 17.09.2026.** Die zunächst erwogene Alternative (außerordentliche
Veröffentlichungen nur als `ergaenzend`) ist damit verworfen; sie hätte die Auswahl in
4 Dokumenten geändert.

## 5. Querprüfung AHB ↔ MIG (welche Dokumente zusammengehören)

Für alle **16 AHB** wurde die MIG-Version aus dem Dokumentinneren gelesen (UNH DE0057 in den
Anwendungsfall-Tabellen) und mit der MIG verglichen, die am Stichtag gilt:

| Ergebnis | AHB |
|---|---|
| **Deckblatt und UNH passen** (13) | APERAK, IFTSTA, INVOIC, ORDCHG, ORDERS, ORDRSP, PARTIN, PRICAT, UTILTS, COMDIS, REMADV, CONTRL, INSRPT |
| **UNH passt, Deckblatt nicht lesbar** (2) | QUOTES AHB 1.1a, REQOTE AHB 1.2: „Stand MIG“ 1.3c/1.4b übereinander → UNH = **1.3c** (O-2 gelöst) |
| **UNH passt, Deckblatt ohne Angabe** (1) | MSCONS AHB 3.2: kein Feld „Stand MIG“, UNH = 2.5 |

**16 / 16 AHB referenzieren die MIG, die am Stichtag gilt.** Damit ist auch belegt, dass die
fortgeltenden MIGs (INVOIC 2.8e, REQOTE 1.3c, COMDIS 1.0g, REMADV 2.9e, UTILTS 1.1e,
CONTRL 2.0b, INSRPT 1.1a) zu den AHB am Stichtag gehören.

## 6. Gelöste Fälle

| Fall | Lösung |
|---|---|
| **O-1** APERAK AHB 1.1 als „Informatorische Lesefassung“ gekennzeichnet | Das BNetzA-PDF ist **bytegleich** mit dem BDEW-Basis-PDF. Eine Fassung ohne Vermerk gibt es nicht, die informatorische Lesefassung ist eine eigene Word-Datei. **Wertung:** Beschriftungsfehler des Dokuments; die Datei bleibt maßgeblich, weil sie die amtlich veröffentlichte Anlage ist. Als `dokumentauffaelligkeit` dokumentiert, nichts umgedeutet. |
| **O-2** QUOTES/REQOTE AHB: Stand MIG mehrdeutig | UNH DE0057 = 1.3c in allen Anwendungsfall-Tabellen (Abschnitt 5) |
| **O-3** REQOTE MIG 1.3d nicht veröffentlicht | REQOTE MIG **1.3c** (Mitteilung 51) gilt fort, REQOTE AHB 1.2 referenziert 1.3c. Warum 1.3d fehlt, steht in keiner Quelle; ohne Einfluss auf die Auswahl. |
| CONTRL MIG „UNGEKLÄRT“ (Befund 01.04.2026) | **Mitteilung 24** (01.10.2021): Linktext „CONTRL 2.0b“, Anlage `CONTRL MIG 2.0b.pdf`, bytegleich mit der BDEW-Basisfassung. Verschoben durch **Mitteilung 27** auf 01.10.2022. Der alte Befund suchte nur in M40–57 und nach „CONTRL MIG“. |
| INSRPT AHB/MIG „UNGEKLÄRT“ | ebenfalls Mitteilung 24, verschoben durch 27 → gültig ab 01.10.2022 |
| ORDCHG MIG Vorgänger „ungeklärt“ | BDEW führt 1.1 mit `validTo 2026-09-30` im selben Thema; als Vorgänger übernommen (abgeleitet, ohne Mitteilungsbeleg für 1.1) |

Die gezielte Suche nach CONTRL MIG und INSRPT las die Mitteilungen 8, 11, 13, 14, 19, 20,
24, 25, 27, 28, 29, 31 und 33, nur auf diese beiden Formate hin, und endete mit dem Fund.

## 7. Neue offene Fälle

| ID | Fall | Bearbeitung |
|---|---|---|
| ~~O-11~~ | Regelerweiterung „außerordentliche Veröffentlichung“ (Abschnitt 4): **bestätigt am 17.09.2026**. Gilt für CONTRL AHB/MIG und INSRPT AHB/MIG und für alle weiteren Etappen. | erledigt |
| ~~O-12~~ | **In O-11 aufgegangen.** Fehlerkorrekturfassungen und außerordentliche Veröffentlichungen sind dasselbe Muster: BDEW veröffentlicht, BNetzA nicht. Ab v0.3 an jeder Fassung als `mitteilungsbezug` erfasst. Zahlen über Etappe 1 und 2: 61 Fassungen sind bytegleiche Mitteilungsanlagen, 32 Konsultationsanlagen, **116 ohne Mitteilungsbezug — darunter 11 der 36 maßgeblichen Fassungen.** | Zahlenbefund in Etappe 7 |

**Kleinere Befunde ohne Einfluss** (als `hinweise` in der JSON):

* UTILTS MIG 1.1e: BDEW-Titel „Stand 17.10.2024“, Deckblatt derselben PDF „18.10.2024“ (ersetzter Stand).
* INSRPT AHB, außerordentliche Veröffentlichung 26.07.2024: falsches „Ursprüngliches Publikationsdatum 26.07.2024“, korrigiert im Stand 11.12.2025.
* 3 XML-Fassungen „außerordentliche Veröffentlichung“ ohne Stand-Datum im Titel → `informativ`.
* Weißer Resttext auf 12 Deckblättern (u. a. „Konsultationsfassung“ bei COMDIS AHB, INVOIC AHB, INSRPT AHB-Basis).

## 8. Bestätigte Methodik aus Etappe 1, hier erneut belegt

* Das BNetzA-PDF ist bytegleich mit dem BDEW-Basis-PDF: **21 / 21** Dokumente aus Mitteilung 56 — und zusätzlich **11 / 11** fortgeltende Dokumente gegen ihre Anlage aus Mitteilung 54, 51, 46 bzw. 24 (auch die von 2021). Damit ist für alle 32 Dokumente belegt, dass BDEW dieselbe Datei führt wie die BNetzA.
* Die maßgebliche Fassung weicht von der amtlich verlinkten ab, sobald es spätere Stände
  gibt: ORDERS AHB, REQOTE AHB (Mitteilung 56) sowie UTILTS MIG, CONTRL AHB/MIG und INSRPT
  AHB/MIG (fortgeltend).
* Die Vollständigkeit der maßgeblichen gegen die Basisfassung ist bei allen 7 Fällen geprüft
  (Seiten, fünfstellige Kennungen, Inhaltsverzeichnis). Keine Kennung ist entfallen. Die
  Abweichungen im Inhaltsverzeichnis (CONTRL AHB 3 Zeilen, INSRPT AHB 2 Zeilen) sind in der
  Historie als Kapitelstruktur- bzw. Layoutanpassung dokumentiert.

**Ticket:** #64
