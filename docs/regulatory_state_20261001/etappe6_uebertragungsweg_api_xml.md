# Etappe 6 — Übertragungsweg, AS4, API-Webdienste, XML-Datenformate (Redispatch 2.0)

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 18.09.2026
**Grundlage:** Auftragsfassung „Stand nach O-18“ ([`auftrag.md`](auftrag.md)); Aufnahme nach
[`aufnahmeregel.md`](aufnahmeregel.md); Rollen nach [`rollendefinition.md`](rollendefinition.md)
mit der neuen Ergänzung R-6a bis R-6c.
**Status:** Etappe 6 abgeschlossen. Zur Bestätigung stehen Schema v0.8, die Regelergänzungen
R-6a–c und der Zuschnitt der API-Dokumente.

Artefakt: [`etappe6_uebertragungsweg_api_xml_provenienz.json`](etappe6_uebertragungsweg_api_xml_provenienz.json)
(37 Datensätze, 149 Fassungen, Schema **v0.8**). Alle 85 Datensätze der Etappen 1–6 sind
gegen v0.8 valide.

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| Dokumente aufgenommen und belegt | **37** (27 Redispatch-Formate, 1 Änderungshistorie, 6 Regelwerke, 3 API-Dokumente) |
| erfasste Fassungen | 149 (PDF, XSD und OpenAPI-YAML geladen und gehasht; Excel/Word nicht geladen) |
| maßgeblich als PDF / XSD / YAML | 25 / 9 / 3 |
| maßgebliche Fassung **ohne Mitteilungsbezug** | **18 von 37** (14 konsolidierte Stände, 1 Änderungshistorie, 3 GitHub-Releases) |
| offene Fälle neu | **1** (O-19, zwei Teilfragen) |
| gelöst | **O-4** (API-Webdienste, aus Etappe 0) |
| Widersprüche zwischen BNetzA und BDEW | **0** |

Die Zahl für K-1 wächst damit deutlich: In Etappe 6 hat fast **jede zweite** maßgebliche
Fassung keinen Mitteilungsbezug (Etappe 1–2: 11 von 36). Der Endstand wird in Etappe 7
über alle Etappen gezählt.

## 2. Ergebnis

| Dokument | Version | Mitt. | gültig ab | maßgebliche Fassung | Bezug zur Mitteilungsanlage | Aufnahme |
|---|---|---|---|---|---|---|
| AcknowledgementDocument AWT | 1.0g | 54 | 01.04.2026 | Basis (bdew:8166, PDF) | zeilengleich | A |
| AcknowledgementDocument FB | 1.0g | 54 | 01.04.2026 | Basis (bdew:8180, PDF) | textgleich | A |
| AcknowledgementDocument XSD | 1.0g | 54 | 01.04.2026 | Basis (bdew:8171, XSD) | bytegleich | A |
| ActivationDocument AWT | 1.1f | 54 | 01.04.2026 | Basis (bdew:8168, PDF) | zeilengleich | A |
| ActivationDocument FB | 1.1f | 54 | 01.04.2026 | konsolidiert 19.02.2026 (bdew:8267, PDF) | **keiner** | A |
| ActivationDocument XSD | 1.1f | 54 | 01.04.2026 | konsolidiert 19.02.2026 (bdew:8266, XSD) | **keiner** | A |
| Kostenblatt AWT | 1.0d | 51 | 01.10.2025 | konsolidiert 05.09.2025 (bdew:8087, PDF) | **keiner** | A |
| Kostenblatt FB | 1.0d | 51 | 01.10.2025 | konsolidiert 16.04.2025 (bdew:7959, PDF) | **keiner** | A |
| Kostenblatt XSD | 1.0d | 51 | 01.10.2025 | konsolidiert 16.04.2025 (bdew:7960, XSD) | **keiner** | A |
| NetworkConstraintDocument AWT | 1.1b | 51 | 01.10.2025 | Basis (bdew:7923, PDF) | bytegleich | A |
| NetworkConstraintDocument FB | 1.1b | 51 | 01.10.2025 | Basis (bdew:7921, PDF) | bytegleich | A |
| NetworkConstraintDocument XSD | 1.1b | 51 | 01.10.2025 | Basis (bdew:7934, XSD) | bytegleich | A |
| PlannedResourceScheduleDocument AWT | 1.0f | 51 | 01.10.2025 | Basis (bdew:7935, PDF) | bytegleich | A |
| PlannedResourceScheduleDocument FB | 1.0f | 51 | 01.10.2025 | konsolidiert 19.02.2026 (bdew:8272, PDF) | **keiner** | A |
| PlannedResourceScheduleDocument XSD | 1.0f | 51 | 01.10.2025 | konsolidiert 19.02.2026 (bdew:8273, XSD) | **keiner** | A |
| Stammdaten AWT | 1.4b | 51 | 01.10.2025 | Basis (bdew:7939, PDF) | bytegleich | A |
| Stammdaten FB | 1.4b | 51 | 01.10.2025 | konsolidiert 19.02.2026 (bdew:8274, PDF) | **keiner** | A |
| Stammdaten XSD | 1.4b | 51 | 01.10.2025 | konsolidiert 19.02.2026 (bdew:8275, XSD) | **keiner** | A |
| StatusRequest_MarketDocument AWT | 1.1 | 51 | 01.10.2025 | Basis (bdew:7920, PDF) | bytegleich | A |
| StatusRequest_MarketDocument FB | 1.1 | 51 | 01.10.2025 | Basis (bdew:7918, PDF) | bytegleich | A |
| StatusRequest_MarketDocument XSD | 1.1 | 51 | 01.10.2025 | Basis (bdew:7943, XSD) | bytegleich | A |
| Unavailability_MarketDocument AWT | 1.1b | 51 | 01.10.2025 | Basis (bdew:7917, PDF) | bytegleich | A |
| Unavailability_MarketDocument FB | 1.1b | 51 | 01.10.2025 | konsolidiert 16.04.2025 (bdew:7965, PDF) | **keiner** | A |
| Unavailability_MarketDocument XSD | 1.1b | 51 | 01.10.2025 | konsolidiert 16.04.2025 (bdew:7966, XSD) | **keiner** | A |
| Kaskade AWT | 1.0 | 54 | 01.04.2026 | Basis (bdew:8173, PDF) | textgleich | A |
| Kaskade FB | 1.0 | 54 | 01.04.2026 | konsolidiert 19.02.2026 (bdew:8270, PDF) | **keiner** | A |
| Kaskade XSD | 1.0 | 54 | 01.04.2026 | konsolidiert 19.02.2026 (bdew:8271, XSD) | **keiner** | A |
| Änderungshistorie XML-Datenformate | — | 54 | 01.04.2026 | Publikation 19.02.2026 (bdew:8268, PDF) | **keiner** | A |
| Regelungen zum Übertragungsweg | 1.10 | 56 | 01.10.2026 | Basis (bdew:8317, PDF) | bytegleich | A |
| AS4-Profil | 1.2 | 56 | 01.10.2026 | Basis (bdew:8316, PDF) | bytegleich | A |
| Regelungen zum Übertragungsweg für AS4 | 2.6 | 56 | 01.10.2026 | Basis (bdew:8318, PDF) | bytegleich | A |
| API-Guideline | 1.0b | 56 | 01.10.2026 | Basis (bdew:8329, PDF) | bytegleich | A |
| Regelungen zum Verzeichnisdienst | 1.1 | 51 | 01.10.2025 | Basis (bdew:7846, PDF) | bytegleich | A |
| Regelungen zum Übertragungsweg für API-Webdienste | 1.2 | 51 | 01.10.2025 | konsolidiert 18.07.2025 (bdew:8053, PDF) | **keiner** | A |
| API-Webdienste … Steuerungshandlungen (iMS) | 1.0.0 | 36 | 01.04.2024 | Release 1.0.0 (controlMeasuresV1.yaml, YAML) | **keiner** | A + B |
| API-Webdienste zur Ermittlung der MaLo-ID der Marktlokation | 1.0.0 | 43 | 04.04.2025 | Release 1.0.0 (maloIdentV1.yaml, YAML) | **keiner** | A + B |
| Verzeichnisdienst API | 1.0.0 | 46 | 04.04.2025 | Release 1.0.0 (directoryServiceV1.yaml, YAML) | **keiner** | A + C |

**Gültig bis** ist bei allen 37 Dokumenten offen. Nachfolger in Konsultation (Mitteilung 57,
für den 01.04.2027): ActivationDocument AWT 1.1g, Änderungshistorie, Regelungen zum
Übertragungsweg 1.11, RzÜ API-Webdienste 1.3, API-Guideline 1.0c und API-Webdienste Strom
Release 2.0.0.

**Stand-Reihen:** Konsolidierte Stände gibt es zu drei Terminen — 16.04.2025 (4 Dokumente),
05.09.2025 bzw. 18.07.2025 (je 1) und **19.02.2026 (8)**. Am 19.02.2026 hat BDEW
Fehlerkorrekturen zu den Mitteilungen 51 **und** 54 zugleich veröffentlicht; keine davon ist
Anlage einer Mitteilung.

## 3. API-Webdienste — O-4 gelöst, und zwar über Kriterium A

Etappe 0 hatte O-4 offen gelassen, weil keine Mitteilung den Wechsel von den BDEW-PDFs zu
den GitHub-Releases als verbindlich ausweist. Die Volltextsuche in allen 95 Mitteilungen
zeigt jetzt: Die **Versionen** stammen aus verbindlichen Mitteilungen, nur ihr
**Veröffentlichungsweg** hat sich geändert.

| Dokument | Version aus | Anlage bytegleich mit BDEW | seit 29.01.2026 |
|---|---|---|---|
| API-Webdienste … Steuerungshandlungen (iMS) | **Mitteilung 36** (verbindlich ab 01.04.2024) | ja, bdew:7313 | Release 1.0.0, `controlMeasuresV1.yaml` |
| API-Webdienste zur Ermittlung der MaLo-ID | **Mitteilung 43** (verbindlich ab 04.04.2025) | ja, bdew:7314 | Release 1.0.0, `maloIdentV1.yaml` |
| Verzeichnisdienst API | **Mitteilung 46** (verbindlich ab 04.04.2025) | **nein** (M46: Dateistand v03, BDEW: v04) | Release 1.0.0, `directoryServiceV1.yaml` + `webSocketV1.yaml` |

Die Kette ist lückenlos belegt:

1. Die alten PDFs (je 3 Seiten) verweisen nur auf die Spezifikation bei SwaggerHub.
2. Mitteilung 55 meldet den Umzug „von Swagger auf die Plattform GitHub“, beschlossen in der
   Konzeptkonsultation (Mitteilung 53).
3. Die API-Guideline 1.0b (Anlage der Mitteilung 56, **Kriterium A**) legt in Kap. 4
   (S. 15–16) fest, dass API-Webdienste über GitHub-Releases versioniert und veröffentlicht
   werden.
4. Die Release-Notiz 1.0.0 beider Repositories: „Überführung … von Swagger auf GitHub ohne
   inhaltliche Änderungen“.
5. Mitteilung 56 schließt Release 2.0.0 ausdrücklich aus.
6. Die OpenAPI-Titel stimmen wörtlich mit den Namen in PID 4.0 überein (**Kriterium B**):
   API00001/API00002 → Steuerungshandlungen (24 Zeilen, S. 43–46), API00003 → MaLo-ID
   (3 Zeilen, S. 31).

Die maßgeblichen Fassungen sind die OpenAPI-Dateien am Release-Tag 1.0.0 mit SHA-256 und
Commit (`api-electricity` 4b4bfde6…, `api-directory-service` 74a01c6b…). Die BDEW-PDFs sind
nach R-6b `ersetzt`; die BNetzA-Anlagen bleiben `ergaenzend`, weil nur sie die Version mit
der Mitteilung verbinden.

**Release 2.0.0** (`api-electricity`, veröffentlicht 24.07.2026, Ziel-Branch
`2026-07-31-consultation`) ist ein Konsultations-Release. Seine Notiz nennt „anzuwenden ab
01.10.2027“, Mitteilung 57 als Regeltermin den 01.04.2027, zugleich aber den Vorschlag, die
produktive Anwendung zum 01.10.2027 sicherzustellen. Für den Stichtag hat das keine Wirkung;
es steht als `abweichender_termin` im Datensatz.

**Zuschnitt (zur Bestätigung):** API-Webdienste Strom sind **zwei** Dokumente — so führen sie
PID 4.0 und die Mitteilungen 36/43, und so hießen sie bei BDEW bis 28.01.2026. Der
BDEW-Sammeleintrag „API-Webdienste Strom – Release 1.0.0“ (Thema 247) ist nur der Verweis auf
das Repository. Die Verzeichnisdienst API bleibt **ein** Dokument, denn sie ist eine Anlage
(M46) und wird als ein Dokument mit zwei Kapiteln zitiert.

## 4. Verzeichnisdienst API — Kriterium C „versionslos, aber eindeutig“ (zweiter Fall)

Die Regelungen zum Verzeichnisdienst 1.1 (Anlage M51) verweisen auf S. 14 auf die „Kapitel
‚Web-API‘“ und „‚WebSocket-API‘ in EDI@Energy-Dokument ‚Verzeichnisdienst API‘“ — **ohne
Version**. Die Eindeutigkeit wurde nach 11e je Fall geprüft, nicht aus dem SLP-Fall übernommen:

* **BDEW (1.752):** nur Thema 241 — 7650 „Verzeichnisdienst API 1.0“ (Plattformgültigkeit bis
  28.01.2026), 8232/8233 Release 1.0.0 ab 29.01.2026. Am Stichtag genau eine Version.
* **95 Mitteilungen:** Anlage in M44 (Konsultation), **M46 (verbindlich)** und **M48:
  Konsultationsfassung einer Version 1.1** (Anzuwenden ab 01.10.2025). Version 1.1 erscheint
  in keiner verbindlichen Mitteilung und nicht bei BDEW.
* **GitHub:** genau ein Repository, genau ein Release; die beiden Dateititel entsprechen
  wörtlich den zitierten Kapitelnamen.
* **BDEW-Marktprozesse (102):** kein Treffer.

Ergebnis: genau ein Dokument, genau eine gültige Version. Die Version 1.1 ist ein ähnlich
benannter Stand **desselben** Dokuments. Nach der O-18-Regel („taucht ein ähnlich benanntes
Dokument auf, neu bewerten“) ist sie ausdrücklich bewertet und nicht übergangen. Da
Kriterium A (M46) die Aufnahme bereits trägt, ist C hier nur Zusatzbeleg.

## 5. Mitteilung 54: nicht bytegleich, aber inhaltsgleich — Korrektur einer Zwischenmeldung

Die sieben PDF-Anlagen der Mitteilung 54 sind mit keiner BDEW-Datei bytegleich (anders
serialisiert). Die XSD-Anlagen sind bytegleich. Beim Volltextvergleich (pdfminer):

* **5 textgleich** (Text-SHA-256 identisch): Acknowledgement FB, Activation FB, Kaskade AWT,
  Kaskade FB, Änderungshistorie.
* **2 zeilengleich:** Acknowledgement AWT 1.0g, Activation AWT 1.1f. Gleiche Zeilenmenge und
  Zeichenzahl (67.686 bzw. 60.226); verschieden ist allein die Reihenfolge der
  Fußnotenmarken [1]–[4] im extrahierten Textstrom.

**Korrektur:** Meine Zwischenmeldung „alle 7 textgleich, 0 Abweichungen“ war zu grob. Die
Aussage „inhaltlich identisch“ bleibt richtig, die Unterscheidung steht jetzt im Datensatz.

Ebenfalls klargestellt: Die Anlagen-Links der Mitteilung 54 enden auf `.html` und liefern die
Datei direkt. Die Varianten `.pdf`/`.xml`/`.xsd`, die ich zusätzlich abgerufen hatte, geben
dieselben Bytes zurück — das ist eine Eigenschaft des Servers, keine dreifache
Veröffentlichung. In den Datensätzen steht der amtliche `.html`-Link.

## 6. Regelergänzungen und Schema v0.8 (zur Bestätigung)

Drei Fassungsarten kannten die Rollenregeln bisher nicht (Schritt 8: „keine stille
Einordnung“). Sie sind in [`rollendefinition.md`](rollendefinition.md) ergänzt:

* **R-6a — kein PDF:** XSD und OpenAPI-YAML *sind* das Dokument; Abschnitt 7 greift nicht,
  die Stand-Reihe läuft im Dokumentformat. Betrifft 9 XSD- und 3 API-Dokumente.
* **R-6b — Wechsel des Veröffentlichungswegs** bei gleicher Version: alte Fassung `ersetzt`,
  nur mit Beleg für unveränderten Inhalt und geregelten neuen Weg.
* **R-6c — versionsloses Dokument:** Stand-Reihe nach Publikationsdatum (Änderungshistorie;
  maßgeblich ist die Veröffentlichung vom 19.02.2026, keine Mitteilung).

**Schema v0.8** ergänzt nur die Quelle `GitHub-EDI@Energy` und in `quelle_ref` die Felder
Repository, Tag, Commit, Pfad und Veröffentlichungszeitpunkt (nach dem Vorbild DVGW in v0.4).
Keine Pflichtfelder neu, alle älteren Datensätze bleiben valide.

## 7. Weitere Befunde (als Hinweise im Datensatz, ohne Wirkung auf die Auswahl)

* **Vorversionen in Mitteilung 51:** AcknowledgementDocument 1.0f und ActivationDocument
  1.1e (verbindlich ab 01.10.2025) sind durch Mitteilung 54 zum 01.04.2026 abgelöst.
* **„MarketDokument“:** Mitteilung 51 schreibt StatusRequest_Market**Dokument** FB; die Datei
  ist bytegleich — ein Schreibfehler in der Mitteilung.
* **Stammdaten FB, Stand 19.02.2026:** Das Deckblatt nennt als „ursprüngliches
  Publikationsdatum“ den 16.04.2025 (den vorigen Korrekturstand), die übrigen Fassungen den
  01.04.2025.
* **Kaskade-XSD** nutzt denselben targetNamespace wie Unavailability_MarketDocument XSD
  (`…451-6:outagedocument:3:0`). Beobachtung, keine Bewertung.
* **Änderungshistorie:** Die Anlage der Mitteilung 51 (01.04.2025) liegt bei BDEW nicht als PDF
  vor.
* **Termine API:** Mitteilung 43 nennt für die MaLo-ID „verbindlich ab 04.04.2025“, Release-Notiz
  und BDEW den 06.06.2025. Für den Stichtag ohne Wirkung.
* **Änderungshistorien der Einzelfassungen** sind in dieser Etappe nicht ausgewertet
  (`aenderungshistorie = null`); das ändert keine Auswahl.

## 8. Offener Punkt

**O-19 (neu) — Verzeichnisdienst API:**
(a) Der Release besteht aus zwei gleichrangigen Dateien, das Schema erlaubt aber nur eine
maßgebliche Fassung je Dokumentversion. Vorläufig ist die Web-API `massgeblich` und die
WebSocket-API `ergaenzend`. Das ist eine **Modellentscheidung**, die ich nicht selbst treffe.
(b) Version 1.1 wurde konsultiert (M48), aber nie verbindlich veröffentlicht. Die Regelungen
zum Verzeichnisdienst 1.1 verweisen ohne Version. Ob sie inhaltlich die API 1.0 voraussetzen,
ist nicht geprüft.

## 9. Nächste Schritte

Etappe 7: Konsolidierung über alle 85 Datensätze, Widerspruchsprüfung, Regulatory-State-Objekt
mit P-1, Negativbelege der ausgeschlossenen Reihen und K-1 im Endstand.

**Ticket:** #64
