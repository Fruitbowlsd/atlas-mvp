# Aufnahmeregel — was gehört in den Regulatory State 01.10.2026?

**Ticket:** #64 · gilt ab Etappe 4 für alle weiteren Etappen, rückwirkend angewandt auf die
Etappen 0 bis 3 (Abschnitt 4). Ersetzt die Einzelfallentscheidung, die in Etappe 3 noch für
Etappe 7 vorgemerkt war (O-13).

## 1. Das Problem

Der Auftrag nennt zwei Quellen (BNetzA, BDEW MaKo) und eine Liste von Kategorien. Etappe 3
hat gezeigt, dass beides nicht ausreicht, um die Grenze zu ziehen:

* **SSQNOT** steht in keiner der 95 Mitteilungen und in keinem der 1.752 BDEW-Einträge, wird
  aber von PID 4.0 und von INVOIC AHB 1.0b am Stichtag verbindlich gebraucht.
* Auf derselben DVGW-Seite stehen **zehn weitere** Gas-Nachrichtentypen (TSIMSG, ALOCAT,
  IMBNOT, NOMINT, TRANOT, CHACAP, SCHEDL, DELRES, NOMRES, NÜVOR), teils mit eigenen Terminen
  zum 01.10.2026. Sie gehören zum Gastransport (Nominierung, Allokation, Kapazität) und zur
  Kooperationsvereinbarung Gas.

Ohne Regel müsste jeder dieser Fälle einzeln entschieden werden — und die Entscheidung wäre
nicht nachvollziehbar.

## 2. Die Regel

Ein Dokument gehört in den Regulatory State, wenn **mindestens eines** dieser drei Kriterien
zutrifft:

| | Kriterium | Beleg im Datensatz |
|---|---|---|
| **A** | Es ist **Anlage einer verbindlichen Mitteilung** der BK6/BK7-Reihe „Datenformate zur Abwicklung der Marktkommunikation“, die am Stichtag noch wirkt (unmittelbar oder fortgeltend). | `fassungen[].mitteilungsbezug.art = anlage_der_mitteilung(_bytegleich)` |
| **B** | Es wird in der am Stichtag gültigen **Anwendungsübersicht der Prüfidentifikatoren** (PID 4.0) in der Spalte „AHB“ oder als API-Webdienst geführt. | Fundstelle in PID 4.0 mit Lfd. Nr. und Prüfidentifikator |
| **C** | Ein Dokument aus A oder B **referenziert es verbindlich** (Muss-Angabe oder Bedingung), sodass der Prozess ohne dieses Dokument nicht ausführbar ist. | Fundstelle im referenzierenden Dokument mit Seite |

**Ausgeschlossen** ist alles, was keines der drei Kriterien erfüllt — insbesondere Dokumente
anderer Veröffentlichungsreihen (DVGW-Gastransport, Kooperationsvereinbarung Gas), auch wenn
sie zum selben Stichtag in Kraft treten. Der Ausschluss wird **belegt**, nicht behauptet: Im
Übergabebericht steht je ausgeschlossener Reihe, welche Prüfung negativ ausfiel.

**Nicht ausreichend** sind: gleicher Stichtag, gleiche Sparte, thematische Nähe, Nennung in
einer Anwendungshilfe ohne verbindlichen Formatbezug, und **Gattungsnennungen** („Anwendungshilfe",
„Kundenwertverfahren (z. B. TU München)") ohne Dokumentname.

### Kriterium C bei Namensverweis ohne Version (seit 18.09.2026, O-18)

Nennt das referenzierende Dokument einen Dokumentnamen **ohne Versionsnummer**, erfüllt das
Kriterium C, wenn die **Eindeutigkeit ausdrücklich geprüft und belegt** ist: Für den genannten
Namen gibt es genau ein Dokument mit genau einer am Stichtag gültigen Version. Der Datensatz
erhält dann `aufnahmekriterium.vermerk = "versionslos, aber eindeutig"` und das Pflichtfeld
`eindeutigkeitspruefung` mit den durchsuchten Quellen und dem Ergebnis (Schema v0.7).

* Welche **Fassung** gilt, bestimmt weiter die Prioritätsregel (neuester Stand) — nicht der
  Titel, den das referenzierende Dokument nennt, auch wenn er historisch ist.
* Die Prüfung wird **je Fall** durchgeführt, nie aus einem früheren Fall fortgeschrieben.
  Taucht ein zweites, ähnlich benanntes Dokument auf, ist der Fall neu zu bewerten.
* Erster Anwendungsfall: Codeliste der Standardlastprofile nach TU München 1.1 — Verweis in
  UTILMD MIG Gas G1.2, S. 143, mit dem Titel der Basisfassung; geprüft in BDEW-Dokumenten
  (1.752), BDEW-Marktprozessen (102), DVGW-Übersicht und 95 BNetzA-Mitteilungen: genau ein
  Dokument, genau eine Version.

## 3. Anwendung auf die DVGW-Reihe (Prüfung, nicht Behauptung)

Volltextsuche in PID 4.0 (86 Seiten, 1.344 Tabellenzeilen) nach allen elf DVGW-Nachrichten­
typen der Übersichtsseite „GABi Gastransport“:

| Nachrichtentyp | Treffer in PID 4.0 | Kriterium | Ergebnis |
|---|---|---|---|
| **SSQNOT** | **3** (davon 2 Tabellenzeilen: Lfd. Nr. 12170/12180, PI 70095/70096) | **B**, zusätzlich **C** (INVOIC AHB 1.0b S. 36, Bedingung [507]; INVOIC MIG 2.8e S. 27) | **aufgenommen** |
| TSIMSG, ALOCAT, IMBNOT, NOMINT, TRANOT, CHACAP, SCHEDL, DELRES, NOMRES, NÜVOR | **je 0** | keines | **nicht aufgenommen** |

Damit ist O-13 entschieden: Es wandert kein einziger Gastransport-Nachrichtentyp in den
State, und SSQNOT bleibt drin — beides aus derselben Regel, nicht aus zwei Einzelfällen.

## 4. Rückwirkende Prüfung der bisherigen 37 Dokumente

| Dokumente | erfülltes Kriterium |
|---|---|
| 34 aus Mitteilung 56 (Etappen 0–2), davon hier 25 EDIFACT | A |
| 11 fortgeltende aus Mitteilung 54, 51, 46, 24 | A (Anlage der jeweiligen Mitteilung, Bytegleichheit geprüft) |
| APERAK AHB, CONTRL AHB/MIG (ohne PID-Zeilen) | A — sie bleiben drin, obwohl B nicht greift |
| SSQNOT | B und C |

Kein Dokument des bisherigen Bestands fällt durch die Regel heraus, und keines kommt hinzu.

## 5. Folge für die weiteren Etappen

* **Etappe 4–6** wenden die Regel an, statt jede Kategorie neu zu begründen. Für jedes
  aufgenommene Dokument steht künftig im Datensatz, welches Kriterium greift.
* **Etappe 7** listet die geprüften, aber ausgeschlossenen Reihen mit Negativbeleg.
* **Etappe 8** nennt die Regel im Übergabebericht, weil sie den Umfang des Ergebnisses
  bestimmt.
