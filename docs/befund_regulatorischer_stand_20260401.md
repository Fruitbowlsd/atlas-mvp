# Empirischer Befund — Regulatorischer Stand zum 01.04.2026

**Status: Recherche abgeschlossen, STOP vor Implementierung.** Keine Parser-, Schema-,
Import- oder Datenmodelländerung. Der Befund ist ausschließlich eine Rekonstruktion des
regulatorischen Zustands zum Stichtag **01.04.2026** aus offiziellen Quellen.

Erhebungsdatum: 05.09.2026. Alle Angaben stammen aus dem HTML der amtlichen
BNetzA-Mitteilungsseiten (`bundesnetzagentur.de`, Beschlusskammer 6/7, Reihe
„Mitteilungen zu den Datenformaten zur Abwicklung der Marktkommunikation") sowie aus
der lokal vorliegenden Anwendungsübersicht der Prüfidentifikatoren 3.3.

---

## A. Executive Summary

### Was untersucht wurde

Rekonstruiert wurde, welche Formate, Dokumenttypen, Regelwerke, Codelisten und
technischen Artefakte am **01.04.2026** verbindlich anzuwenden waren — für **beide
Sparten** (Gas und Strom) und über alle in den Quellen belegten Marktprozesse hinweg,
nicht nur Gas/Lieferbeginn.

**69 Einträge** stehen in der Master-Formatliste (Abschnitt C). Jeder Eintrag hat ein
explizites Ergebnis.

### Zentraler Befund: Mitteilung 54 deckt nur ein Drittel ab

Mitteilung Nr. 54 (01.10.2025) veröffentlicht **29 Dokumente** und erklärt sie
wörtlich für „verbindlich ab dem 01.04.2026". Das ist der einzige Textbeleg, der den
Stichtag ausdrücklich nennt.

Der tatsächlich am 01.04.2026 geltende Bestand ist rund **doppelt so groß**. Der Grund
ist strukturell und für das Datenmodell von Atlas die wichtigste Erkenntnis dieser
Recherche:

> **Eine Mitteilung veröffentlicht ausschließlich die _geänderten_ Dokumente.**
> Der geltende Stand ist keine Momentaufnahme einer Mitteilung, sondern eine
> **Überlagerung mehrerer Mitteilungen unterschiedlichen Alters**. Dokumente, die seit
> Jahren unverändert sind, tauchen in keiner aktuellen Mitteilung auf und gelten
> trotzdem.

Konkret setzt sich der Stand zum 01.04.2026 aus **fünf** verbindlichen
Veröffentlichungen zusammen:

| Mitteilung | veröffentlicht | verbindlich ab | Beitrag zum 01.04.2026-Stand |
|---|---|---|---|
| **54** | 01.10.2025 | **01.04.2026** | 29 Dokumente (UTILMD Gas, COMDIS, INVOIC AHB, MSCONS AHB, ORDERS AHB, ORDRSP, PARTIN, REMADV, AF 6.1c, PID 3.3, OBIS 2.5c, EBD 4.2, XML-Redispatch, RzÜ AS4 2.5) |
| **51** | 01.04.2025 | 01.10.2025 | APERAK, CONTRL, IFTSTA, INVOIC MIG, ORDERS MIG, PRICAT, QUOTES, REQOTE, Codelisten, 8 XML-Dokumenttypen, RzÜ-Familie |
| **46** | 01.10.2024 | 04.04.2025 → **06.06.2025** | UTILMD **Strom** 2.1/S2.1, UTILTS, ORDCHG AHB, API-Guideline, Codeliste Konfigurationen, AS4-Profil |
| **43** | 03.07.2024 | 04.04.2025 → 06.06.2025 | API-Webdienste MaLo-ID 1.0.0 |
| **42** | 19.06.2024 | 04.04.2025 → 06.06.2025 | APERAK MIG 2.1i |

Die Verschiebung 04.04.2025 → 06.06.2025 ist **nicht** in den Mitteilungen 42/43/46
selbst dokumentiert, sondern erst in der nachgelagerten **Mitteilung 47 (16.12.2024)**.
Ein Datenmodell, das nur „Mitteilung → Dokument → gültig ab" abbildet, würde für diese
Dokumente ein falsches Gültigkeitsdatum führen.

### Abgrenzung nach oben: kein Zwischenstand zwischen 54 und dem Stichtag

Geprüft wurden alle Mitteilungen mit Nummer > 54. Ergebnis: **keine** davon verändert
den Stand zum 01.04.2026.

* **Mitteilung 55** (02.02.2026) — reine *Konsultation* für den Umsetzungstermin
  01.10.2026. Konsultationsfassungen sind nicht verbindlich.
* **Mitteilung 56** (01.04.2026) — verbindliche Veröffentlichung, aber ausdrücklich
  „verbindlich ab dem **01.10.2026**". Sie erscheint am Stichtag, gilt aber erst ein
  halbes Jahr später. Sie ist damit für den 01.04.2026 **Negativbeleg** und zugleich
  die beste Quelle für die Nachfolgerspalte.
* **Mitteilung 57** (31.07.2026) — Konsultation für 01.04.2027.

Die Nummernfolge 54 → 55 → 56 → 57 ist lückenlos; es gibt keine unbemerkte
Ad-hoc-Mitteilung im Zeitraum. Mitteilung 58 existiert nicht (HTTP 404).

### Validitätsbilanz

| Status | Anzahl | Bedeutung |
|---|---|---|
| **BESTÄTIGT** | 24 | Mitteilung 54 nennt das Dokument und sagt wörtlich „verbindlich ab dem 01.04.2026" |
| **WAHRSCHEINLICH** | 33 | Letzte verbindliche Veröffentlichung liegt vor dem Stichtag, keine Ablösung gefunden — aber **keine Quelle bestätigt den 01.04.2026 ausdrücklich** |
| **UNGEKLÄRT** | 5 | Version am Stichtag nicht bestimmbar |
| **ENTFALLEN (belegt)** | 6 | ausdrückliche Beendigung/Obsoleszenz in der Quelle |
| **nicht existent am Stichtag** | 1 | Codeliste der Verwendungszwecke (erst ab 01.10.2026) |

Die 33 WAHRSCHEINLICH-Einträge sind der eigentliche Befund: **für die Mehrheit des
geltenden Bestands existiert kein Dokument, das seine Gültigkeit am 01.04.2026
ausdrücklich bestätigt.** Gültigkeit entsteht durch Fortschreibung („zuletzt
veröffentlicht, nicht abgelöst"), nicht durch Bestätigung. Das ist kein Mangel der
Recherche, sondern die Funktionsweise des Änderungsmanagements — und es ist genau die
Semantik, die `get_effective()` später abbilden muss.

### Wesentliche Unsicherheiten

1. **Fünf Formate ungeklärt** (CONTRL MIG, ORDCHG MIG, INSRPT AHB, SSQNOT AHB, plus
   Verzeichnisdienst API) — siehe Abschnitt E.
2. **Ein Quellwiderspruch** bei PlannedResourceScheduleDocument (M48 konsultiert 1.1f,
   M51 veröffentlicht 1.0f).
3. Die Vorgängerkette reicht nur bis Mitteilung 41 (03.04.2024) zurück; ältere
   Vorgänger sind bewusst nicht recherchiert (siehe Abschnitt F, Methodik).

---

## B. Methodik und Abgrenzung

**Ebene 1 (aktueller Stand)** wurde für alle Formate zuerst durchgeführt: Mitteilung 54
als Primärquelle, ergänzt um die Mitteilungen 55/56/57 zur Abgrenzung nach oben und um
die lokal vorliegende PID 3.3 als Existenz- und Relevanznachweis.

**Ebene 2 (gezielte Historie)** wurde ausschließlich für die Formate gezogen, die
Ebene 1 nicht eindeutig auflöste. Belegquelle war jeweils die letzte verbindliche
Veröffentlichung (Mitteilungen 51, 46, 43, 42, 41) plus die Sondermitteilungen 47, 49
und 50, die Gültigkeitsdaten verschieben.

**Ehrliche Einschränkung zur Methodik:** Die Ebene-2-Recherche wurde in Teilen als
chronologischer Durchlauf über die Mitteilungen 53 → 41 ausgeführt statt strikt
formatbezogen. Das Ergebnis ist davon nicht betroffen — die belegten Versionen und
Quellen sind dieselben —, aber der Weg dorthin war breiter als nötig. Nicht gelesen
wurden Mitteilungen mit Nummer < 41; die Rückwärtssuche wurde beendet, sobald jedes
Format ein Ergebnis hatte.

**Nicht verfügbare Quelle:** `bdew-mako.de` liefert HTTP 403 (Zugriffsschutz). Die
ergänzende BDEW/EDI@Energy-Sicht konnte daher nicht herangezogen werden. Genau die
fünf UNGEKLÄRT-Fälle wären dort vermutlich auflösbar.

---

## C. Master-Formatliste — Stand zum 01.04.2026

Sparte „Beide" heißt: die Quelle führt das Dokument spartenübergreifend, ohne
Sparten-Suffix im Namen.

### C.1 EDIFACT — Nachrichtenformate

| ID | Format / Dokumenttyp | Sparte | Marktprozess (belegt) | Version 01.04.2026 | gültig ab | Quelle Mitteilung | Vorgänger | Nachfolger | Validität |
|---|---|---|---|---|---|---|---|---|---|
| 1 | UTILMD AHB Gas | Gas | GeLi Gas 2.0 | **1.1** | 01.04.2026 | **54** | — (n. rech.) | 1.2 (M56) | BESTÄTIGT |
| 2 | UTILMD MIG Gas | Gas | GeLi Gas 2.0 | **G1.1** | 01.04.2026 | **54** | — (n. rech.) | G1.2 (M56) | BESTÄTIGT |
| 3 | UTILMD AHB Strom | Strom | LFW24, GPKE, WiM, Netzbetreiberwechsel | **2.1** | 06.06.2025 | 46 (+47) | 2.0 (M42) | 2.2 (M56) | WAHRSCHEINLICH |
| 4 | UTILMD MIG Strom | Strom | LFW24, GPKE, WiM | **S2.1** | 06.06.2025 | 46 (+47) | S2.0 (M42) | S2.2 (M56) | WAHRSCHEINLICH |
| 5 | COMDIS AHB | Beide | Rechnungsprüfung | **1.0h** | 01.04.2026 | **54** | 1.0g (M51) | — | BESTÄTIGT |
| 6 | COMDIS MIG | Beide | Rechnungsprüfung | **1.0g** | 01.04.2026 | **54** | 1.0f (M51) | — | BESTÄTIGT |
| 7 | INVOIC AHB | Beide | Abrechnung | **1.0a** | 01.04.2026 | **54** | 1.0 (M51) | 1.0b (M56) | BESTÄTIGT |
| 8 | INVOIC MIG | Beide | Abrechnung | **2.8e** | 01.10.2025 | 51 | 2.8d (M42) | — | WAHRSCHEINLICH |
| 9 | MSCONS AHB | Beide | Messwerte | **3.1g** | 01.04.2026 | **54** | 3.1f (M46) | 3.2 (M56) | BESTÄTIGT |
| 10 | MSCONS MIG | Beide | Messwerte | **2.4c** | 24.10.2023 | 46 (Hinweis) | — (n. rech.) | 2.5 (M56) | WAHRSCHEINLICH |
| 11 | ORDERS AHB | Beide | Bestellung, Sperren, MaBiS | **1.1a** | 01.04.2026 | **54** | 1.1 (M51) | 1.1b (M56) | BESTÄTIGT |
| 12 | ORDERS MIG | Beide | Bestellung | **1.4b** | 01.10.2025 | 51 | 1.4a (M46) | 1.4c (M56) | WAHRSCHEINLICH |
| 13 | ORDRSP AHB | Beide | Auftragsantwort | **1.1a** | 01.04.2026 | **54** | 1.1 (M51) | 1.1b (M56) | BESTÄTIGT |
| 14 | ORDRSP MIG | Beide | Auftragsantwort | **1.4b** | 01.04.2026 | **54** | 1.4a (M51) | 1.4c (M56) | BESTÄTIGT |
| 15 | PARTIN AHB | Beide | Marktpartnerstammdaten | **1.0f** | 01.04.2026 | **54** | 1.0e (M46) | 1.1 (M56) | BESTÄTIGT |
| 16 | PARTIN MIG | Beide | Marktpartnerstammdaten | **1.0f** | 01.04.2026 | **54** | 1.0e (M46) | 1.1 (M56) | BESTÄTIGT |
| 17 | REMADV AHB | Beide | Zahlungsavis | **1.0a** | 01.04.2026 | **54** | 1.0 (M51) | — | BESTÄTIGT |
| 18 | REMADV MIG | Beide | Zahlungsavis | **2.9e** | 01.04.2026 | **54** | 2.9d (M51) | — | BESTÄTIGT |
| 19 | APERAK AHB | Beide | Anerkennungs-/Fehlermeldung | **1.0** | 01.10.2025 | 51 | CONTRL/APERAK AHB 2.4a (M46) | 1.1 (M56) | WAHRSCHEINLICH |
| 20 | APERAK MIG | Beide | Anerkennungs-/Fehlermeldung | **2.1i** | 06.06.2025 | 42 (+47) | — (n. rech.) | 2.2 (M56) | WAHRSCHEINLICH |
| 21 | CONTRL AHB | Beide | Syntaxfehlermeldung | **1.0** | 01.10.2025 | 51 | CONTRL/APERAK AHB 2.4a (M46) | 1.0a (M57, Konsult.) | WAHRSCHEINLICH |
| 22 | CONTRL MIG | Beide | Syntaxfehlermeldung | **ungeklärt** | — | keine (M40–57) | — | 2.0c (M57, Konsult.) | **UNGEKLÄRT** |
| 23 | IFTSTA AHB | Beide | Statusmeldung, Sperren, MaBiS | **2.0h** | 01.10.2025 | 51 | 2.0g (M46) | 2.1 (M56) | WAHRSCHEINLICH |
| 24 | IFTSTA MIG | Beide | Statusmeldung | **2.0g** | 01.10.2025 | 51 | 2.0f (M42) | 2.1 (M56) | WAHRSCHEINLICH |
| 25 | PRICAT AHB | Beide | Preisblatt | **2.0f** | 01.10.2025 | 51 | 2.0e (M42) | 2.1 (M56) | WAHRSCHEINLICH |
| 26 | PRICAT MIG | Beide | Preisblatt | **2.0e** | 01.10.2025 | 51 | 2.0d (M42) | 2.1 (M56) | WAHRSCHEINLICH |
| 27 | QUOTES AHB | Beide | Angebot | **1.1** | 01.10.2025 | 51 | 1.0 (M42) | 1.1a (M56) | WAHRSCHEINLICH |
| 28 | QUOTES MIG | Beide | Angebot | **1.3b** | 01.10.2025 | 51 | 1.3a (M42) | 1.3c (M56) | WAHRSCHEINLICH |
| 29 | REQOTE AHB | Beide | Anfrage | **1.1** | 01.10.2025 | 51 | 1.0a (M46) | 1.2 (M56) | WAHRSCHEINLICH |
| 30 | REQOTE MIG | Beide | Anfrage | **1.3c** | 01.10.2025 | 51 | 1.3b (M46) | **keiner** (s. E.2) | WAHRSCHEINLICH |
| 31 | ORDCHG AHB | Beide | Stornierung Sperr-/Bestellauftrag | **1.0a** | 06.06.2025 | 46 (+47) | 1.0 (M42) | 1.1 (M56) | WAHRSCHEINLICH |
| 32 | ORDCHG MIG | Beide | Stornierung | **ungeklärt** | — | keine (M40–57) | — | 1.2 (M56) | **UNGEKLÄRT** |
| 33 | UTILTS AHB | Beide | GPKE Teil 3, Berechnungsformel/Zählzeiten | **1.0** | 06.06.2025 | 46 (+47) | AHB Berechnungsformel 1.0g + AHB Definitionen 1.1b (M42) | 1.1 (M56) | WAHRSCHEINLICH |
| 34 | UTILTS MIG | Beide | GPKE Teil 3 | **1.1e** | 06.06.2025 | 46 (+47) | 1.1d (M42) | — | WAHRSCHEINLICH |
| 35 | INSRPT AHB | **Beide** | WiM Strom Teil 2 / WiM Gas Kap. C 2.3 — Störungsbehebung | **ungeklärt** | — | keine (M40–57) | — | — | **UNGEKLÄRT** |
| 36 | SSQNOT AHB | **Gas** | Mehr-/Mindermengen SLP + RLP | **ungeklärt** | — | keine (M40–57) | — | — | **UNGEKLÄRT** |

### C.2 Übergreifende Regelwerke

| ID | Dokumenttyp | Sparte | Version 01.04.2026 | gültig ab | Mitteilung | Vorgänger | Nachfolger | Validität |
|---|---|---|---|---|---|---|---|---|
| 37 | Allgemeine Festlegungen | Beide | **6.1c** | 01.04.2026 | **54** | 6.1b (M46) | 6.1d (M56) | BESTÄTIGT |
| 38 | Anwendungsübersicht der Prüfidentifikatoren (PID) | Beide | **3.3** | 01.04.2026 | **54** | 3.2 (M51), 3.1 (M46), 3.0 (M42) | 4.0 (M56) | BESTÄTIGT |
| 39 | Entscheidungsbaum-Diagramme und Codelisten (EBD) | Beide | **4.2** | 01.04.2026 | **54** | 4.1 (M51), 4.0b (M46), 4.0a (M43), 4.0 (M42) | 4.3 (M56) | BESTÄTIGT |
| 40 | API-Guideline | Beide | **1.0a** | 06.06.2025 | 46 (+47) | 1.0 (M42) | 1.0b (M56) | WAHRSCHEINLICH |
| 41 | BDEW-Anwendungshilfe „Prozesse zur Änderung der Technik an Lokationen" | Strom | o. Versionsangabe | 01.10.2025 | 51 (Hinweis) | — | — | WAHRSCHEINLICH |

### C.3 Codelisten

| ID | Codeliste | Sparte | Version 01.04.2026 | gültig ab | Mitteilung | Vorgänger | Nachfolger | Validität |
|---|---|---|---|---|---|---|---|---|
| 42 | Codeliste der OBIS-Kennzahlen und Medien | Beide | **2.5c** | 01.04.2026 | **54** | — (n. rech.) | — | BESTÄTIGT |
| 43 | Codeliste der Konfigurationen | Beide | **1.3c** | 01.10.2025 | 51 | 1.3b (M46), 1.3 (M42) | 1.4 (M56) | WAHRSCHEINLICH |
| 44 | Codeliste der Artikelnummern und Artikel-ID | Beide | **5.6** | **01.09.2025** (Sondertermin) | 51 (Hinweis) | — (n. rech.) | 5.7 (M57, Konsult.) | WAHRSCHEINLICH |
| 45 | Codeliste der Verwendungszwecke | Beide | **existiert nicht** | 01.10.2026 | 56 | — | — | **n. existent am Stichtag** |

Zu ID 44: Mitteilung 51 legt ausdrücklich fest, dass diese Codeliste abweichend
„bereits zum 1. September 2025 umzusetzen" ist — Begründung: MsbG-Anpassungen mit
Wirkung der neuen Artikel-IDs zum 01.01.2026. Ein Beispiel für einen vom regulären
Zyklus abweichenden Umsetzungstermin innerhalb derselben Mitteilung.

### C.4 XML-Datenformate (Redispatch 2.0 / Netzkapazität)

Jeder Dokumenttyp erscheint in drei Ausprägungen: **AWT** (Anwendungshandbuch/
Anwendungsübersicht), **FB** (Formatbeschreibung), **XSD** (Schema). Die Versionen
laufen synchron.

| ID | Dokumenttyp | Version 01.04.2026 | gültig ab | Mitteilung | Vorgänger | Nachfolger | Validität |
|---|---|---|---|---|---|---|---|
| 46 | AcknowledgementDocument (AWT/FB/XSD) | **1.0g** | 01.04.2026 | **54** | 1.0f (M51), 1.0e (M41) | — | BESTÄTIGT |
| 47 | ActivationDocument (AWT/FB/XSD) | **1.1f** | 01.04.2026 | **54** | 1.1e (M51), 1.1d (M46, ausgesetzt per M49) | 1.1g (M57, Konsult.) | BESTÄTIGT |
| 48 | Kaskade (AWT/FB/XSD) | **1.0** | 01.04.2026 | **54** | — (neu) | — | BESTÄTIGT |
| 49 | Änderungshistorie XML-Datenformate | Stand 01.10.2025 | 01.04.2026 | **54** | M51, M46, M41 | M57 (Konsult.) | BESTÄTIGT |
| 50 | PlannedResourceScheduleDocument (AWT/FB/XSD) | **1.0f** (str.) | 01.10.2025 | 51 | 1.0e (M46, ausgesetzt per M49), 1.0d (M41) | — | WAHRSCHEINLICH |
| 51 | Stammdaten (AWT/FB/XSD) | **1.4b** | 01.10.2025 | 51 | 1.4a (M46, ausgesetzt per M49), 1.4 (M41) | — | WAHRSCHEINLICH |
| 52 | NetworkConstraintDocument (AWT/FB/XSD) | **1.1b** | 01.10.2025 | 51 | 1.1a (M41) | — | WAHRSCHEINLICH |
| 53 | Kostenblatt (AWT/FB/XSD) | **1.0d** | 01.10.2025 | 51 | 1.0c (M41) | — | WAHRSCHEINLICH |
| 54 | StatusRequest_MarketDocument (AWT/FB/XSD) | **1.1** | 01.10.2025 | 51 | — (n. rech.) | — | WAHRSCHEINLICH |
| 55 | Unavailability_MarketDocument (AWT/FB/XSD) | **1.1b** | 01.10.2025 | 51 | 1.1a (M41) | — | WAHRSCHEINLICH |

### C.5 Übertragungsweg, Verzeichnisdienst, API

| ID | Dokument | Version 01.04.2026 | gültig ab | Mitteilung | Vorgänger | Nachfolger | Validität |
|---|---|---|---|---|---|---|---|
| 56 | Regelungen zum Übertragungsweg (RzÜ) | **1.9** | 01.10.2025 | 51 | 1.8 (M41) | 1.10 (M56) | WAHRSCHEINLICH |
| 57 | Regelungen zum Übertragungsweg für AS4 | **2.5** | 01.04.2026 | **54** | 2.4 (M51), 2.3 (M46), 2.2 (M41) | 2.6 (M56) | BESTÄTIGT |
| 58 | AS4-Profil | **1.1 v13** | 04.04.2025 (RzÜ von M47 ausgenommen) | 46 | — (n. rech.) | 1.2 (M56) | WAHRSCHEINLICH |
| 59 | Regelungen zum Übertragungsweg für API-Webdienste | **1.2** | 01.10.2025 | 51 | 1.1 (M46), 1.0 (M43) | 1.3 (M57, Konsult.) | WAHRSCHEINLICH |
| 60 | Regelungen zum Verzeichnisdienst | **1.1** | 01.10.2025 | 51 | 1.0 (M46) | — | WAHRSCHEINLICH |
| 61 | Verzeichnisdienst API | **ungeklärt** (1.0 oder 1.1) | — | 46 / 48 | 1.0 (M46) | — | **UNGEKLÄRT** |
| 62 | API-Webdienste zur Ermittlung der MaLo-ID | **1.0.0** | 06.06.2025 | 43 (+47) | — (neu) | Release 2.0.0 **nicht veröffentlicht** (M56) | WAHRSCHEINLICH |

### C.6 Explizit entfallen / abgelöst (mit Beleg)

Nach §5 des Auftrags nur bei ausdrücklicher Evidenz in der Quelle.

| ID | Dokument | Ergebnis | Wortlaut / Beleg | Quelle |
|---|---|---|---|---|
| 63 | HKNR AHB 2.3e | ENTFALLEN | „wird beendet zum 03.04.2025" | M42 |
| 64 | ORDERS/ORDRSP AHB MaBiS 2.2d | ENTFALLEN | „wird beendet zum 03.04.2025" | M42 |
| 65 | REQOTE/QUOTES/ORDERS/ORDRSP/ORDCHG AHB 2.3 | ENTFALLEN | „wird beendet zum 03.04.2025" | M42 |
| 66 | UTILMD AHB MaBiS 4.1b | ENTFALLEN | „wird beendet zum 03.04.2025" | M42 |
| 67 | MSCONS MIG 2.4d | ENTFALLEN, nie in Kraft | „wird die Version der MSCONS MIG 2.4d obsolet" | M46 |
| 68 | Beschaffungsvorbehalt (XML) | ENTFALLEN | „verlieren alle Versionen … ihre Gültigkeit bzw. Grundlage" | M41 |
| 69 | Beschaffungsanforderung_energetischerAusgleich (XML) | ENTFALLEN | „verlieren alle Versionen … ihre Gültigkeit bzw. Grundlage" | M41 |

**Nicht als entfallen klassifiziert**, obwohl in aktuellen Mitteilungen nicht mehr
genannt: `CONTRL/APERAK AHB 2.4a` und `INVOIC/REMADV AHB 2.5d`. Beide wurden in
Mitteilung 51 durch je zwei getrennte Handbücher ersetzt (APERAK AHB 1.0 + CONTRL AHB
1.0 bzw. INVOIC AHB 1.0 + REMADV AHB 1.0). Die Quelle sagt das aber **nicht wörtlich** —
die Ablösung ist aus der Namensstruktur erschlossen, nicht belegt. Einstufung daher
**WAHRSCHEINLICH abgelöst**, nicht ENTFALLEN.

---

## D. Historische Kette und Gültigkeitsmechanik

### D.1 Drei Mechanismen, die Gültigkeit erzeugen

Die Recherche zeigt drei unterschiedliche Wege, auf denen ein Dokument am 01.04.2026
gilt. Für `get_effective()` sind das drei verschiedene Fälle, nicht einer:

**(1) Ausdrückliche Bestätigung** — Mitteilung 54 nennt das Dokument und sagt
„verbindlich ab dem 01.04.2026". 24 Einträge. Nur hier ist der Stichtag belegt.

**(2) Fortschreibung** — Das Dokument wurde zuletzt in einer früheren Mitteilung
verbindlich veröffentlicht und seither nicht abgelöst. Es gilt weiter, ohne dass eine
Quelle das für den Stichtag ausspricht. 33 Einträge. **Der Regelfall.**

**(3) Verschobene Gültigkeit** — Das Dokument wurde veröffentlicht, sein
Gültigkeitsbeginn aber durch eine *spätere, separate* Mitteilung verändert:

| Verschiebung | betroffen | Quelle |
|---|---|---|
| 04.04.2025 → **06.06.2025** | alle Dokumente aus M42, M43, M46 (außer RzÜ) | **M47** (16.12.2024) |
| 06.06.2025 → **01.10.2025** (ausgesetzt) | Redispatch-XML: ActivationDocument 1.1d, PlannedResourceScheduleDocument 1.0e, Stammdaten 1.4a | **M49** (13.03.2025) |
| AES-128-GCM-Pflicht ausgesetzt bis 01.10.2025 | RzÜ, S/MIME Gas | **M50** (26.03.2025), zuvor **M45** |
| Sondertermin **01.09.2025** statt 01.10.2025 | Codeliste der Artikelnummern 5.6 | **M51** (Hinweis) |
| Sondertermin **01.08.2025** | Netzbetreiberwechsel-Anpassungen *innerhalb* UTILMD Strom 2.1 | **M46** (Hinweis) |

Der letzte Fall ist der schärfste Beleg gegen ein Modell „ein Dokument = ein
Gültigkeitsdatum": Mitteilung 46 stellt fest, dass die Netzbetreiberwechsel-Anpassungen
**in den ab 04.04.2025 gültigen UTILMD-Dokumenten** enthalten sind, aber „erst ab dem
01.08.2025 gültig" werden — „und sind entsprechend gekennzeichnet". **Innerhalb eines
Dokuments gelten Teile ab unterschiedlichen Daten.**

### D.2 Der CTA/COM-Fall im Licht der Quellen

Mitteilung 55 bestätigt den bereits bekannten CTA/COM-Fall als Quellenlage: „Das in der
Konsultation des ‚Konzepts zur Nutzung der Kontaktinformationen des Senders in den
EDI@Energy Nachrichtentypen' beschlossene Vorgehen wurde in den Datenformaten
umgesetzt." Das zugrundeliegende Konzeptdokument wurde in **Mitteilung 52** als eigenes
Dokument konsultiert („Konzept zur Nutzung der Kontaktinformationen des Senders in den
EDI@Energy Nachrichtentypen 1.0", Konsultationsfrist bis 15.10.2025).

Damit ist die Beziehungskette belegt:

```text
Konzeptdokument (M52, konsultiert bis 15.10.2025)
  → Umsetzung in den Datenformaten (M55, Konsultationsfassungen)
  → verbindliche Veröffentlichung (M56, ab 01.10.2026)
  → betrifft in AHB Gas 1.1 → 1.2 nur bestimmte PIs
```

Ein Konzeptdokument ist damit ein eigener regulatorischer Artefakttyp: es ist selbst
kein Format, steuert aber Änderungen über mehrere Formate hinweg. Ebenso in M52
konsultiert: „Konzept zur Weiterentwicklung der Berechnungsformel, der
Lokationsbündelstruktur und der Zählzeiten 1.0". Mitteilung 53 (01.09.2025) besteht
sogar **ausschließlich** aus einem solchen Konzept („Konzept zur Nutzung und
Veröffentlichung von API-Webdiensten") — sie veröffentlicht kein einziges Format.

### D.3 Teilweise Ersetzung ist der Normalfall, nicht die Ausnahme

Mehrere Belege gegen „neue Version = vollständiger Ersatz":

* **MSCONS MIG 2.4d** (M46): Die Version enthielt „bis auf die Löschung der
  Segmentausprägung … keine weiteren Änderungen". Weil diese eine Änderung fachlich
  falsch war (Gas braucht das Segment weiter), wurde die **gesamte Version verworfen**
  und die ältere 2.4c blieb gültig. Eine Version kann also rückwirkend entfallen,
  ohne dass ein Nachfolger existiert.
* **UTILMD Strom 2.1** (M46): enthält Inhalte mit zwei verschiedenen
  Gültigkeitsbeginnen (04.04.2025 und 01.08.2025), im Dokument gekennzeichnet.
* **EBD 4.4** (M57): „in einzelnen EBD [wurde] der Antwortcode ‚A99' entfernt. Dies
  wurde in den EDIFACT-Dokumenten UTILMD und ORDRSP … **nicht nachgezogen**." —
  Dokumente desselben Stands können untereinander inkonsistent sein, und die BNetzA
  weist darauf ausdrücklich hin.
* **Antwortcodes A90/A96/A99** (M55): „Für die laufende Konsultation wird die
  befristete Nutzungsmöglichkeit … um ein halbes Jahr verlängert." — Einzelne
  Codewerte haben eigene, befristete und verlängerbare Gültigkeitszeiträume,
  unabhängig von der Dokumentversion.

---

## E. Lücken und Unsicherheiten

### E.1 Die fünf UNGEKLÄRT-Fälle

| Format | Was belegt ist | Was fehlt |
|---|---|---|
| **CONTRL MIG** | Existiert: M57 konsultiert Version 2.0c für 01.04.2027. CONTRL AHB 1.0 ist ab 01.10.2025 verbindlich (M51). Relevanz belegt: M42 — CONTRL entfällt ab 04.04.2025 als Empfangsbestätigung, „etwaige Syntaxfehlermeldungen per CONTRL sind davon ausgenommen". | Die am 01.04.2026 gültige MIG-Version. In keiner Mitteilung 40–57 veröffentlicht. |
| **ORDCHG MIG** | Existiert: M55/M56 nennen Version 1.2 (ab 01.10.2026). ORDCHG AHB 1.0a gilt ab 06.06.2025. | Die Vorgängerversion. In keiner Mitteilung 40–57 veröffentlicht. |
| **INSRPT AHB** | Relevanz **belegt** über PID 3.3 (gültig ab 01.04.2026): 22 Zeilen der Tabelle 1 mit AHB-Wert „INSRPT AHB", Sparte **Strom** (Lfd. Nr. 31320–31430, WiM Strom Teil 2 „Störungsbehebung in der Messstelle") **und Gas** (Lfd. Nr. 871–880, WiM Gas Kap. C 2.3). Die dort genannten **Prüfidentifikatoren** sind 23001, 23003, 23004, 23005, 23008, 23009, 23011, 23012. Tupel ZO-T12 (SG8 LOC+172) ist auf INSRPT definiert. | Version und veröffentlichende Mitteilung. |
| **SSQNOT AHB** | Relevanz **belegt** über PID 3.3: 2 Zeilen (Lfd. Nr. 12170/12180) mit den **Prüfidentifikatoren 70095** (Mehr-/Mindermengenmeldung SLP) und **70096** (RLP), Prozess „Prozesse zur Ermittlung und Abrechnung von Mehr-/Mindermengen Strom und Gas", Tupel ZO-T19 (SG39 NAD+ZSH, „Mehrmindermengenmeldung Gas Netzkonto"). | Version und veröffentlichende Mitteilung. |

> **Korrektur gegenüber der ersten Fassung dieses Befunds.** Dort waren 31320/31430
> bzw. 12170/12180 als Prüfidentifikatoren ausgewiesen. Das war falsch: Spalte 0 der
> PID-Tabelle 1 heißt **„Lfd. Nr."**, der Prüfidentifikator steht in **Spalte 3**. Die
> zellgenaue Prüfung (Abschnitt I.3) hat das aufgedeckt; die Zeilen- und Prozessbezüge
> selbst waren korrekt.
| **Verzeichnisdienst API** | M46 veröffentlicht „Verzeichnisdienst API" ohne Versionsnummer; M48 konsultiert Version 1.1; M51 nennt das Dokument in der verbindlichen Liste **nicht**. | Ob 1.1 je verbindlich veröffentlicht wurde, oder ob 1.0 aus M46 weitergilt. |

Diese fünf sind **nicht** als entfallen zu werten (§5). Bei INSRPT und SSQNOT belegt
die PID 3.3 sogar das Gegenteil: beide sind zum Stichtag produktiv in Gebrauch.

### E.2 Quellwidersprüche und Auffälligkeiten

1. **PlannedResourceScheduleDocument** — M48 (Konsultation, 03.02.2025) nennt
   „AWT 1.1f / FB 1.1f", M51 (verbindliche Veröffentlichung, 01.04.2025) nennt
   „1.0f". Nicht auflösbar ohne Blick ins Dokument. In C.4 als „1.0f (str.)" geführt,
   weil M51 die verbindliche Quelle ist.
2. **REQOTE MIG 1.3d** — in M55 konsultiert, in M56 **nicht veröffentlicht**. Der
   Nachfolger existiert also als Konsultationsfassung, aber nicht als verbindliche
   Version. Beleg dafür, dass Konsultation ≠ Veröffentlichung und dass ein
   Datenmodell beide Zustände trennen muss.
3. **API-Webdienste Release 2.0.0** — in M55 konsultiert, in M56 ausdrücklich
   ausgeschlossen: „sind nicht Bestandteil dieser Veröffentlichung". M57 ergänzt, dass
   diese Anpassungen dennoch als Konsultationsergebnis gelten und keine weiteren
   Rückmeldungen erwartet werden. Ein Zwischenzustand, den weder „gültig" noch
   „entfallen" korrekt beschreibt.
4. **Konsultationsfassung ≠ nicht verbindlich** — AHB Gas 1.1, MIG Gas G1.1 und PID
   3.3 tragen laut vorhandenem `backend/data/regulatory/README.md` auf dem Deckblatt
   den Vermerk „Konsultationsfassung", werden von Mitteilung 54 aber als ab 01.04.2026
   anzuwenden geführt. Die Dokumenteigenschaft widerspricht dem regulatorischen Status.
5. **PID 3.3 liegt als Anlage unter Mitteilung 52**, wird aber von Mitteilung 54
   verbindlich gestellt. Anlagenort und Geltungsquelle fallen auseinander.

### E.3 Bewusst nicht recherchiert

* Vorgängerversionen älter als Mitteilung 41 (03.04.2024) — in C.x als „(n. rech.)"
  markiert. Betrifft u. a. den Vorgänger von UTILMD AHB/MIG Gas 1.1/G1.1 und von
  MSCONS MIG 2.4c (veröffentlicht 24.10.2023).
* `bdew-mako.de` als ergänzende Quelle (HTTP 403).
* Inhaltliche Prüfung der Dokumente selbst — dieser Befund arbeitet auf Ebene
  Dokument/Version, nicht auf Ebene Segment/PI/Code.

---

## F. Vollständigkeitsprüfung (Regel 8)

| Prüfung | Ergebnis |
|---|---|
| Einträge Master-Formatliste (C.1–C.6) | **69** |
| davon mit explizitem Prüfergebnis | **69** |
| Einträge im Stand-Bericht (Abschnitt C = Effective-State-Sicht) | **69** |
| **Abweichung** | **0** |

Aufschlüsselung: 36 EDIFACT (C.1) + 5 Regelwerke (C.2) + 4 Codelisten (C.3) +
10 XML (C.4) + 7 Übertragungsweg/API (C.5) + 7 entfallen (C.6) = 69.

Abdeckung der Mindest-Prüfliste aus §3.3:

* **A. EDIFACT** — APERAK ✓, CONTRL ✓ (AHB belegt, MIG ungeklärt), IFTSTA ✓, INVOIC ✓,
  MSCONS ✓, ORDERS ✓, ORDRSP ✓, UTILMD ✓ (Gas **und** Strom). Zusätzlich durch offene
  Recherche gefunden: COMDIS, PARTIN, REMADV, PRICAT, QUOTES, REQOTE, ORDCHG, UTILTS,
  INSRPT, SSQNOT.
* **B. Fachliche Dokumentation** — AHB ✓, MIG ✓, PID ✓, Allgemeine Festlegungen ✓,
  EBD ✓, Übertragungswege ✓. Zusätzlich: API-Guideline, BDEW-Anwendungshilfe,
  Konzeptdokumente (D.2).
* **C. Codelisten** — EBD-Codelisten ✓, OBIS/Medien ✓, Konfigurationen ✓,
  Artikelnummern/Artikel-ID ✓, Verwendungszwecke ✓ (nicht existent am Stichtag).
* **D. XML** — AcknowledgementDocument ✓, ActivationDocument ✓, Kaskade ✓. Zusätzlich:
  PlannedResourceScheduleDocument, Stammdaten, NetworkConstraintDocument, Kostenblatt,
  StatusRequest_MarketDocument, Unavailability_MarketDocument, Änderungshistorie,
  Beschaffungsvorbehalt (entfallen), Beschaffungsanforderung (entfallen).
* **E. Weitere Artefakte** — RzÜ ✓, RzÜ AS4 ✓, AS4-Profil ✓, RzÜ API-Webdienste ✓,
  Verzeichnisdienst ✓, Verzeichnisdienst API ✓, API-Webdienste MaLo-ID ✓.

Kein Format der Mindestliste ist ohne Ergebnis geblieben.

---

## G. Empfehlungen für die nächsten Schritte

Die Recherche liefert sechs konkrete Anforderungen an das Datenmodell. Alle sind
**Befunde, keine Modellentscheidungen** — die Entscheidung steht noch aus.

**1. Ein regulatorischer Stand ist eine Überlagerung, kein Snapshot.**
Der 01.04.2026-Stand entsteht aus fünf Mitteilungen von 2024 und 2025. Ein Modell
„RegulatoryVersion → alle Dokumente" muss abbilden können, dass ein Dokument aus
Mitteilung 46 und eines aus Mitteilung 54 gleichzeitig gelten.

**2. Gültigkeitsbeginn ist ein eigenes Objekt, kein Feld am Dokument.**
Mitteilung 47 verschiebt nachträglich das Datum von Dokumenten aus drei anderen
Mitteilungen; M49 setzt einen Formatwechsel ganz aus; M51 legt für eine Codeliste einen
Sondertermin fest. Ein Feld `gueltig_ab` am Dokument kann das nicht tragen — nötig ist
ein Änderungsereignis mit eigener Quelle.

**3. Validitätsstatus muss persistiert werden.**
33 von 69 Einträgen gelten durch Fortschreibung, nicht durch Bestätigung.
`get_effective()` darf nicht so tun, als wäre das dieselbe Aussagequalität. Vorschlag:
`BESTÄTIGT` / `WAHRSCHEINLICH` / `UNGEKLÄRT` als Feld an der Zuordnung
Dokument↔Stand, mit Quellenverweis.

**4. Konsultation und Veröffentlichung sind zwei Zustände.**
REQOTE MIG 1.3d und API-Release 2.0.0 existieren als Konsultationsfassung, aber nicht
als verbindliche Version. Gleichzeitig tragen AHB Gas 1.1 und PID 3.3 den Vermerk
„Konsultationsfassung" und sind verbindlich. Der Dokumentvermerk taugt nicht als
Statusquelle — der Status kommt aus der Mitteilung.

**5. Teilgültigkeit innerhalb eines Dokuments ist belegt.**
UTILMD Strom 2.1 enthält Inhalte mit zwei Gültigkeitsdaten; die EBD-Codes A90/A96/A99
haben eigene befristete Nutzungszeiträume; MSCONS MIG 2.4d wurde als Ganzes verworfen
wegen einer einzigen Änderung. Das ist die empirische Grundlage für die Delta Engine —
Granularität unterhalb der Dokumentversion ist Pflicht, nicht Kür.

**6. Konzeptdokumente sind ein eigener Artefakttyp.**
Mitteilung 53 veröffentlicht ausschließlich ein Konzept; das CTA/COM-Konzept aus
Mitteilung 52 steuert Änderungen über mehrere Formate und zwei Mitteilungen hinweg.
Ein Konzept ist kein Format, aber Ursache von Formatänderungen.

### Vorschlag für die Aufteilung der Folgeprompts

| Prompt | Inhalt | Grundlage |
|---|---|---|
| **Nächster** | Beziehungsmodell / Effective-State-Konzept — Mitteilung, Dokument, Version, Gültigkeitsereignis, Validitätsstatus als Objekte. **Konzeptphase, keine Migration.** | dieser Befund, Punkte 1–3 |
| danach | Delta-Granularität: was ändert sich zwischen AHB Gas 1.1 → 1.2 tatsächlich (PI-Ebene), belegt am konkreten CTA/COM-Fall | Punkt 5, D.3 |
| danach | Provenienz-/Quellenmodell: Mitteilung als Objekt mit URL, Datum, Typ (Konsultation/Veröffentlichung/Verschiebung) | Punkt 4, 6 |
| offen | Auflösung der fünf UNGEKLÄRT-Fälle über eine BDEW/EDI@Energy-Quelle mit Zugriff | E.1 |

---

## H. Quellenverzeichnis

Alle URLs unter
`https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_<N>/Mitteilung_Nr_<N>.html`

| Nr. | Datum | Typ | Bedeutung für diesen Befund |
|---|---|---|---|
| 41 | 03.04.2024 | Veröffentlichung (ab 01.10.2024) | XML-Basisversionen, RzÜ 1.8 / AS4 2.2; Entfall Beschaffungsvorbehalt |
| 42 | 19.06.2024 | Veröffentlichung (ab 04.04.2025) | APERAK MIG 2.1i; vier explizite Beendigungen zum 03.04.2025 |
| 43 | 03.07.2024 | Veröffentlichung (ab 04.04.2025) | API-Webdienste MaLo-ID 1.0.0, RzÜ API-Webdienste 1.0 |
| 45 | 17.09.2024 | Aussetzung | AES-128-GCM (Gas, S/MIME) |
| 46 | 01.10.2024 | Veröffentlichung (ab 04.04.2025) | UTILMD Strom 2.1/S2.1, UTILTS, ORDCHG, API-Guideline; MSCONS-MIG-2.4d-Befund |
| 47 | 16.12.2024 | **Verschiebung** | 04.04.2025 → 06.06.2025 für M42/M43/M46 (außer RzÜ) |
| 48 | 03.02.2025 | Konsultation (für 01.10.2025) | Widerspruch PlannedResourceScheduleDocument |
| 49 | 13.03.2025 | **Aussetzung** | Redispatch-XML-Formatwechsel → 01.10.2025 |
| 50 | 26.03.2025 | Aussetzung | AES-128-GCM bis 01.10.2025 |
| 51 | 01.04.2025 | Veröffentlichung (ab 01.10.2025) | zweitgrößter Beitrag zum Stichtagsstand |
| 52 | 01.08.2025 | Konsultation (für 01.04.2026) | Konzeptdokumente CTA/COM und Berechnungsformel; Anlagenort der PID 3.3 |
| 53 | 01.09.2025 | Konsultation (Konzept) | nur API-Webdienste-Konzept, kein Format |
| **54** | **01.10.2025** | **Veröffentlichung (ab 01.04.2026)** | **Primärquelle des Stichtags, 29 Dokumente** |
| 55 | 02.02.2026 | Konsultation (für 01.10.2026) | Negativbeleg; CTA/COM-Umsetzung bestätigt |
| 56 | 01.04.2026 | Veröffentlichung (ab 01.10.2026) | Negativbeleg; Nachfolgerspalte |
| 57 | 31.07.2026 | Konsultation (für 01.04.2027) | Negativbeleg; Inkonsistenz-Hinweis EBD/UTILMD |

Ergänzend: `backend/data/regulatory/PID_3_3_Konsultationsfassung_20250801.pdf`
(SHA-256 `6b4f5e36…c7139a`) als Existenz- und Relevanznachweis für INSRPT, SSQNOT,
ORDCHG, UTILTS, IFTSTA.

---

## I. Beziehungsanalyse — die elf festgelegten Kanten

Nachgereicht auf Prüfauftrag. Untersucht wird die vorgegebene Kette

```text
Mitteilung → Dokument → Dokumentversion → PID → PI → Nachricht → MIG → AHB → Codeliste → EBD
```

zuzüglich `PID → AHB` und `PID → Nachricht` — elf Kanten. Alle Belege stammen aus den
fünf lokal vorliegenden Dokumentversionen des 01.04.2026-Stands und aus den
BNetzA-Mitteilungen. Es wurde **keine** neue Formatrecherche geführt.

### I.1 Verwendete Evidenzstufen

Der Auftrag definiert D und N/A; A–C sind die Abstufungen darüber. Verwendete Lesart —
falls das intern anders belegt ist, sind die Einstufungen ohne inhaltliche Änderung
umzuetikettieren:

| Stufe | Bedeutung |
|---|---|
| **A** | Direkt und explizit im Dokument belegt, eindeutig auflösbar |
| **B** | Belegt, aber eingeschränkt — z. B. nur Dokumenttyp statt Version, oder nur eine Richtung |
| **C** | Nur indirekt erschlossen (über Dritte, Struktur, Namenskonvention) |
| **D** | Fachlich relevant/möglich, aber **nicht belastbar nachweisbar** |
| **N/A** | Beziehung existiert **fachlich nicht** |

**D und N/A sind strikt getrennt:** keine der elf Kanten ist N/A — jede ist fachlich
denkbar. N/A tritt nur bei einzelnen *Richtungen* auf (I.2, Spalte „Gegenrichtung").

### I.2 Übersicht

| # | Kante | Stufe | Belegte Richtung | Gegenrichtung | Kard. | vers.-abh. | zeit-abh. | Kante selbst versionsgebunden |
|---|---|---|---|---|---|---|---|---|
| 1 | Mitteilung → Dokument | **A** | Mitteilung → Dokument | **D** (Dokument nennt keine Mitteilung) | n:m | ja | **ja** | **ja** — Kante trägt Version + „gültig ab" |
| 2 | Dokument → Dokumentversion | **A** | beidseitig | — | 1:n | — (ist die Versionsachse) | ja | ja |
| 3 | Dokumentversion → PID | **B** | PID 3.3 *ist* eine Dokumentversion | **D** (AHB/MIG verweisen nie auf die PID) | 1:1 | ja | ja | ja |
| 4 | PID → PI | **A** | PID → PI (Tab. 1, Sp. 3) | n/a | 1:n | ja | ja | ja |
| 5 | PI → Nachricht | **B** | PI → Nachrichtentyp | **N/A** (Nachricht kennt PI nur über MIG) | n:1 | ja | ja | nein |
| 6 | Nachricht → MIG | **A** | MIG → Nachricht (Deckblatt) | A | 1:n (je Sparte) | ja | ja | **ja** — inkl. UN-Verzeichnis |
| 7 | MIG → AHB | **A**, aber **Richtung umgekehrt** | **AHB → MIG** („Stand MIG: G1.1") | **D** (MIG nennt AHB nur generisch) | n:1 | ja | ja | **ja** — Kante trägt MIG-Version |
| 8 | AHB → Codeliste | **B** | AHB → Codeliste | **N/A** | n:m | **nein** | nein | **nein** — Verweis nennt nie eine Version |
| 9 | Codeliste → EBD | **A**, aber **Richtung umgekehrt** | **EBD → Codeliste** | **D** (Codeliste → EBD nicht belegt) | n:m | nein | teilw. ja | nein |
| 10 | **PID → AHB** | **B** (Typ) / **D** (Version) | PID → AHB-*Dokumenttyp* | **N/A** (AHB nennt PID nie, 0 Treffer) | n:1 je PI | **nein** | nein | **nein** |
| 11 | PID → Nachricht | **B** | PID → Nachrichtentyp (abgeleitet) | N/A | 1:n | ja | ja | nein |

### I.3 Die Kanten im Einzelnen

**(1) Mitteilung → Dokument — A.**
Mitteilung 54 listet 29 Dokumente jeweils mit Version und erklärt sie „verbindlich ab
dem 01.04.2026". Die Kante trägt die Version, nicht der Knoten.
**n:m, nicht 1:n:** PID 3.3 liegt als Anlage unter Mitteilung 52 und wird durch
Mitteilung 54 verbindlich gestellt — dasselbe Dokument hängt an zwei Mitteilungen mit
verschiedener Rolle (Konsultation / Veröffentlichung).
**Zeitabhängig:** Mitteilung 47 ändert nachträglich das „gültig ab" von Dokumenten aus
drei anderen Mitteilungen (04.04.2025 → 06.06.2025). Die Kante ist also selbst
veränderlich.
**Gegenrichtung D:** Deckblatt und Fußzeile von AHB Gas 1.1, MIG Gas G1.1 und PID 3.3
nennen Version, Publikationsdatum und Autor — aber **keine Mitteilungsnummer**. Vom
Dokument aus ist seine Mitteilung nicht auflösbar.

**(2) Dokument → Dokumentversion — A.**
AHB Gas Deckblatt: „Version: 1.1 / Publikationsdatum: 01.10.2025", wiederholt in der
Fußzeile aller 329 Seiten. MIG: „Version: G1.1", Fußzeile aller 168 Seiten. Beidseitig
auflösbar, 1:n.

**(3) Dokumentversion → PID — B.**
Zwei Lesarten, beide geprüft:
* *Instanziierung* („die PID ist eine Dokumentversion"): **A** — PID 3.3 trägt Version
  und Publikationsdatum wie jedes andere Dokument.
* *Verweis* („eine Dokumentversion referenziert die PID"): **D** — Volltextsuche nach
  „Anwendungsübersicht der Prüfidentifikatoren" ergibt **0 Treffer im AHB Gas 1.1** und
  **0 Treffer in der MIG Gas G1.1**. Kein Dokument des Stands verweist auf die PID.
Gesamteinstufung **B**, weil die Kante nur in der Instanziierungslesart trägt.

**(4) PID → PI — A.**
Tabelle 1 der PID 3.3: 1441 extrahierte Zeilen, davon 71 Kopfzeilenwiederholungen
(je eine pro Seite 7–77) → **1370 Datenzeilen** mit **486 verschiedenen
Prüfidentifikatoren** in Spalte 3.
**Fallstrick, empirisch belegt:** Spalte 0 heißt **„Lfd. Nr."**, nicht
„Prüfidentifikator". Beide sind fünfstellige Zahlen und optisch nicht unterscheidbar.
Die erste Fassung dieses Befunds ist genau darauf hereingefallen (siehe Korrektur in
E.1). Für einen Parser heißt das: Spaltenposition ist Pflicht, Mustererkennung reicht
nicht.
Ein PI erscheint in mehreren Zeilen: PI 44112 steht in **6 Zeilen** über **3
Prozessbeschreibungen** (GeLi Gas 2.0, WiM Gas, Marktraumumstellung). Zeile → PI ist
n:1, PI → Zeile 1:n. **100 von 486 PIs** hängen an mehr als einer Prozessbeschreibung.

**(5) PI → Nachricht — B.**
Die PID hat **keine Spalte „Nachrichtentyp"**. Der Typ wird aus dem AHB-Namen der
Spalte 1 entnommen (führende Großbuchstaben: „MSCONS AHB" → MSCONS). Das ist eine
strukturelle Entnahme, kein Beleg — daher **B**, nicht A.
Stützend: **0 von 486 PIs** tragen mehr als einen AHB-Wert, die Ableitung ist also
widerspruchsfrei. Für den Teilbestand, der in einer MIG steht, ist die Kante **A**:
MIG Gas G1.1, SG6 RFF DE1154 (S. 51–53) listet 91 PIs direkt unter dem Nachrichtentyp
der MIG.
**58 der 1370 Datenzeilen** liefern keinen Nachrichtentyp: 31 Zeilen mit „--" und 27
Zeilen, die statt eines AHB einen API-Webdienst nennen.

**(6) Nachricht → MIG — A.**
MIG-Deckblatt: „UTILMD Nachrichtenbeschreibung -Gas **auf Basis UTILMD
Netzanschluss-Stammdaten UN D.11A S3**". Die Kante ist doppelt versionsgebunden — an
die MIG-Version (G1.1) *und* an das UN/EDIFACT-Verzeichnis (D.11A S3).
1:n über die Sparte: derselbe Nachrichtentyp UTILMD hat am 01.04.2026 zwei MIGs
(Gas G1.1 aus Mitteilung 54, Strom S2.1 aus Mitteilung 46).

**(7) MIG → AHB — A, aber die vorgegebene Richtung ist umgekehrt.**
Belegt ist **AHB → MIG**, versionsgenau und an genau einer Stelle: Deckblatt AHB Gas
1.1, „**Stand MIG: G1.1**". Ein Treffer im gesamten Dokument.
Die Gegenrichtung MIG → AHB ist **D**: die MIG enthält 4 Erwähnungen, alle generisch
und ohne Namen oder Version — „Die Nutzung der Codes ist den entsprechenden
Anwendungshandbüchern (= AHB) zu entnehmen" (S. 13), „Die Verwendung dieses Segments
wird im jeweiligen Anwendungshandbuch beschrieben" (S. 16, S. 56). Von der MIG aus ist
nicht auflösbar, welche AHB auf ihr aufsetzen.
**Konsequenz:** Die Kante gehört im Modell an das AHB, nicht an die MIG. Sie ist
zugleich die **einzige** der elf Kanten, die eine konkrete Fremdversion trägt.

**(8) AHB → Codeliste — B.**
Belegt, aber **nie versionsauflösend**. Zwei verschiedene Verweistypen im AHB Gas 1.1:
* **Interne Codelisten-IDs** (107 Treffer): „SG4 STS 1131 **G_0002** Codeliste Gas Nr.
  G_0002". Verweis per ID, ohne Version.
* **Externe Codelisten-Dokumente**, per Name + Kapitel, ohne Version:
  * OBIS, 27 Treffer, S. 58: „Es sind alle OBIS-Kennzahlen gem. EDI@Energy **Codeliste
    der OBIS-Kennzahlen und Medien für den deutschen Energiemarkt Kap. 4** anzugeben".
  * Konfigurationen, 17 Treffer, S. 58: „ergibt sich aus den genannten
    Messprodukt-Codes dem **Kap. 5.2 des Dokumentes „Codeliste der Konfigurationen"**".
Dass am 01.04.2026 OBIS **2.5c** und Konfigurationen **1.3c** gemeint sind, steht in
Mitteilung 54 bzw. 51 — **nicht im AHB**. Die Versionsauflösung ist ausschließlich über
den Stand möglich, nie über das Dokument.

**(9) Codeliste → EBD — A, aber die vorgegebene Richtung ist umgekehrt.**
Belegt ist **EBD → Codeliste**, z. B. EBD 4.2 S. 115: „vor der Nutzung des
elektronischen Netznutzungspreisblatts mit den entsprechenden Codes aus der **Codeliste
S_0103**. … Nach Abschluss der Prüfung der Rechnungsposition gegen die Codeliste S_0103
ist mit dem EBD E_0406 … fortzufahren." Ebenso S. 99: „müssen die Antwortcodes aus der
**externen Codeliste S_0103** genutzt werden."
Die Gegenrichtung Codeliste → EBD ist **D**: Codelisten verweisen nicht auf EBDs. Der
einzige gefundene Codelisten-Ausgangsverweis, `G_0088` → „Es ist die Codeliste G_0079
zu nutzen", ist Codeliste → Codeliste.

#### I.3.1 Verhältnis EBD ↔ Codeliste — die Belegstellen im Wortlaut

Diese Frage entscheidet, ob das Konzeptmodell hier **einen** Knoten oder **zwei** führt.
Deshalb beide Quellen wörtlich, mit Seitenangabe.

**Quelle 1 — UTILMD MIG Gas G1.1, S. 42, Bemerkungsblock zum STS-Segment**
(wortgleich wiederholt auf S. 43):

> „DE9013 Diesem Datenelement werden Codes aus den Codelisten des Dokumentes
> „Entscheidungsbaum-Diagramme" verwendet. **Jeder Entscheidungsbaum gilt als
> Codeliste.** Die relevante Codeliste wird im DE1131 angegeben. Somit sind nur die
> Codes in einem Anwendungsfall möglich, welche in dem zugehörigen Entscheidungsbaum
> aufgeführt sind.
> DE1131 des Segments ist genutzt und enthält die Codes der Entscheidungsbaumdiagramme
> **bzw.** die Codes der im Dokument Entscheidungsbaum-Diagramme enthaltenen
> Code-Tabellen, die in der Nachricht verwendet werden.
> Beispiel: `STS+E01++E15:G_0002'`"

**Quelle 2 — EBD und Codelisten 4.2, S. 24, Kapitel 2 „Aufbau des Dokumentes"**:

> „Die Gliederung des Dokumentes erfolgt in drei Ebenen. Die erste Ebene entspricht der
> jeweiligen Festlegung. Auf der zweiten Ebene erscheint der Name des
> Aktivitätsdiagramms oder, falls dieses nicht vorhanden ist, wie beispielsweise in der
> GeLi Gas, der Name des Sequenzdiagrammes. **Auf der dritten Ebene befinden sich das
> EBD oder die Codeliste pro Anwendungsfall.** …
> **Da sich das Dokument noch im Aufbau befindet, enthält es neben den EBD auch
> Codelisten pro Anwendungsfall.** Dies ist nötig, da die Überführung der Antwortcodes
> aus den Nachrichtenbeschreibungen in die **externen Codelisten (die sich in EDB [sic]
> und Codelisten pro Anwendungsfall unterteilen/aufteilen)** für einen Nachrichtentypen
> vollständig erfolgt."

**Auswertung — keine Identität, aber auch keine bloße Alternative.** Quelle 2 löst den
scheinbaren Widerspruch auf: „externe Codeliste" ist der **Obertyp**, der sich „in EBD
und Codelisten pro Anwendungsfall **unterteilt/aufteilt**". Damit gilt:

* Die MIG-Aussage „Jeder Entscheidungsbaum gilt als Codeliste" ist **keine
  Gleichsetzung zweier Knoten**, sondern eine Untertyp-Aussage aus Sicht des
  Referenzslots DE1131: ein EBD *zählt dort als* externe Codeliste. Das „gilt als"
  ist wörtlich so formuliert — nicht „ist".
* Die EBD-Aussage „das EBD **oder** die Codeliste pro Anwendungsfall" beschreibt die
  Ausprägung **je Anwendungsfall** — pro Anwendungsfall genau eine der beiden Formen.
* Die Codeliste pro Anwendungsfall ist ausdrücklich ein **Übergangszustand** („Da sich
  das Dokument noch im Aufbau befindet"). Zielbild ist das EBD; die Codeliste steht
  dort, wo die Überführung noch nicht erfolgt ist.

**Empirische Stütze für den Übergangszustand:** Die DE1131-Werteliste der MIG Gas G1.1
(S. 41–42) führt **50 Codelisten-IDs, alle `G_`/`GS_`, und keinen einzigen `E_`-Code**.
Für UTILMD Gas ist die Überführung also noch nicht erfolgt — in der Praxis zeigt der
Slot ausschließlich auf Codelisten, obwohl er laut MIG auch auf EBDs zeigen dürfte.

**Konsequenz fürs Modell — Korrektur gegenüber der ersten Fassung dieses Abschnitts.**
Dort stand „EBD und Codeliste sind keine zwei Knoten, sondern derselbe Knotentyp". Das
war eine unzulässige Verkürzung des „gilt als". Belegt ist stattdessen:

```text
externe Codeliste  (Obertyp, Referenzziel von DE1131)
 ├── EBD (E_xxxx)                     — Zielform
 └── Codeliste pro Anwendungsfall     — Übergangsform, je Anwendungsfall alternativ
```

Also **ein Obertyp mit zwei Ausprägungen**, nicht ein Knoten mit zwei Namen und nicht
zwei beziehungslose Knoten. Beide Ausprägungen liegen im selben Dokument (EBD 4.2: 106
verschiedene Codelisten-IDs, 346 EBD-IDs) und damit implizit in derselben Version.

**Nicht gegengeprüft:** Beide Quellen verweisen für die genaue Verbindung auf
*Allgemeine Festlegungen 6.1c, Kapitel 6.11 „Antwortcodes in den Segmenten AJT, FTX und
STS"*. Dieses Dokument liegt lokal nicht vor. Wer die Ober-/Untertyp-Aussage vor einer
Modellentscheidung härten will, sollte dort nachschlagen — es ist die von den Quellen
selbst benannte maßgebliche Stelle.

Zeitabhängig ja, aber unterhalb der Version: die Antwortcodes A90/A96/A99 haben eigene
befristete Nutzungszeiträume, laut Mitteilung 55 „um ein halbes Jahr verlängert".

**(10) PID → AHB — B für den Dokumenttyp, D für die Version.**
Die kritisch geprüfte Kante. Ergebnis der vollständigen Auswertung von Spalte 1 über
alle 1370 Datenzeilen:

| Befund | Wert |
|---|---|
| verschiedene AHB-Werte | **21** |
| davon mit Versionsnummer (Regex `\d+\.\d`) | **0** |
| PIs mit mehr als einem AHB-Wert | **0** von 486 |
| Zeilen ohne AHB-Bezug | 31× „--" + 27× API-Webdienst = **58** |

Die 21 Werte lauten: `UTILMD AHB Strom` (331 Z.), `MSCONS AHB` (170), `IFTSTA AHB`
(159), `UTILMD AHB Gas` (130), `ORDRSP AHB` (124), `ORDERS AHB` (115), `REMADV AHB`
(107), `INVOIC AHB` (43), `PARTIN AHB` (42), `UTILTS AHB` (25), `INSRPT AHB` (22),
`COMDIS AHB` (11), `PRICAT AHB` (9), `QUOTES AHB` (9), `REQOTE AHB` (8), `ORDCHG AHB`
(5), `SSQNOT zur Übermittlung von Mehr-/Mindermengen` (2), zwei API-Webdienst-Bezeichner
sowie `--`.

**Damit ist die Warnung des Prüfauftrags empirisch bestätigt:** Die PID benennt einen
AHB-**Dokumenttyp** (bei UTILMD zusätzlich die Sparte), **niemals eine AHB-Version**.
Aus „PI 44112 → UTILMD AHB Gas" folgt **nicht**, dass 44112 in AHB Gas **1.1** vorkommt.
Dass am 01.04.2026 die 1.1 gilt, stammt aus Mitteilung 54 — die PID trägt dazu nichts
bei. Die Kante ist **nicht versionsgebunden**; ihre Versionsauflösung ist ein
Fremdschluss über den regulatorischen Stand.

Drei weitere Einschränkungen, die gegen eine Gleichsetzung „PI in PID ⇒ PI in AHB-Version"
sprechen:
1. **Die PID ist kein vollständiges PI-Verzeichnis.** Die MIG Gas G1.1 führt 91 PIs,
   die PID 3.3 führt 486; die Schnittmenge ist 88. **Drei PIs — 44096, 44097, 44172 —
   stehen in der MIG, aber nicht in der PID.** (44096 = „TSIMSG / Deklarationsliste an
   MGV", 44097 = „… an BKV".)
2. **Ein AHB-Wert deckt mehrere Dokumentversionen ab.** „UTILMD AHB Gas" bezeichnet den
   Dokumenttyp über alle Versionen hinweg; die PID unterscheidet nicht zwischen 1.1
   und 1.2.
3. **Die Gegenrichtung ist N/A**, nicht nur D: AHB Gas 1.1 und MIG Gas G1.1 enthalten
   **0 Treffer** auf „Anwendungsübersicht der Prüfidentifikatoren". Die Beziehung ist
   strikt einseitig.

**(11) PID → Nachricht — B.**
Identische Beleglage wie (5), nur auf Dokumentebene: die PID 3.3 deckt über ihre 21
AHB-Werte die Nachrichtentypen ab; eine eigene Spalte dafür gibt es nicht. 58 der 1370
Datenzeilen bleiben ohne auflösbaren Nachrichtentyp. Einstufung **B**, weil abgeleitet.

### I.4 Fünf durchgerechnete Beziehungsketten

Nachvollzogen wurde jeweils
`PID → PI → Nachricht → MIG → AHB → Codeliste/EBD` an den echten Dokumenten.

| | PI 44112 | PI 44123 | PI 23001 | PI 70095 | PI 44096 |
|---|---|---|---|---|---|
| **PID Tab. 1** | ✓ 6 Zeilen, 3 Prozesse | ✓ 2 Zeilen | ✓ Lfd. Nr. 31320 (Strom) + 871 (Gas) | ✓ Lfd. Nr. 12170 | ✗ **nicht enthalten** |
| **AHB-Spalte** | „UTILMD AHB Gas" (o. Version) | „UTILMD AHB Gas" | „INSRPT AHB" | „SSQNOT zur Übermittlung …" | — |
| **Nachricht** | UTILMD (abgeleitet) | UTILMD | INSRPT | SSQNOT | UTILMD (aus MIG, direkt) |
| **MIG** | ✓ Gas G1.1, DE1154 S. 52 | ✓ Gas G1.1 | ✗ **kein INSRPT MIG auffindbar** | ✗ **kein SSQNOT MIG auffindbar** | ✓ Gas G1.1, DE1154 |
| **AHB** | ✓ Gas 1.1, 19 Seiten | ✓ Gas 1.1, 11 Seiten | ✗ Version ungeklärt (E.1) | ✗ Version ungeklärt (E.1) | ✗ **nicht im AHB Gas 1.1** |
| **Codeliste** | ✓ G_0016 | ✓ G_0019 | — | — | — |
| **Codeliste im EBD-Dok** | ✓ G_0016 (4 Treffer in 4.2) | ✓ G_0019 (2 Treffer) | — | — | — |
| **EBD (E_xxxx)** | ✗ **Bruch** | ✗ **Bruch** | ✗ | ✗ | ✗ |

**Wo die Kette trägt:** Für Gas-UTILMD-PIs läuft sie sauber durch bis zur Codeliste —
PID → PI → UTILMD → MIG Gas G1.1 → AHB Gas 1.1 → G_00xx → im EBD-Dokument 4.2
vorhanden. Fünf von sechs Kanten sind belegbar.

**Wo sie bricht — drei verschiedene Bruchtypen:**

1. **Bruch am EBD (systematisch, betrifft alle PIs).** Das AHB Gas 1.1 enthält über 329
   Seiten **0 Vorkommen** von `E_XXXX` und **0 Vorkommen** des Wortes
   „Entscheidungsbaum". Das EBD-Dokument 4.2 enthält über 851 Seiten **0 Vorkommen**
   des Wortes „Prüfidentifikator". **Es gibt keine dokumentierte direkte Beziehung
   zwischen einem Prüfidentifikator und einem Entscheidungsbaum.** Der einzige Pfad
   führt indirekt über die Codeliste (AHB → G_00xx → im EBD-Dokument), und der landet
   bei einer *Codeliste*, nicht bei einem *Entscheidungsbaum*.
2. **Bruch an MIG/AHB wegen fehlender Dokumente** (23001, 70095). Die PID belegt die
   Existenz und den Prozessbezug, aber die zugehörigen INSRPT- und SSQNOT-Dokumente
   sind im Stand nicht auffindbar (siehe E.1). Kette endet nach `PI → Nachricht`.
3. **Bruch an der PID selbst** (44096). Der PI existiert in der MIG Gas G1.1, ist aber
   in der PID nicht enthalten und im AHB Gas 1.1 nicht auffindbar. Wer die Kette bei
   der PID beginnt, verliert diesen PI vollständig. Betrifft 3 der 91 MIG-PIs.

### I.5 Folgerungen für das Beziehungsmodell

1. **Zwei Kanten laufen entgegen der vorgegebenen Richtung.** `MIG → AHB` ist real
   `AHB → MIG`, `Codeliste → EBD` ist real `EBD → Codeliste`. Ein Modell, das die
   Kanten in der vorgegebenen Richtung anlegt, hat für beide keinen Beleg.
2. **Nur zwei Kanten tragen eine Fremdversion:** `Mitteilung → Dokument` (Version +
   „gültig ab") und `AHB → MIG` („Stand MIG: G1.1"). Alle anderen Verweise sind
   versionslos. Versionsauflösung ist damit fast immer eine Leistung des
   *regulatorischen Stands*, nicht des Dokuments — genau die Aufgabe von
   `get_effective()`.
3. **EBD und Codeliste sind kein Kantenpaar, sondern Obertyp und Ausprägungen.**
   Belegt (I.3.1): „externe Codeliste" ist der Obertyp und „unterteilt/aufteilt" sich in
   EBD und Codeliste pro Anwendungsfall; die Codeliste ist dabei ausdrücklich
   Übergangsform. Statt einer Kante `Codeliste → EBD` gehört an diese Stelle eine
   Typ-Hierarchie mit einem gemeinsamen Referenzslot (DE1131). Vor der
   Modellentscheidung sollte AF 6.1c Kap. 6.11 gegengelesen werden.
4. **PID → AHB darf im Modell nie auf eine AHB-Version zeigen.** Ziel der Kante ist ein
   Dokument*typ*. Eine Kante PI → AHB-Version wäre erfunden.
5. **Die PID ist kein Vollverzeichnis.** 3 MIG-PIs fehlen. Eine Modellierung „PI
   entsteht aus der PID" verliert sie.
6. **Zeitabhängigkeit sitzt auf mindestens drei Ebenen:** Mitteilung (M47 verschiebt
   Gültigkeitsdaten), Dokumentteil (UTILMD Strom 2.1 mit zwei Gültigkeitsdaten,
   Abschnitt D.1) und Einzelcode (A90/A96/A99 mit befristeter Nutzung). Ein einziges
   Gültigkeitsfeld je Dokument reicht auf keiner davon.

### I.6 Vollständigkeitsprüfung Beziehungsanalyse

| Prüfung | Ergebnis |
|---|---|
| Vorgegebene Kanten | 11 |
| Untersuchte Kanten | **11** |
| Kanten mit Stufe + Richtung + Kardinalität + Vers.-/Zeitabhängigkeit + Beleg | **11** |
| Abweichung | **0** |
| Stufenverteilung | A: 5 · B: 6 · C: 0 · D: 0 · N/A: 0 |
| D nur auf Gegenrichtungen | 4 (Kanten 1, 3, 7, 9) |
| N/A nur auf Gegenrichtungen | 3 (Kanten 5, 8, 10) |
| Durchgerechnete PI-Ketten | 5 (davon 2 tragend bis Codeliste, 3 mit dokumentiertem Bruch) |

Keine der elf Kanten ist als Ganzes N/A oder D — jede ist mindestens B. Die Unsicherheit
liegt durchgehend in den *Gegenrichtungen* und in der *Versionsbindung*, nicht in der
Existenz der Beziehung.

---

**STOP.** Keine Implementierung, keine Schemaänderung, kein Import. Freigabe für den
nächsten Schritt abwarten.
