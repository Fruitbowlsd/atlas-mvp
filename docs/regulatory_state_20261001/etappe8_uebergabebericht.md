# Etappe 8: Übergabebericht Regulatory State 01.10.2026

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erstellt:** 18.09.2026
**Grundlage:** Auftragsfassung vom 18.09.2026, Stand O-20-Entscheidung ([`auftrag.md`](auftrag.md));
eingefrorene Datenbasis aus Etappe 7 ([`etappe7_regulatory_state.json`](etappe7_regulatory_state.json),
Merge-Commit `f3594f9`, Nachtrag `96a3371`).
**Status:** Entwurf, wartet auf Bestätigung. Erst danach wird der Status des Regulatory State auf
`VALID` gesetzt. Bis dahin beginnt keine fachliche Analyse (Abschnitt 12/16).

Dieser Bericht fasst nur zusammen. Er ändert keinen Datensatz, keine Rolle und keine Zahl aus
Etappe 7. Jede Aussage verweist auf das Etappendokument, in dem der Beleg steht.

---

## 1. Das Ergebnis in einem Satz

Zum 01.10.2026 gelten **85 Dokumente**. Für jedes ist die maßgebliche Fassung mit Quelle, URL
und SHA-256 belegt. Zwischen BNetzA und BDEW gibt es **keinen Widerspruch** bei Version oder
Gültigkeit. Die wichtigste Erkenntnis ist aber: **Bei 38 dieser 85 Dokumente steht die
maßgebliche Fassung in keiner BNetzA-Mitteilung** (K-1).

## 2. Was vollständig und belegt ist

| Kennzahl | Wert | Beleg |
|---|---|---|
| Dokumente im State | **85** (34 `verbindlich`, 51 `verbindlich_fortgeltend`) | Etappe 7, Abschnitt 1 |
| Fassungen gesamt | **402** | Etappe 7, Abschnitt 2 |
| maßgebliche Fassungen | **86**. Die Verzeichnisdienst-API besteht aus zwei gleichrangigen Bestandteilen, Web-API und WebSocket-API (Schema v0.9) | 11g, Etappe 6 |
| Rollen | `massgeblich` 86 · `ergaenzend` 102 · `ersetzt` 29 · `nicht_verbindlich` 33 · `informativ` 152 | JSON `kennzahlen.rollen` |
| Quelle der maßgeblichen Fassung | BDEW-MaKo 81 · GitHub EDI@Energy 4 · DVGW 1 | JSON `kennzahlen` |
| Widersprüche BNetzA ↔ BDEW (Version, Gültigkeit) | **0** | Etappe 7, Abschnitt 5 |
| neuere, schon veröffentlichte, noch nicht gültige Version (Frage 6) | **0** bei allen 85 | Etappe 7, Abschnitt 5 |
| Nachfolger in Konsultation (Frage 7) | **25** Dokumente: die 23 aus Mitteilung 57 plus Release 2.0.0 der zwei API-Webdienste Strom | Etappe 7, Abschnitt 5 |

**Vollständigkeit gegen BDEW:** Am Stichtag sind bei BDEW 231 Einträge in 90 Themen gültig.
83 Themen sind vollständig durch Datensätze abgedeckt. Die übrigen 7 sind genau die Dokumente,
die Etappe 4 mit Negativbeleg ausgeschlossen hat. Es gibt keinen gültigen BDEW-Eintrag ohne
zugehörige Fassung und keine Versionsabweichung (Etappe 7, Abschnitt 3).

**Aufbau nach Zweigen (Abschnitt 14):** EDIFACT 37 · XML 28 · Codelisten 8 · API 4 ·
Übertragungsweg 3 · AS4 2 · PID 1 · EBD 1 · Allgemeine Festlegungen 1.

**Verhältnis zum Datenmodell (9b, bestätigt):** Der State liegt eine Ebene über
`RegulatoryVersion`, als 1:n-Beziehung über das nullable Feld `regulatory_state_id`. Umgesetzt ist
davon noch nichts, siehe Abschnitt 9.

## 3. Kernbefund K-1: Die maßgebliche Fassung fehlt oft bei der BNetzA

> **38 von 85 Dokumenten (45 %)** haben bei der maßgeblichen Fassung **keinen
> Mitteilungsbezug**. Das betrifft UTILMD, PID und EBD ausnahmslos.

Die Zahl 38/85 ersetzt die Zwischenstände aus früheren Etappen, etwa 18/37 aus Etappe 6 oder
11/36 aus Etappe 1–2. Diese werden hier nicht mehr genannt.

**Das ist kein Zufall, sondern folgt aus dem Verfahren.** Die BNetzA veröffentlicht je Version
nur die Basisfassung als Mitteilungsanlage. Fehlerkorrekturen zwischen Veröffentlichung und
Inkrafttreten erscheinen nur bei BDEW, und dort als konsolidierte Fassung. Bei UTILMD, PID und
EBD ist die am Stichtag maßgebliche Fassung deshalb immer so ein Fehlerkorrekturstand, und der
hat keine eigene Mitteilungsanlage.

Belege (geprüft 18.09.2026, Ticket #64):

* Von den 38 Fällen sind **33 BDEW-Stände**: 29 konsolidierte Fehlerkorrekturstände und
  4 außerordentliche Veröffentlichungen. Die übrigen 5 sind die Änderungshistorie XML, die drei
  GitHub-Releases der API und SSQNOT von der DVGW, das außerhalb der Mitteilungsreihe steht.
* **32 der 33** BDEW-Stände erschienen **nach** der Mitteilung ihrer Version, 22 davon noch
  **vor** Gültigkeitsbeginn. Einzige Ausnahme ist die SLP-Codeliste TU München, die nie
  Mitteilungsanlage war.
* Die zentralen Dokumente folgen genau diesem Muster. Mitteilung 56 erschien am 01.04.2026.
  Danach kamen EBD (23.06.2026), UTILMD AHB Strom und MIG Gas (29.06.2026), UTILMD MIG Strom
  und AHB Gas (06.08.2026) und PID (12.08.2026). Alle diese Stände liegen vor dem
  01.10.2026.
* Die 95 Mitteilungen haben zusammen 1.319 Anlagen-Links. Keine einzige Datenformat-Anlage trägt
  „Fehlerkorrektur“ oder „konsolidiert“ im Namen. Die 4 Treffer sind Lesefassungen der
  Prozessfestlegungen GPKE, GeLi Gas, WiM und MaBiS.

**Was daraus folgt:** Wer nur die BNetzA-Mitteilungen auswertet, hat bei 38 von 85 Dokumenten
einen veralteten Stand. Bei UTILMD, PID und EBD trifft das immer zu. Für Atlas heißt das: Die
BDEW-Fehlerkorrekturstände sind für diese Dokumente die eigentliche Quelle, nicht nur eine
Ergänzung.

Über alle 402 Fassungen: 142 bytegleiche Mitteilungsanlagen, 9 nicht bytegleiche
Mitteilungsanlagen, 33 Konsultationsanlagen, 216 ohne Mitteilungsbezug, 2 außerhalb der
Mitteilungsreihe.

## 4. Kernbefund K-2: Für Gas reichen BNetzA und BDEW nicht

**SSQNOT** wird für die Prüfidentifikatoren 70095 und 70096 gebraucht. Das Dokument steht
in keiner der 95 Mitteilungen und in keinem der 1.752 BDEW-Einträge. Veröffentlicht wird es von
der **DVGW Service & Consult**, also einer dritten Quelle, die der Auftrag ursprünglich nicht
vorsah (Etappe 3, 11c).

Dass SSQNOT trotzdem in den State gehört, folgt aus der **Aufnahmeregel** und nicht aus einer
Einzelfallentscheidung ([`aufnahmeregel.md`](aufnahmeregel.md), 11e). Ein Dokument gehört
dazu, wenn mindestens eines dieser Kriterien erfüllt ist:

| | Kriterium |
|---|---|
| **A** | Anlage einer am Stichtag wirksamen Mitteilung der BK6/BK7-Reihe (unmittelbar oder fortgeltend) |
| **B** | in PID 4.0 in der Spalte „AHB“ oder als API-Webdienst geführt |
| **C** | von einem Dokument aus A oder B verbindlich referenziert. Ein Namensverweis ohne Version genügt nur, wenn geprüft ist, dass es genau ein passendes Dokument in genau einer gültigen Version gibt (Vermerk „versionslos, aber eindeutig“) |

SSQNOT erfüllt **B** (PID 4.0, Lfd. Nr. 12170/12180) und zusätzlich **C** (INVOIC AHB 1.0b,
S. 36, Bedingung [507]). Dieselbe Regel schließt die zehn übrigen DVGW-Gastransport-Typen aus:
TSIMSG, ALOCAT, IMBNOT, NOMINT, TRANOT, CHACAP, SCHEDL, DELRES, NOMRES und NÜVOR haben in PID 4.0
jeweils 0 Treffer. Der Ausschluss ist damit belegt und nicht nur behauptet.

## 5. Produktentscheidung P-1: Der State hängt nur an der Gas-RV

Laut 9b verweist nur **RV 2** (Mitteilung 56, Gas) auf den Regulatory State 01.10.2026. Der State
enthält aber **81 Dokumente mit Strom-Bezug** (36 nur Strom, 45 beide Sparten). Für den
01.10.2026 gibt es keine Strom-`RegulatoryVersion`. RV 3 (Strom 2.1, ab 06.06.2025) und RV 1
(Gas G1.1) bleiben ohne Verknüpfung.

Ob eine Strom-RV angelegt wird und was mit RV 3 geschieht, entscheidet das Produkt, nicht die
Recherche. Das ist bewusst **nicht Teil dieses Auftrags**, darf aber im Ergebnis nicht
untergehen.

## 6. Offene Beobachtung O-20: Regel R-6b hat derzeit keinen Anwendungsfall

**O-20 ist entschieden, aber nicht gelöst** (11g, Commit `96a3371`).

Regel R-6b (siehe [`rollendefinition.md`](rollendefinition.md)) betrifft den Fall, dass eine
Version gleich bleibt und nur ihr Veröffentlichungsweg wechselt. Die alte Fassung wird dann nur
`ersetzt`, wenn **beides** belegt ist: Der Inhalt ist nachweislich unverändert, **und** der
neue Weg ist regulatorisch geregelt.

Bei den drei API-Dokumenten (Steuerungshandlungen, MaLo-ID, Verzeichnisdienst) ist der neue Weg
geregelt, nämlich über GitHub-Releases nach API-Guideline 1.0b. Einen **Beleg für
unveränderten Inhalt gibt es aber nicht**:

* Die alten BDEW-PDFs (7313, 7314, 7650) sind reine Linkblätter mit rund 1.100 Zeichen, ohne
  Pfade und ohne Schemas.
* Sie verlinken auf SwaggerHub. Dort sind die Spezifikationen gelöscht (HTTP 404), und das
  Internet Archive hat keinen Inhalt gespeichert.
* Der Bytevergleich aus Etappe 6 verglich nur PDF mit PDF (BNetzA ↔ BDEW), nicht die
  Spezifikationen selbst.
* Übrig bleibt nur die Erklärung des Herausgebers in der Release-Notiz, es habe keine
  inhaltlichen Änderungen gegeben.

**Stand:** Die drei PDFs sind `ergaenzend`, die OpenAPI-/YAML-Dateien bleiben `massgeblich`. R-6b
gilt weiter als Regel, hat derzeit aber **keinen erfüllten Anwendungsfall**. Kriterium A
(Mitteilungsbezug über die Mitteilungen 36, 43 und 46) ist für alle drei Dokumente davon nicht
berührt.

## 7. Eigenständiger Befund: Ankündigungspflicht ohne Schnittstellenfeld (RzV 1.1, Kap. 4.6)

*Dieser Befund steht absichtlich getrennt von O-19(b).*

Kapitel 4.6 der **Regelungen zum Verzeichnisdienst 1.1** verlangt, die **Einstellung des
Betriebs** „mit ausreichendem Vorlauf“ anzukündigen. Die gültige **Verzeichnisdienst API 1.0.0**
hat dafür **kein Schnittstellenfeld**. Die Felder, die das abbilden würden (`ServiceInfo.status`,
`ServiceInfo.activeUntil`), gibt es erst in Version 1.1. Die wurde mit Mitteilung 48 konsultiert,
aber nie verbindlich übernommen (Etappe 6, 11g).

Der Regelungstext schreibt also eine Pflicht vor, für die die gültige Schnittstelle keinen
technischen Weg bietet. Wie die Ankündigung am Stichtag tatsächlich übermittelt wird, lässt sich
aus den Quellen nicht belegen.

*Zur Abgrenzung von O-19(b), das bestätigt beantwortet ist:* RzV 1.1 setzt API 1.1 nicht
voraus, weil Kap. 4.6 keinen technischen Weg vorschreibt. Das ist richtig und erklärt trotzdem
nicht, wo die Ankündigung technisch landen soll. Genau diese Lücke beschreibt der Befund hier.

## 8. Was bewusst offen bleibt

| Punkt | Inhalt | Warum offen |
|---|---|---|
| **O-14** | PI 70096 heißt in PID 4.0 (S. 27) „Mehr-/Mindermengenmeldung **RLP**“, in SSQNOT 5.7 (S. 12) „… **RLM**“ | Welche Bezeichnung fachlich stimmt, lässt sich aus den Quellen nicht belegen. Beide Werte bleiben unverändert stehen. Auf die Versionsauswahl hat das keinen Einfluss. Das ist die einzige Markierung „Widerspruch: ja“ im Fragenkatalog (Frage 8), und sie betrifft PID ↔ DVGW, nicht BNetzA ↔ BDEW |
| **O-15** | Lokationsbündel-Codeliste: Die Anlage zu Mitteilung 33 liefert HTTP 404. Es gibt zwei BDEW-Stände vom 12. und 13.12.2024 (0,96 MB gegen 6,7 MB) | Ein Byte-Beleg für die Mitteilungsanlage ist derzeit nicht möglich. Warum es zwei Stände gibt, ist nicht belegbar. Maßgeblich ist der neueste Stand 7713. Mitteilung 57 kündigt an, dass die Liste zum 01.04.2027 wegfällt |
| **O-17** | PID Zeile 26100, PI 55024: Die Codelisten-Kennung **S_0088** gibt es in EBD 4.3 nicht (dort endet die Reihe bei S_0087) und in keinem anderen maßgeblichen Dokument | Das ist ein Dokumentfehler und damit regulatorische Realität. Er wird bewusst nicht auf eine ähnliche Kennung „korrigiert“. Auch der Stand vom 12.08.2026 enthält ihn noch |
| O-5 (Rest) | Ein Dokument mit dem Namen aus PID 4.0, „SSQNOT zur Übermittlung von Mehr-/Mindermengen“, gibt es nicht | Dass damit die DVGW-Beschreibung gemeint ist, liegt nahe, ist aber nicht ausdrücklich belegt. Auf die Auswahl hat das keinen Einfluss |
| O-10 | UTILMD MIG Gas G1.2, S. 168: Vermerk „erst zum 1.4.2026“ | Wahrscheinlich aus G1.1 übernommen. Wegen des Spaltenlayouts lässt sich der Vermerk keiner Änd-ID sicher zuordnen. Das gehört in die fachliche Analyse (Abschnitt 12) |
| P-1 | fehlende Strom-RV | Produktentscheidung, siehe Abschnitt 5 |
| O-20 | R-6b ohne Anwendungsfall | offene Beobachtung, siehe Abschnitt 6 |

Seit Etappe 0 gelöst: O-1, O-2, O-3, O-4 (mit der Korrektur aus O-20), O-6, O-7, O-8, O-9,
O-11 (mit O-12), O-13, O-16, O-18, O-19(a), O-19(b). **Keine Rückfrage blockiert die
Bestätigung dieses Berichts.**

## 9. Was bewusst nicht vertieft wurde

**Sparten-Zuordnung ohne Einzelbeleg (11d).** Die Sparte ist bei 72 Dokumenten belegt, bei
den übrigen 13 nicht gleich stark:

| Belegart | Anzahl | Dokumente | Begründung |
|---|---|---|---|
| angenommen, ohne Einzelnachweis | 4 | **APERAK AHB/MIG, CONTRL AHB/MIG** („beide“) | Anders als die 13 übrigen spartenübergreifenden Nachrichtentypen haben sie keine eigene PID-Zeile. Ein Einzelbeleg wie bei den anderen fehlt, und das bleibt sichtbar |
| angenommen, ohne Spartenangabe | 7 | RzÜ 1.10, AS4-Profil, RzÜ AS4, API-Guideline, RzV, RzÜ API, Verzeichnisdienst API | Regelwerke ohne Spartenangabe im Dokument |
| nur indirekt | 2 | Verwendungszwecke, Artikelnummern („beide“) | Kein Verweis aus einem Gas-spezifischen Dokument |

Die Versionsauswahl hängt an keiner dieser Annahmen, nur die Spartenkennzeichnung. Eine Klärung
gehört in die fachliche Analyse.

**Ebenfalls nicht vertieft:**

* **Inhalt der Konsultationsfassungen** (25 Dokumente, Mitteilung 57, Release 2.0.0). Sie sind
  am Stichtag nicht verbindlich und nur als `nicht_verbindlich` erfasst, ohne inhaltlichen
  Vergleich.
* **Gastransport und Kooperationsvereinbarung Gas** (DVGW-Reihe ohne SSQNOT). Sie fallen nicht
  unter die Aufnahmeregel, der Ausschluss ist belegt (Abschnitt 4).
* **GeLi Gas 3.0.** Sie hat keine Formatwirkung, sondern regelt Verträge. Sie ist nicht im
  Dokumentbaum und dient als Kontext für Abschnitt 12/16.
* **Sieben BDEW-Themen ohne Aufnahme:** Temperaturanbieter, Gruppierungen, Änderungsantrag EBD,
  Anwendungshilfe Solarpaket und drei Anwendungshilfen vom 18.08.2026. Ausgeschlossen jeweils
  mit Negativbeleg (Etappe 4).
* **Früherer Inhalt der API-Spezifikationen.** Er lässt sich nicht rekonstruieren (SwaggerHub
  gelöscht, siehe O-20).
* **Das reale Postgres-Schema.** Der Auftrag bleibt bei Rechercheartefakten (15a). Vor einer
  Migration nach 9b müssen Migrationen und ORM-Modelle unter `backend/` direkt eingesehen werden.
* **Fachliche Inhalte der Dokumente** (Prozesse, Prüfidentifikatoren, Segmentregeln). Das ist
  ausdrücklich Abschnitt 12/16 und beginnt erst nach Bestätigung dieses Berichts.

## 10. `relevanz_unklar`

**Keine Markierung offen.** Alle 85 Dokumente sind `verbindlich` oder
`verbindlich_fortgeltend` (JSON `kennzahlen.relevanz_unklar = []`). Der einzige zwischenzeitlich
unklare Fall war die Codeliste Standardlastprofile nach TU München. Er ist über Kriterium C mit
dem Vermerk „versionslos, aber eindeutig“ geklärt (O-18, 11e).

## 11. Zur Bestätigung

1. Den Bericht bestätigen. Damit wird der Status des Regulatory State von „Vorschlag“ auf
   `VALID` gesetzt, als Eintrag im JSON und nicht in der Datenbank.
2. P-1 als Produktentscheidung einplanen, getrennt von diesem Auftrag.
3. Freigeben, dass die fachliche Analyse nach Abschnitt 12/16 beginnen darf.

**Ticket:** #64
