# Etappe 3 — Gasspezifika

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 17.09.2026
**Status:** Etappe 3 abgeschlossen. O-5 (SSQNOT) und O-6 (GeLi Gas 3.0) sind beantwortet.
**Ein Befund ändert den Zuschnitt des Auftrags** (Abschnitt 2).

Artefakt: [`etappe3_gas_provenienz.json`](etappe3_gas_provenienz.json) (SSQNOT, Schema v0.4).
Die Sparten-Belege der 32 Dokumente aus Etappe 2 sind in
[`etappe2_edifact_provenienz.json`](etappe2_edifact_provenienz.json) nachgetragen.

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| neue Dokumente belegt | **1** (SSQNOT 5.7, Gas) |
| Sparten-Zuordnung nachbelegt | **32** Dokumente aus Etappe 2, aus PID 4.0 |
| offene Fälle **gelöst** | O-5 (SSQNOT, mit Rest), O-6 (GeLi Gas 3.0) |
| offene Fälle **neu** | **2**: O-13 (dritte Quelle DVGW) — inzwischen durch die Aufnahmeregel entschieden; **O-14** (Bezeichnung des PI 70096: RLP ↔ RLM), bleibt bewusst offen |
| Widersprüche zwischen Quellen | **1** (Bezeichnung des Prüfidentifikators 70096: „RLP" gegen „RLM") |

## 2. O-5 SSQNOT — keine Lücke im Bestand, aber eine Lücke in der Quellenliste

**Das Format wird am Stichtag gebraucht.** Drei unabhängige Belege aus Dokumenten, die am
01.10.2026 gelten:

* **PID 4.0** (S. 27) führt zwei Zeilen: Lfd. Nr. 12170 „SSQNOT zur Übermittlung von
  Mehr-/Mindermengen — Mehr-/Mindermengenmeldung SLP — **70095**" und 12180 „… RLP —
  **70096**", beide mit Sparte Gas = X.
* **INVOIC AHB 1.0b** (S. 36) macht in den Anwendungsfällen 31007/31008 (MMM-Rechnung NB an
  MGV) die Bedingung [507] „Dokumentennummer der SSQNOT" zur Muss-Angabe.
* **INVOIC MIG 2.8e** (S. 27): „Für die MMMA-Prozesse referenziert die INVOIC durch Angabe
  der Dokumentennummer der MSCONS oder SSQNOT …"

**Es fehlt aber in beiden bisher genutzten Quellen:**

* **0 Treffer** in allen **95 Mitteilungen** der BK6/BK7-Reihe (Volltextsuche über alle
  Seiten der amtlichen Mitteilungsliste, 17.09.2026).
* **0 Treffer** in den **1.752 Einträgen** der BDEW-MaKo-Dokumenten-API.

**Gefunden wurde es bei einer dritten Stelle:** der **DVGW Service & Consult GmbH**, Reihe
„GABi Gastransport". SSQNOT ist laut Dokument „die Definition der DVGW
Mehr-/Mindermengen-Mitteilung (SSQNOT), einer angepassten Teilmenge der EDIFACT UNSM Order
Response Nachricht (ORDRSP) … für den Elektronischen Datenaustausch (EDI) in der
Gaswirtschaft".

| | |
|---|---|
| Maßgebliche Fassung | **SSQNOT 5.7, konsolidierte Lesefassung mit Fehlerkorrekturen, Stand 31.10.2021** |
| Gültig ab | 01.12.2019 (DVGW-Übersicht), Gültig bis offen |
| Ursprüngliches Publikationsdatum | 01.04.2019 |
| Umfang | 27 Seiten, SHA-256 `3b499f4a…56e8c60a` |
| Ersetzte Fassung | 5.7 Stand 31.03.2020 (28 S.) |
| Mitteilungsbezug | `keine_mitteilungsreihe` |

Die Datei deckt **MIG- und AHB-Inhalte zugleich** ab: Segmentlayout (u. a. RFF+Z13 mit den
Prüfidentifikatoren 70095/70096, S. 12) **und** eine Anwendungsfall-Tabelle (S. 23) mit
Prozessschritt, Prüfidentifikator, „NB an MGV" und Zuordnung — mit „KoV" als
Prozessbeschreibung.

**Rest von O-5:** Ein Dokument mit genau dem Namen, den PID 4.0 in der AHB-Spalte nennt
(„SSQNOT zur Übermittlung von Mehr-/Mindermengen"), gibt es nicht. Dass PID 4.0 damit die
DVGW-Nachrichtenbeschreibung meint, ist naheliegend, aber nicht ausdrücklich belegt.

**O-14 — Widerspruch zwischen den Quellen, bleibt offen.** Derselbe Prüfidentifikator
**70096** heißt in PID 4.0 (S. 27) „Mehr-/Mindermengenmeldung **RLP**" und in SSQNOT 5.7
(S. 12) „Mehr-/Mindermengenmeldung **RLM**". **Beide Bezeichnungen werden unverändert
festgehalten und nicht aufgelöst**; welche fachlich richtig ist, lässt sich aus den Quellen
nicht belegen. Für 70095 stimmen beide Quellen überein („SLP"). Die Auswahl der Version
berührt das nicht.

## 3. O-13 (neu) — Die Quellenliste des Auftrags ist für Gas nicht vollständig

Der Auftrag nennt BNetzA (Abschnitt 2) und BDEW MaKo (Abschnitt 5). Für Gas kommt eine
**dritte Stelle** hinzu: die DVGW Service & Consult GmbH. Auf derselben Übersichtsseite
stehen neben SSQNOT weitere Gas-Nachrichtentypen mit eigenen Ständen und Terminen, z. B.
**TSIMSG 5.11** (Stand 01.04.2026, **gültig ab 01.10.2026**), ALOCAT 5.11a, IMBNOT 5.7a,
NOMINT 4.6, TRANOT 5.8b, CHACAP/SCHEDL/DELRES/NOMRES (Fehlerkorrekturen 01.02.2026).

Diese Nachrichtentypen betreffen den Gastransport (Nominierung, Allokation, Kapazität) und
gehören zur Kooperationsvereinbarung Gas, nicht zur Marktkommunikation im Sinne der
BK6-Mitteilungen. **Entschieden durch die Aufnahmeregel** ([`aufnahmeregel.md`](aufnahmeregel.md), seit
18.09.2026): Aufgenommen wird, was Anlage einer verbindlichen Mitteilung ist (A), in PID 4.0
geführt wird (B) oder von einem solchen Dokument verbindlich referenziert wird (C). Von den
elf DVGW-Nachrichtentypen erfüllt **nur SSQNOT** ein Kriterium (B und C); die übrigen zehn
haben **null** Treffer in PID 4.0 und bleiben draußen. Keine Einzelfallentscheidung mehr in
Etappe 7, sondern ein Negativbeleg je Reihe.

## 4. O-6 GeLi Gas 3.0 — kein Einfluss auf die Formatversionen

Beschluss **BK7-24-01-009** vom **12.09.2025** (46 Seiten, SHA-256 `168d40f6…`):

* **Keine Nennung** von EDIFACT, UTILMD oder einer Nachrichtentypversion (0 Treffer).
* Für Datenformate verweist der Beschluss weiter: „Anforderungen an den Daten- und
  Nachrichtenaustausch, wie insbesondere das anzuwendende Datenformat, die zu nutzenden
  Nachrichtentypen … ergeben sich aus der Anlage zu dem Beschluss BK7-06-067 vom 20. August
  2007 in der jeweils geltenden Fassung."
* **Am Stichtag wirksam, aber vertraglich, nicht formatbezogen:** Die Festlegung
  BK7-17-026 (Messstellenbetreiberrahmenvertrag Gas) „wird mit Wirkung zum **01.10.2026**
  widerrufen"; Netzbetreiber und Messstellenbetreiber müssen „bis zum **01.10.2026** einen
  neuen Messstellenbetreiberrahmenvertrag … erarbeiten".

**Ergebnis:** GeLi Gas 3.0 ändert keine Dokumentversion des Regulatory State. Der Vorbehalt
aus Mitteilung 56 („abweichende Umsetzungstermine … aus Festlegungen") greift hier nicht für
Formate, wohl aber für Verträge.

## 5. Sparten-Zuordnung der spartenübergreifenden Dokumente (Frage aus Etappe 2)

Aus **PID 4.0** ausgewertet: je Zeile die Spalten „Sparte Strom" und „Sparte Gas" (X / --),
ausgelesen über die Spaltenposition. 1.344 Zeilen erfasst.

| AHB | Zeilen | Strom = X | Gas = X | Sparte im Datensatz |
|---|---:|---:|---:|---|
| UTILMD AHB Strom | 330 | 330 | 0 | Strom (Titel) |
| UTILMD AHB Gas | 131 | 0 | 131 | Gas (Titel) |
| MSCONS AHB | 157 | 95 | 62 | beide |
| IFTSTA AHB | 154 | 136 | 18 | beide |
| ORDRSP AHB | 116 | 96 | 20 | beide |
| ORDERS AHB | 111 | 98 | 13 | beide |
| REMADV AHB | 111 | 77 | 34 | beide |
| INVOIC AHB | 42 | 24 | 18 | beide |
| PARTIN AHB | 42 | 27 | 15 | beide |
| INSRPT AHB | 22 | 12 | 10 | beide |
| COMDIS AHB | 11 | 9 | 2 | beide |
| PRICAT AHB | 9 | 8 | 1 | beide |
| QUOTES AHB | 9 | 8 | 1 | beide |
| REQOTE AHB | 8 | 7 | 1 | beide |
| ORDCHG AHB | 5 | 3 | 2 | beide |
| **UTILTS AHB** | 26 | 26 | **0** | **Strom** (korrigiert) |
| SSQNOT | 2 | 0 | 2 | Gas |
| APERAK AHB, CONTRL AHB | 0 | — | — | beide, **ohne Einzelnachweis** |

Zwei Korrekturen gegenüber Etappe 2:

1. **UTILTS AHB 1.1 und UTILTS MIG 1.1e sind Strom**, nicht „beide": PID 4.0 führt keinen
   einzigen Gas-Anwendungsfall. Das ist ein Negativbefund aus einer Quelle, kein
   ausdrücklicher Ausschluss — im Datensatz so vermerkt. Dazu passt, dass Mitteilung 57 die
   UTILTS durch API-Webdienste Strom ersetzen will.
2. **APERAK AHB und CONTRL AHB** haben keine PID-Zeilen (Servicenachrichten ohne eigene
   Prüfidentifikatoren). Sie bleiben „beide", jetzt aber ausdrücklich ohne positiven
   Einzelnachweis.

Die MIG-Dokumente erben die Sparte von ihrem AHB; sie haben keine eigenen PID-Zeilen.

**Methodischer Hinweis:** Gezählt sind nur Zeilen mit eindeutigem „X". Bei mehrzeiligen
Tabellenzeilen liest die Extraktion gelegentlich nur eine der beiden Spalten; die Zahlen
sind deshalb **untere Schranken**. Für die Aussage „Gas kommt vor" genügt das, für „Gas
kommt nicht vor" ist es ein Indiz, kein Beweis.

## 6. Was Etappe 3 nicht behandelt

* Die übrigen DVGW-Nachrichtentypen (Gastransport) — durch die Aufnahmeregel ausgeschlossen, Negativbeleg in Etappe 7.
* Gas-Prozessdokumente (GeLi Gas 2.0, WiM Gas 2.0, KoV) als eigene Artefakte des Regulatory
  State. Sie sind Prozess-, keine Formatdokumente; im Auftrag nicht als Kategorie geführt.
  Zur Kenntnis: Die BDEW-Plattform führt sie in einem zweiten Bereich („Marktprozesse",
  102 Dokumente, eigene API), der bisher nicht ausgewertet ist.
* Ein Fund daraus mit Stichtagsbezug: Die Anwendungshilfe „Prozesse zur Ermittlung und
  Abrechnung von Mehr-/Mindermengen Strom und Gas" (Version 2.1, Stand 18.03.2025) sagt zum
  Use-Case „Bestellung der bilanzierten Menge beim ÜNB": „Ab dem 01.10.2026 00:00 Uhr findet
  dieser Use-Case keine Anwendung mehr." Das betrifft Strom und ist ein Prozess-, kein
  Formatbefund — für Etappe 7 vorgemerkt.

**Ticket:** #64
