# Etappe 0 — Fundament: Mitteilung 56 erfassen

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 17.09.2026 (Abrufe 17:12–17:14 UTC)
**Status:** Etappe 0 abgeschlossen. Nur Metadaten, keine Tiefenanalyse einzelner Dokumente.
Keine Schema-, Import- oder Datenbankänderung.

Maschinenlesbare Rohliste: [`etappe0_rohliste_mitteilung56.json`](etappe0_rohliste_mitteilung56.json)
(34 Einträge, je mit URL, SHA-256, Dateigröße, Seitenzahl, Deckblattangaben und allen
BDEW-Einträgen gleicher Version). Quellenabzüge: [`quellen/`](quellen/).

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| In Mitteilung 56 referenzierte Dokumente, erfasst | **34** (34 PDF, alle heruntergeladen und gehasht) |
| davon in BDEW-MaKo mit identischer Version wiedergefunden | **34 / 34** |
| davon mit konsolidierter Fehlerkorrekturfassung (nur bei BDEW, nicht bei der BNetzA) | **9** |
| Kandidaten außerhalb von Mitteilung 56, laut BDEW am Stichtag gültig (Themen, **nicht bewertet**) | **57** |
| Offene/unklare Fälle | **9** (Abschnitt 7) |
| Widersprüche BNetzA ↔ BDEW (belegt) | **0** auf Ebene der 34 Dokumente; 1 Kandidat bei den API-Webdiensten (O-4) |

---

## 2. Gegenprüfung Mitteilung 56 (Abschnitt 2 des Auftrags)

### 2.1 Ist Mitteilung 56 die gültige, verbindliche Mitteilung für den 01.10.2026?

**Ja, bestätigt.** Belege von der BNetzA-Seite selbst:

* Die amtliche Mitteilungsliste (`…/835_mitteilungen_datenformate/Datenformate-node.html`,
  Abzug `quellen/bnetza_mitteilungsliste_bk6_bk7_20260917.txt`) führt als jüngste Einträge:

  | Nr. | Betreff | veröffentlicht |
  |---|---|---|
  | 57 | Konsultation überarbeiteter Nachrichtentypversionen zum 01.04.2027 | 31.07.2026 |
  | **56** | **Inkrafttreten überarbeiteter Nachrichtentypversionen zum 01.10.2026** | **01.04.2026** |
  | 55 | Konsultation von Nachrichtentypversionen für den Umsetzungstermin 01.10.2026 | 02.02.2026 |
  | 54 | Inkrafttreten überarbeiteter Nachrichtentypversionen zum 01.04.2026 | 01.10.2025 |

* Der Mitteilungstext 56 sagt wörtlich: „Diese Versionen gelten für alle […]
  umsetzungspflichtigen Marktteilnehmer verbindlich ab dem 01.10.2026.“
* `Mitteilung_58` bis `Mitteilung_60` liefern HTTP 404.

### 2.2 Gibt es eine neuere Mitteilung, die 56 ersetzt, korrigiert oder ergänzt?

**Nein.** Die einzige neuere Mitteilung ist **Nr. 57 (31.07.2026)**. Sie ist eine reine
**Konsultation** für den Umsetzungstermin **01.04.2027** und ändert den Stand zum 01.10.2026
nicht. Zwei Punkte daraus sind trotzdem festzuhalten:

1. **Nicht verbindliche Nachfolger-Entwürfe** existieren bereits für 18 EDIFACT-Dokumente
   (u. a. UTILMD AHB/MIG Strom 2.3/S2.3, APERAK AHB 1.1a / MIG 2.2a, IFTSTA 2.1a, PID 4.1,
   Allgemeine Festlegungen 6.1e, CONTRL AHB 1.0a, CONTRL MIG 2.0c, QUOTES AHB 1.2 / MIG 1.4,
   Codeliste Artikelnummern 5.7) sowie für EBD 4.4, ActivationDocument AWT 1.1g, RzÜ 1.11,
   RzÜ API-Webdienste 1.3 und API-Webdienste Strom Release 2.0.0. → Frage 7 aus Abschnitt 8
   (Konsultationsfassung, nicht verbindlich), wird je Etappe zugeordnet.
2. **Vorschlag, den Umsetzungszeitraum zu verlängern (nicht beschlossen):** Die PG EDI@Energy
   „weist darauf hin, dass vorgeschlagen wird“, für die **zum 01.10.2026 zu
   veröffentlichenden** Dokumente zwölf statt sechs Monate Umsetzungszeit einzuräumen, also
   produktive Anwendung zum **01.10.2027**. Das betrifft den künftigen Stand
   01.04.2027/01.10.2027, **nicht** den Stand 01.10.2026. Festgehalten als Hinweis auf einen
   abweichenden Umsetzungstermin.

### 2.3 Beschlusskammer 6 oder 7?

Geprüft, nicht angenommen. Befund:

| Prüfpunkt | Beleg | Ergebnis |
|---|---|---|
| Überschrift der Mitteilungsliste | „Daten­for­ma­te zur Ab­wick­lung der Markt­kom­mu­ni­ka­ti­on — **Beschlusskammer 6 / Beschlusskammer 7**“ | **Eine gemeinsame Reihe** für beide Kammern, technisch im BK6-Baum abgelegt |
| Prozesse auf der Listenseite | GPKE, **GeLi Gas**, MaBiS, WiM, MPES | Gas-Prozesse laufen über dieselbe Reihe |
| Kopfzeile der Konsultationen | M55, M57: „- Beschlusskammer 6 - / - Beschlusskammer 7 -“ | beide Kammern |
| Kopfzeile der Veröffentlichungen | M54, **M56**: nur „- Beschlusskammer 6 -“ | nur BK6 unterzeichnet, obwohl UTILMD **Gas** 1.2/G1.2 enthalten ist |
| BK7 „Aktuelles“ (`BK7_01_Aktuell/BK7_Aktuell.html`) | keine Mitteilung zu Datenformaten; nur Festlegungen/Beschlüsse (u. a. **GeLi Gas 3.0**, BK7-24-01-009, 24.09.2025; WiM Gas 2.0, 15.08.2025) | keine separate BK7-Formatreihe |
| Ältere gemeinsame Mitteilungen | Mitteilungen zu BK6-16-200/BK7-16-142 liegen im BK7-Pfad, werden aber aus derselben Liste verlinkt | historisch, für den Stichtag nicht relevant |

**Herangezogene Quelle:** ausschließlich die gemeinsame Reihe „Mitteilungen zu den
Datenformaten“ (BK6-Pfad, BK6/BK7 gemeinsam). **Begründung:** Es gibt keine eigene
BK7-Formatreihe. BK7 behandelt Festlegungen (Netzzugang, Bilanzierung, GeLi Gas,
Wasserstoff).

Nicht geklärt ist, ob die **Festlegung GeLi Gas 3.0** einen eigenen Umsetzungstermin
hat, der Gas-Formate zum 01.10.2026 berührt. Das wird in Etappe 3 geprüft (O-6).
Dass M56 nur von BK6 gezeichnet ist, wird als formale Beobachtung festgehalten. Eine
Einschränkung der Verbindlichkeit für Gas steht nicht im Text.

---

## 3. Zeitliche Logik Konsultation → Veröffentlichung → Inkrafttreten (Abschnitt 1)

Für den Stichtag 01.10.2026 belegt:

```text
M55 Konsultation          02.02.2026   Stellungnahmefrist 27.02.2026   (BK6 + BK7)
        │  Konsultationssitzung 05.03.2026 (BDEW)
        ▼
M56 Veröffentlichung      01.04.2026   "verbindlich ab dem 01.10.2026" (BK6)
        │  BDEW: konsolidierte Fehlerkorrekturstände 23.06. / 29.06. / 06.08. / 12.08.2026
        ▼
Inkrafttreten             01.10.2026
        ┆
M57 Konsultation          31.07.2026   für 01.04.2027 (Frist 31.08.2026) — nicht verbindlich
```

**Korrektur an der Faustregel im Auftrag:** Nicht die Konsultation liegt 6 Monate vor dem
Stichtag, sondern die **Veröffentlichung** (01.04. → 01.10.). Die Konsultation liegt rund
**8 Monate** davor (02.02.2026 → 01.10.2026; ebenso M52 01.08.2025 → 01.04.2026).

Neu gegenüber dem Grundmuster: **Zwischen Veröffentlichung und Inkrafttreten entstehen
weitere maßgebliche Fassungen** (konsolidierte Fehlerkorrekturstände), und zwar nur auf
BDEW-MaKo. Die Zeitachse eines Dokuments hat also mehr als drei Punkte.

---

## 4. Mitteilung 56 — vollständige Analyse (Abschnitt 3)

| Merkmal | Befund |
|---|---|
| Titel | Mitteilung Nr. 56 zu den Datenformaten zur Abwicklung der Marktkommunikation — „Inkrafttreten überarbeiteter Nachrichtentypversionen zum 01.10.2026“ |
| Kammer / Datum | Beschlusskammer 6, 01.04.2026 |
| Konsultationsbezug | Konsultation vom 02.02.2026 bis 27.02.2026 (= M55) |
| Inkrafttreten | verbindlich ab **01.10.2026**; „etwaige abweichende Umsetzungstermine, die sich aus gesetzlichen Vorgaben oder aus Festlegungen der Bundesnetzagentur ergeben, bleiben unberührt“ |
| Sparten | „spartenübergreifende Nachrichtentypversionen“; Sparten-Suffix nur bei UTILMD |
| Fachlicher Sonderhinweis | **UTILMD Strom / § 10b EEG (Fernsteuerbarkeit):** Status Z24, Codes ZW5 (steuerbar) / ZW6 (nicht steuerbar); ZW5 bestätigt die Erfüllung aller Anforderungen nach § 10b EEG 2023 → fachlich, Etappe 1 |
| EDIFACT-Dokumente | 30 |
| Entscheidungsbaum-Diagramme | 1 (EBD und Codelisten 4.3) |
| Regelungen zum Übertragungsweg | 3 (RzÜ 1.10, AS4-Profil 1.2, RzÜ AS4 2.6) |
| API-Dokumente | nur die API Guideline 1.0b (im EDIFACT-Block). **API-Webdienste Release 2.0.0 ausdrücklich nicht Bestandteil**, soll mit weiteren Anpassungen erneut konsultiert werden |
| XML-Dokumente | **keine Redispatch-/Kaskade-XML-Dokumente.** Der Hinweis „XML-Dateien“ meint die XML-Fassungen der MIG/AHB auf BDEW-MaKo (kostenpflichtiges Abonnement) |
| Hinweise auf andere Quellen | www.bdew-mako.de (Veröffentlichung „auf ihren Internetseiten“ durch BNetzA **und** BDEW; XML-Fassungen) |
| Zurückgestellt / nicht veröffentlicht | (a) API-Webdienste Release 2.0.0 — ausdrücklich; (b) **REQOTE MIG 1.3d** — in M55 konsultiert, in M56 **ohne jeden Hinweis** nicht enthalten (O-3); (c) PID 4.0 „Info“-xlsx aus M55 nicht in M56 (auf BDEW als informatorische Lesefassung vorhanden) |
| Dateiformate bei der BNetzA | ausschließlich PDF (34/34) |

---

## 5. Rohliste aller Dokumente aus Mitteilung 56

Tags gemäß Anhang: Kategorie ∈ {AHB, MIG, PID, EBD, Codeliste, Übertragungsweg, AS4, API,
XML, Sonstiges}; Sparte ∈ {Strom, Gas, beide}. „beide“ bedeutet: keine Spartenangabe im
Titel, Mitteilung spricht von spartenübergreifend. Ob der Nachrichtentyp tatsächlich in
beiden Sparten verwendet wird, ist **nicht** geprüft (Etappe 2/3).

Alle 34: veröffentlicht 01.04.2026, gültig ab 01.10.2026 (Beleg: Mitteilungstext), Dateityp
PDF, Deckblatt-Publikationsdatum 01.04.2026, Autor BDEW, Deckblattversion = Version im
Mitteilungstitel (34/34). Hashes und URLs stehen in der JSON-Datei.

| # | Kat. | Nachrichtentyp | Sparte | Dokument | Version | Seiten | Stand MIG (Deckblatt) | Vorgänger (lt. Befund 01.04.2026) | BDEW: konsolidierte Fehlerkorrektur | Etappe |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Sonstiges | — | beide | Allgemeine Festlegungen | 6.1d | 118 | — | 6.1c (M54) | — | 4 |
| 2 | PID | — | beide | Anwendungsübersicht der Prüfidentifikatoren | 4.0 | 86 | — | 3.3 (M54) | Stand 29.06.2026, **12.08.2026** | 4 |
| 3 | AHB | APERAK | beide | APERAK AHB | 1.1 | 55 | 2.2 | 1.0 (M51) | — ⚠ O-1 | 2/3 |
| 4 | MIG | APERAK | beide | APERAK MIG | 2.2 | 27 | — | 2.1i (M42+M47) | — | 2/3 |
| 5 | API | — | beide | API Guideline | 1.0b | 22 | — | 1.0a (M46+M47) | — | 6 |
| 6 | Codeliste | — | beide | Codeliste der Konfigurationen | 1.4 | 64 | — | 1.3c (M51) | — | 4 |
| 7 | Codeliste | — | beide | Codeliste der Verwendungszwecke | 1.0 | 7 | — | — (neu) | Stand 29.06.2026 | 4 |
| 8 | AHB | IFTSTA | beide | IFTSTA AHB | 2.1 | 76 | 2.1 | 2.0h (M51) | — | 2/3 |
| 9 | MIG | IFTSTA | beide | IFTSTA MIG | 2.1 | 144 | — | 2.0g (M51) | — | 2/3 |
| 10 | AHB | INVOIC | beide | INVOIC AHB | 1.0b | 83 | 2.8e | 1.0a (M54) | — | 2/3 |
| 11 | AHB | MSCONS | beide | MSCONS AHB | 3.2 | 156 | — | 3.1g (M54) | — | 2/3 |
| 12 | MIG | MSCONS | beide | MSCONS MIG | 2.5 | 51 | — | 2.4c (Hinweis M46) | — | 2/3 |
| 13 | AHB | ORDCHG | beide | ORDCHG AHB | 1.1 | 10 | 1.2 | 1.0a (M46+M47) | — | 2/3 |
| 14 | MIG | ORDCHG | beide | ORDCHG MIG | 1.2 | 15 | — | ungeklärt | — | 2/3 |
| 15 | AHB | ORDERS | beide | ORDERS AHB | 1.1b | 135 | 1.4c | 1.1a (M54) | Stand 29.06.2026 | 2/3 |
| 16 | MIG | ORDERS | beide | ORDERS MIG | 1.4c | 144 | — | 1.4b (M51) | — | 2/3 |
| 17 | AHB | ORDRSP | beide | ORDRSP AHB | 1.1b | 74 | 1.4c | 1.1a (M54) | — | 2/3 |
| 18 | MIG | ORDRSP | beide | ORDRSP MIG | 1.4c | 42 | — | 1.4b (M54) | — | 2/3 |
| 19 | AHB | PARTIN | beide | PARTIN AHB | 1.1 | 88 | 1.1 | 1.0f (M54) | — | 2/3 |
| 20 | MIG | PARTIN | beide | PARTIN MIG | 1.1 | 64 | — | 1.0f (M54) | — | 2/3 |
| 21 | AHB | PRICAT | beide | PRICAT AHB | 2.1 | 27 | 2.1 | 2.0f (M51) | — | 2/3 |
| 22 | MIG | PRICAT | beide | PRICAT MIG | 2.1 | 31 | — | 2.0e (M51) | — | 2/3 |
| 23 | AHB | QUOTES | beide | QUOTES AHB | 1.1a | 41 | **mehrdeutig** ⚠ O-2 | 1.1 (M51) | — | 2/3 |
| 24 | MIG | QUOTES | beide | QUOTES MIG | 1.3c | 109 | — | 1.3b (M51) | — | 2/3 |
| 25 | AHB | REQOTE | beide | REQOTE AHB | 1.2 | 31 | **mehrdeutig** ⚠ O-2 | 1.1 (M51) | Stand 29.06.2026 | 2/3 |
| 26 | AHB | UTILMD | **Strom** | UTILMD AHB Strom | 2.2 | 1397 | S2.2 | 2.1 (M46+M47) | Stand 29.06.2026 | **1** |
| 27 | MIG | UTILMD | **Strom** | UTILMD MIG Strom | S2.2 | 559 | — | S2.1 (M46+M47) | Stand 29.06.2026, **06.08.2026** | **1** |
| 28 | AHB | UTILMD | **Gas** | UTILMD AHB Gas | 1.2 | 307 | G1.2 | 1.1 (M54) | Stand 29.06.2026, **06.08.2026** | **1** |
| 29 | MIG | UTILMD | **Gas** | UTILMD MIG Gas | G1.2 | 169 | — | G1.1 (M54) | Stand 29.06.2026 | **1** |
| 30 | AHB | UTILTS | beide | UTILTS AHB | 1.1 | 48 | 1.1e | 1.0 (M46+M47) | — | 2/3 |
| 31 | EBD | — | beide | Entscheidungsbaum-Diagramme und Codelisten | 4.3 | 832 | — | 4.2 (M54) | Stand 23.06.2026 | 5 |
| 32 | Übertragungsweg | — | beide | Regelungen zum Übertragungsweg | 1.10 | 41 | — (Deckblatt: „Anzuwenden ab: 01.10.2026“) | 1.9 (M51) | — | 6 |
| 33 | AS4 | — | beide | AS4-Profil | 1.2 | 26 | — („Anzuwenden ab: 01.10.2026“) | 1.1 v13 (M46) | — | 6 |
| 34 | AS4 | — | beide | Regelungen zum Übertragungsweg AS4 | 2.6 | 12 | — („Anzuwenden ab: 01.10.2026“) | 2.5 (M54) | — | 6 |

**Nachrichtentypen für Etappe 2/3 (aus M56):** APERAK, IFTSTA, INVOIC, MSCONS, ORDCHG,
ORDERS, ORDRSP, PARTIN, PRICAT, QUOTES, REQOTE, UTILTS. Dazu kommen Nachrichtentypen, die
in M56 fehlen, laut BDEW am Stichtag aber gelten (Abschnitt 6): COMDIS, CONTRL, INSRPT,
INVOIC MIG, REMADV, REQOTE MIG, UTILTS MIG, sowie SSQNOT, das in keiner Quelle geführt
wird (O-5).

**Stichtag bei 3 von 34 Dokumenten doppelt belegt:** RzÜ 1.10, AS4-Profil 1.2 und RzÜ AS4
2.6 tragen „Anzuwenden ab: 01.10.2026“ zusätzlich auf dem Deckblatt. Bei allen anderen
steht der Stichtag nur im Mitteilungstext.

---

## 6. Zweite Quelle BDEW-MaKo — Zugang und Befund zur Quelle

### 6.1 Zugang

Im Befund vom 05.09.2026 lieferte `bdew-mako.de` HTTP 403. **Das ist nicht mehr so.** Die
Plattform ist eine JavaScript-Anwendung. Ihre öffentliche, nicht authentifizierte
Dokumenten-API liefert strukturierte Metadaten:

* `GET https://www.bdew-mako.de/api/documents` → HTTP 200, **1.752 Einträge**
  (Abzug `quellen/bdew_mako_api_documents_20260917.json`, SHA-256
  `016a6f8c…01fb709f`, abgerufen 2026-09-17T17:12:32Z)
* `GET https://www.bdew-mako.de/api/topicGroups` → 14 Themengruppen
* `GET /api/list/documents` → HTTP 401 (angemeldeter Bereich, nicht benutzt)
* Felder je Eintrag: `id, fileId, title, topicId, topicGroupId, isFree, validFrom, validTo,
  isConsolidatedReadingVersion, isErrorCorrection, correctionDate,
  isInformationalReadingVersion, isExtraordinaryPublication, fileType, link`
* Download-Endpunkt laut Frontend: `/api/downloadDocuments/{…}` — **in Etappe 0 noch nicht
  genutzt**, die BDEW-PDFs werden erst ab Etappe 1 geladen und gehasht.

### 6.2 Befund zur Datenqualität der Quelle (maßgeblich für die Methodik ab Etappe 1)

1. **Die Kennzeichenfelder sind nicht gepflegt.** `isConsolidatedReadingVersion`,
   `isErrorCorrection`, `isInformationalReadingVersion`, `isExtraordinaryPublication` sind
   bei **allen 1.752** Einträgen `false`, `correctionDate` ist immer leer. Der Fassungstyp
   (Basis / informatorische Lesefassung / konsolidierte Fehlerkorrektur mit Stand /
   außerordentliche Veröffentlichung / Konsultationsfassung) lässt sich **nur aus dem
   Titel** ableiten.
2. **`validTo` hat keine einheitliche Bedeutung.**
   * Regulatorisches Ende: z. B. UTILMD AHB Gas 1.1 → `validTo 2026-09-30`.
   * Ablösung eines Fehlerkorrekturstands: UTILMD AHB Gas 1.2 Stand 29.06.2026 →
     `validTo 2026-08-05` (Tag vor dem Stand 06.08.2026), obwohl die Version selbst erst ab
     01.10.2026 gilt.
   * `validTo` **vor** `validFrom`: z. B. XML-Basisdatei UTILMD AHB Gas 1.2 (`id 8390`,
     validFrom 2026-10-01, validTo 2026-06-28). Das wirkt wie „Datei zurückgezogen“.
   * Konsultationsfassungen: `validFrom`/`validTo` = Konsultationszeitraum.

   `validFrom`/`validTo` beschreiben also die **Gültigkeit der Datei auf der Plattform**,
   nicht zwingend die regulatorische Gültigkeit der Version. Das ist die Präzisierung zu
   Abschnitt 5 des Auftrags („nicht nur anhand des Dateinamens“): auch nicht allein anhand
   von `validTo`.
3. **Die Basisfassung bleibt neben den Fehlerkorrekturen „gültig“.** Das Basis-PDF jeder
   M56-Version hat `validTo = offen`, auch wenn konsolidierte Stände existieren. Die
   Prioritätsregel aus Abschnitt 6 des Auftrags muss das auflösen, die Quelle tut es nicht.
4. **Keine Überschneidung von Versionen.** Für kein BDEW-Thema sind am 01.10.2026 zwei
   verschiedene Basisversionen gleichzeitig gültig.
5. **Keine künftigen Versionen.** Kein Eintrag hat `validFrom` nach dem 01.10.2026.
   Nachfolger existieren nur als Konsultationsfassung (M57).
6. **Fehlerkorrekturen erscheinen nur bei BDEW.** Die BNetzA-Seite führt ausschließlich die
   Basisfassung vom 01.04.2026. Für 9 der 34 Dokumente gibt es bei BDEW spätere
   konsolidierte Stände (Tabelle Abschnitt 5). Die maßgebliche Fassung ist damit bei diesen
   9 Dokumenten **nicht** das bei der BNetzA verlinkte PDF. Die Regel „PDF als Primärquelle“
   (Abschnitt 7) muss sich deshalb auf das **BDEW-PDF der konsolidierten Fassung** beziehen.

### 6.3 Kandidaten außerhalb von Mitteilung 56 (laut BDEW am 01.10.2026 gültig, nicht bewertet)

57 BDEW-Themen haben am Stichtag gültige Einträge, die nicht zu den 34 M56-Dokumenten
gehören. **Nur Rohliste für die Etappenzuordnung**, keine Gültigkeitsaussage:

| Etappe | Themen (Version laut BDEW-Titel, `validFrom`) |
|---|---|
| 2/3 EDIFACT | COMDIS AHB 1.0h / MIG 1.0g (01.04.2026) · REMADV AHB 1.0a / MIG 2.9e (01.04.2026) · INVOIC MIG 2.8e (01.10.2025) · REQOTE MIG 1.3c (01.10.2025) · UTILTS MIG 1.1e (06.06.2025) · CONTRL AHB 1.0 (01.10.2025, außerordentliche Veröffentlichung Stand 11.12.2025) · **CONTRL MIG 2.0b** (01.10.2022, a. o. Veröff. 11.12.2025) · **INSRPT AHB 1.1g** / **INSRPT MIG 1.1a** (2022/2023, a. o. Veröff.) |
| 4 Codelisten/Querschnitt | OBIS 2.5c (01.04.2026) · Artikelnummern/Artikel-ID 5.6 (01.09.2025; konsolidiert 30.09.2025) · Lokationsbündelstrukturen 1.0 (konsolidiert 13.12.2024) · Europäische Ländercodes 1.0 · Standardlastprofile TU München 1.1 · Temperaturanbieter 1.0i · Zeitreihentypen 1.1d · Änderungsantrag EBD 1.5 · Gruppierungen der EDI@Energy-Dokumente 2.2 · Anwendungshilfe Berechnungsformeln Solarpaket 1 1.1 · 3 BDEW-Anwendungshilfen vom 18.08.2026 (Berechnungsformeln in API-Webdiensten; Lokationsbündel; **Einführungsszenario neue Segmente/Codes zum 01.10.2026 in der UTILMD**) |
| 6 XML/API/Übertragungsweg | Redispatch 2.0: 8 Dokumenttypen × AWT/FB/XSD (Acknowledgement 1.0g, Activation 1.1f, Kostenblatt 1.0d, NetworkConstraint 1.1b, PlannedResourceSchedule 1.0f, Stammdaten 1.4b, StatusRequest 1.1, Unavailability 1.1b) + Änderungshistorie · **Kaskade AWT/FB/XSD 1.0** (01.04.2026) · API-Webdienste Strom Release 1.0.0 + OpenAPI-Doku (29.01.2026) · Verzeichnisdienst API Release 1.0.0 (29.01.2026) · Regelungen zum Verzeichnisdienst 1.1 · RzÜ für API-Webdienste 1.2 (konsolidiert) |

Die Einträge **CONTRL MIG** und **INSRPT AHB** waren im Befund 01.04.2026 „UNGEKLÄRT“. Mit
BDEW gibt es jetzt jeweils einen Kandidaten. Ob der trägt, wird in Etappe 2/3 bewertet.

---

## 7. Offene und unklare Fälle

| ID | Fall | Beleg | Bearbeitung |
|---|---|---|---|
| **O-1** | Das bei der BNetzA verlinkte **APERAK AHB 1.1**-PDF ist auf dem Deckblatt **sichtbar** als „Informatorische Lesefassung“ gekennzeichnet (dunkelrot, 20 pt). Es ist das einzige der 34 PDFs mit diesem Vermerk. Laut Abschnitt 6 darf eine informatorische Lesefassung nicht maßgeblich sein, es ist aber die einzige amtlich verlinkte Fassung. BDEW führt ein separates Basis-PDF (`id 8321`), dessen Deckblatt noch nicht geprüft ist. | `APERAK_AHB_1_1_20260401.pdf`, S. 1; SHA-256 `6c1aef93…31f1dfc0` | Etappe 2: BDEW-PDF laden und vergleichen |
| **O-2** | **QUOTES AHB 1.1a** und **REQOTE AHB 1.2**: Deckblattfeld „Stand MIG“ enthält zwei schwarze Textobjekte an **identischer Position**, „1.4b“ und „1.3c“. Die Angabe ist nicht eindeutig lesbar, Textextraktion ergibt `11..43bc`. Es gibt weder eine QUOTES MIG 1.4b noch eine REQOTE MIG 1.4b. | Zeichenanalyse pdfplumber, x=253,8 pt | Etappe 2: MIG-Bezug aus dem Dokumentinneren belegen, nicht raten |
| **O-3** | **REQOTE MIG 1.3d** wurde in M55 konsultiert, in M56 aber **ohne Hinweis** nicht veröffentlicht. BDEW führt REQOTE MIG 1.3c weiter (ab 01.10.2025, offen). Welche MIG REQOTE AHB 1.2 referenziert, ist offen (hängt an O-2). | M55 vs. M56; BDEW `id 7906` | Etappe 2 |
| **O-4** | **API-Webdienste:** M56 schließt Release 2.0.0 aus. BDEW beendet „API-Webdienste zur Identifikation der MaLo-ID 1.0.0“ und „…Steuerungshandlungen 1.0.0“ zum 28.01.2026 und führt ab 29.01.2026 „API-Webdienste Strom – Release 1.0.0“ (GitHub). Eine BNetzA-Mitteilung, die diesen Wechsel als verbindlich ausweist, ist nicht gefunden. M55 nennt nur den Umzug von Swagger auf GitHub, beschlossen in der Konzeptkonsultation. **Möglicher Widerspruch**, noch nicht belegt. | BDEW `id 7313/7314/8230`; M55-Text | **gelöst in Etappe 6:** Version aus M36/M43/M46 (Kriterium A), PID 4.0 (B), Veröffentlichungsweg GitHub durch API-Guideline 1.0b (Anlage M56) geregelt; kein Widerspruch |
| **O-5** | **SSQNOT AHB (Gas)** steht weder in M56 noch in der BDEW-API (0 Einträge über alle 1.752). Im Befund 01.04.2026 war er „UNGEKLÄRT“. | BDEW-Abzug | Etappe 3 |
| **O-6** | **GeLi Gas 3.0** (Festlegung BK7-24-01-009 vom 24.09.2025): Umsetzungstermin und Auswirkung auf Gas-Datenformate zum 01.10.2026 nicht geprüft. M56 behält abweichende Termine aus Festlegungen ausdrücklich vor. | BK7 „Aktuelles“ | Etappe 3 |
| **O-7** | **Redispatch-XML und Kaskade** stehen nicht in M56, bei BDEW mit offenem `validTo`. Das Verhältnis zur letzten BNetzA-Veröffentlichung wurde für den Stichtag noch nicht bestätigt. | BDEW-Abzug | Etappe 6 |
| **O-8** | **BDEW-Metadaten:** Kennzeichen nicht gepflegt, `validTo`-Semantik uneinheitlich (Abschnitt 6.2). Die Methodik zur Bestimmung der maßgeblichen Fassung muss darauf ausgelegt werden. | Abschnitt 6.2 | Etappe 1 (Pilot validiert die Methodik) |
| **O-9** | **Auftragsreferenz fehlt:** `Claude_Code_Prompt_FINAL.md` (Abschnitt 18, Workflow) liegt weder im Repo noch auf dem Rechner. Der Workflow wurde analog zu Issue #56/PR (Befund 01.04.2026) umgesetzt: Issue → eigener Branch → Draft-PR. | `find /` ohne Treffer | Rückfrage an den Nutzer |

**Kein offener Fall, nur dokumentiert:** Auf den Deckblättern von 15 PDFs steht **weißer,
unsichtbarer Resttext** aus der Vorlage, z. B. „Konsultationsfassung“ bei UTILMD AHB Gas
1.2, UTILMD AHB Strom 2.2 und INVOIC AHB 1.0b, sowie alte Datumsangaben wie „24.10.2023“.
Farbwert 1.0 (weiß), nicht sichtbar. Eine naive Textextraktion würde diese PDFs fälschlich
als Konsultationsfassung einstufen. Das ist für spätere automatische Klassifikationen
relevant. Die Liste steht je Dokument im Feld `deckblatt.unsichtbarer_resttext` der JSON.

---

## 8. Methodik und Abgrenzung

* **Ebene 1** (aktuelle Quelle): M56 vollständig, M55 nur zum Abgleich „konsultiert vs.
  veröffentlicht“, M57 zur Abgrenzung nach oben, BDEW-API als Gesamtabzug.
* **Nicht gelesen:** Mitteilungen < 54. Der Stand 01.04.2026 wird **nicht** rekonstruiert.
  Die Vorgängerspalte stammt unverändert aus `docs/befund_regulatorischer_stand_20260401.md`
  (Abschnitt C) und ist dort belegt.
* **Deckblattprüfung** nur Seite 1, deterministisch (pdfplumber, Farbwert je Wort). Keine
  Inhaltsanalyse.
* **Nicht committet:** die 34 PDFs (≈ 90 MB). Reproduzierbar über URL + SHA-256 in der
  JSON-Datei. Die HTML-Seiten der BNetzA sind nicht bytegleich reproduzierbar (dynamische
  Navigation), deshalb sind Textauszüge abgelegt.

---

## 9. Vorschlag für Etappe 1 (UTILMD-Pilot)

1. BDEW-PDFs für die 4 UTILMD-Dokumente laden (Basis + alle konsolidierten Stände), hashen,
   Deckblatt und Änderungshistorie auf Fehlerkorrekturstand prüfen.
2. Maßgebliche Fassung je Dokument nach Abschnitt 6 bestimmen. Erwartung **ohne Vorgriff**:
   AHB Gas 1.2 → Stand 06.08.2026, MIG Strom S2.2 → Stand 06.08.2026, AHB Strom 2.2 und
   MIG Gas G1.2 → Stand 29.06.2026. Zu belegen ist, dass es keine neueren Stände gibt und
   dass der BDEW-`validTo` der Vorstände nur „abgelöst“ bedeutet.
3. Fragenkatalog Abschnitt 8 (8 Fragen) je Dokument beantworten, Provenienzdatensatz nach
   Abschnitt 11 als JSON festlegen (Schema zur Bestätigung vorlegen).
4. Einführungsszenario UTILMD zum 01.10.2026 (BDEW-Anwendungshilfe 18.08.2026) auf
   abweichende Termine einzelner Segmente/Codes prüfen.

**Ticket:** #64
