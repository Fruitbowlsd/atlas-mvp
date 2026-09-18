# Etappe 4 — Querschnittsdokumente: PID, Codelisten, Allgemeine Festlegungen

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 18.09.2026
**Grundlage:** Auftragsfassung vom 18.09.2026 ([`auftrag.md`](auftrag.md)), bewertet nach
Abschnitt 6/6a, 11a–11e; Aufnahme nach [`aufnahmeregel.md`](aufnahmeregel.md).
**Status:** Etappe 4 abgeschlossen.

Artefakt: [`etappe4_querschnitt_provenienz.json`](etappe4_querschnitt_provenienz.json)
(10 Datensätze, 37 Fassungen, Schema v0.6).

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| Dokumente aufgenommen und belegt | **10** |
| geprüft und **nicht** aufgenommen (mit Negativbeleg) | **6** |
| erfasste Fassungen | 37 (26 PDF geladen und gehasht) |
| offene Fälle neu | **1** (O-15: zwei Dezember-2024-Stände der Lokationsbündel-Codeliste) |
| Widersprüche zwischen Quellen | **0** |

## 2. Ergebnis

| Dokument | Version | Mitteilung | gültig ab | maßgebliche Fassung | S. | Aufnahme |
|---|---|---|---|---|---|---|
| Allgemeine Festlegungen | **6.1d** | 56 | 01.10.2026 | Basis (BDEW 8319) | 118 | A + C |
| Anwendungsübersicht der Prüfidentifikatoren | **4.0** | 56 | 01.10.2026 | **konsolidiert Stand 12.08.2026** (BDEW 8461) | 83 | A + B |
| Codeliste der Konfigurationen | **1.4** | 56 | 01.10.2026 | Basis (BDEW 8332) | 64 | A + C |
| Codeliste der Verwendungszwecke | **1.0** | 56 | 01.10.2026 | **konsolidiert Stand 29.06.2026** (BDEW 8417) | 9 | A + C |
| Codeliste der OBIS-Kennzahlen und Medien | **2.5c** | 54 | 01.04.2026 | Basis (BDEW 8123) | 46 | A + C |
| Codeliste der Artikelnummern und Artikel-ID | **5.6** | 51 | **01.09.2025** ¹ | **konsolidiert Stand 30.09.2025** (BDEW 8113) | 60 | A + C |
| Codeliste der Zeitreihentypen | **1.1d** | 19 | 01.10.2021 | **konsolidiert Stand 16.07.2021** (BDEW 7356) | 12 | A + C |
| Codeliste der europäischen Ländercodes | **1.0** | 58 ² | 01.10.2017 | **konsolidiert Stand 30.03.2023** (BDEW 7342) | 5 | A + C |
| Codeliste der Lokationsbündelstrukturen | **1.0** | 33 | 01.10.2023 | **konsolidiert Stand 13.12.2024** (BDEW 7713) | 52 | A + B + C |
| Codeliste der Standardlastprofile nach TU München-Verfahren | **1.1** | **keine** ³ | 01.10.2015 | **konsolidiert Stand 22.05.2015** (BDEW 7352) | 10 | **C — „versionslos, aber eindeutig“** (O-18 gelöst) |

¹ Abweichender Umsetzungstermin, Mitteilung 51 wörtlich: „bereits zum 1. September 2025
umzusetzen" (MsbG-Anpassungen, neue Artikel-ID ab 01.01.2026).
² Ältere Mitteilungsreihe (GPKE/GeLi Gas, Mitteilung Nr. 58), nicht die Reihe „Datenformate".
³ In keiner der 95 Mitteilungen; nur auf BDEW-MaKo. **Korrektur 18.09.2026:** Kriterium C ist nur teilweise erfüllt. Einziger Dokumentverweis: UTILMD MIG Gas G1.2, S. 143 — mit Dokumentname (Titel der Basisfassung), aber ohne Version. Die zuvor gezählten 7 Treffer in UTILMD AHB Gas sind Verfahrensnennungen („Kundenwertverfahren (z. B. TU München)“) und keine Dokumentverweise. **Entschieden 18.09.2026:** Ein Namensverweis ohne Version genügt bei belegter Eindeutigkeit (Auftrag 11e). Eindeutigkeit geprüft in allen vier Quellen — genau ein Dokument, genau eine Version. Aufgenommen mit Vermerk „versionslos, aber eindeutig“; `relevanz_unklar` aufgehoben.

**Gültig bis** ist bei allen 10 offen. **6 von 10** sind nur mit einer konsolidierten Fassung
maßgeblich abgedeckt — bei der PID sogar erst im zweiten Korrekturstand.

**Bytegleichheit BNetzA ↔ BDEW:** geprüft für 9 der 10 Dokumente, **8 davon bytegleich** —
Allgemeine Festlegungen, PID, Konfigurationen und Verwendungszwecke gegen Mitteilung 56,
dazu OBIS gegen Mitteilung 54, Artikelnummern gegen 51, Zeitreihentypen gegen 19 und
Ländercodes gegen 58. **Die einzige Abweichung ist die Lokationsbündel-Codeliste** und damit
kein eigener Fall, sondern genau O-15 (Abschnitt 4): Die verglichene Datei aus Mitteilung 32
war die Konsultationsfassung, die verbindliche Fassung steht in Mitteilung 33 und ist dort
nicht mehr abrufbar. Das zehnte Dokument (Standardlastprofile TU München 1.1) hat keine
BNetzA-Anlage, für die ein Vergleich möglich wäre.

## 3. Geprüft und nicht aufgenommen (Negativbeleg nach Aufnahmeregel)

| Dokument | A (Mitteilungsanlage) | B (in PID 4.0) | C (verbindlich referenziert) | Ergebnis |
|---|---|---|---|---|
| Codeliste der Temperaturanbieter 1.0i | kein Treffer in 95 Mitteilungen | 0 | **0** Referenzen in den 37 maßgeblichen Fassungen | nicht aufgenommen |
| Gruppierungen der EDI@Energy-Dokumente 2.2 | kein Treffer | 0 | 0 | nicht aufgenommen (Übersichtsdokument) |
| Änderungsantrag EBD 1.5 | kein Treffer | 0 | 0 | nicht aufgenommen (Formular) |
| EDI@Energy-Anwendungshilfe Beispiele von Berechnungsformeln für das Solarpaket 1, 1.1 | kein Treffer | 0 | 0 | nicht aufgenommen |
| BDEW-Anwendungshilfen vom 18.08.2026 (Berechnungsformeln in API-Webdiensten; Darstellung von Lokationsbündeln; Einführungsszenario UTILMD) | kein Treffer | 0 | keine namentliche Muss-Referenz | nicht aufgenommen; das Einführungsszenario bleibt als Hinweis an den UTILMD-Datensätzen (Etappe 1) |

Der Suchbegriff „Anwendungshilfe" kommt in den maßgeblichen Fassungen zwar vor (z. B. REQOTE
MIG 11-mal), aber ohne Nennung eines konkreten Dokuments mit Version. Eine generische
Erwähnung erfüllt Kriterium C nicht — sonst würde jede Anwendungshilfe über einen
Allgemeinbegriff in den State rutschen.

**Die Temperaturanbieter-Codeliste ist der auffälligste Fall:** Sie ist am Stichtag bei BDEW
gültig, aber weder in einer Mitteilung noch in PID 4.0 noch in einer der 37 maßgeblichen
Fassungen genannt (auch nicht in MSCONS oder UTILMD Gas, wo man sie vermuten würde). Sie
bleibt draußen — mit diesem Negativbeleg, nicht mit einer Vermutung.

## 4. O-15 (neu): Lokationsbündel-Codeliste

Drei Punkte, die zusammengehören:

1. **Die Anlage aus Mitteilung 32 ist nicht bytegleich** mit der BDEW-Basisfassung (892 KB
   gegen 5,8 MB). Mitteilung 32 war die Konsultation; die verbindliche Fassung steht in
   **Mitteilung 33** und wird dort mit „(PDF / 6 MB)" ausgewiesen — das passt zur BDEW-Datei.
2. **Der Anlagen-Link der Mitteilung 33** (auf `data.bundesnetzagentur.de`) liefert heute
   **HTTP 404**. Ein Byte-Beleg ist deshalb derzeit nicht möglich; die Zuordnung stützt sich
   auf Dokumentname, Version und die Größenangabe der Mitteilung.
3. **Zwei Fehlerkorrekturstände im Dezember 2024**, einen Tag auseinander: Stand 12.12.2024
   (BDEW 7663, `validTo` 31.12.2024, 0,96 MB) und Stand 13.12.2024 (BDEW 7713, offen,
   6,7 MB). Maßgeblich ist 7713 als neuester Stand mit offener Gültigkeit; 7663 ist
   `ersetzt`. Warum es zwei Dateien gibt, ist nicht belegbar.

Zusätzlich, ohne Wirkung auf den Stichtag: Mitteilung 57 kündigt an, dass diese Codeliste mit
dem Ausbau der Lokationsbündelstruktur aus der UTILMD „obsolet" wird (Konsultation für
01.04.2027).

## 5. Weitere Befunde

* **PID 4.0 hat zwei Korrekturstände** (29.06.2026 und 12.08.2026). Maßgeblich ist der
  zweite. Das ist bemerkenswert, weil die PID zugleich das Dokument ist, an dem Kriterium B
  der Aufnahmeregel gemessen wird — die Sparten- und Referenzauswertungen aus Etappe 3 und 4
  stammen aus der Basisfassung; sie sind für Etappe 7 gegen den Stand 12.08.2026 zu
  wiederholen.
* **Korrektur vor Inkrafttreten:** Bei den Zeitreihentypen (Korrektur 16.07.2021, gültig ab
  01.10.2021) und den Standardlastprofilen (Korrektur 22.05.2015, gültig ab 01.10.2015) liegt
  der Fehlerkorrekturstand **vor** dem Gültigkeitsbeginn. Die Stand-Reihe ordnet trotzdem
  eindeutig.
* **Alter des Bestands:** Die Querschnittsdokumente reichen von 2015 (Standardlastprofile)
  bis 2026. Vier stammen aus Mitteilung 56, sechs gelten aus früheren Veröffentlichungen fort.

## 6. Nächste Schritte

Etappe 5 (Entscheidungsbaum-Diagramme). Das EBD-Dokument 4.3 ist bereits als Rohdatensatz
vorhanden (Anlage der Mitteilung 56, konsolidierter Stand 23.06.2026 bei BDEW).

**Ticket:** #64
