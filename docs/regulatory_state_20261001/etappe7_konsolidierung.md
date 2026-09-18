# Etappe 7 — Konsolidierung, Widerspruchsprüfung, Regulatory-State-Objekt

**Ticket:** #64 · **Stichtag:** 01.10.2026 · **Erhebung:** 18.09.2026
**Grundlage:** Auftragsfassung „Etappe-7-Zwischenergebnis“ ([`auftrag.md`](auftrag.md)); alle
Provenienzdatensätze der Etappen 1–6; BDEW-Abzug `016a6f8c…01fb709f` (unverändert seit 17.09.).
**Status:** Etappe 7 abgeschlossen. Zur Bestätigung stehen zwei Punkte (Abschnitt 7 und 9).

Artefakt: [`etappe7_regulatory_state.json`](etappe7_regulatory_state.json) — das
Regulatory-State-Objekt nach Abschnitt 15 mit allen 85 maßgeblichen Dokumentversionen, Baum,
Kennzahlen, konsolidiertem Fragenkatalog und Vollständigkeitsprüfung. Es ist ein
Rechercheartefakt, kein Datenbankschreibvorgang (15a).

---

## 1. Zwischenstand (Abschnitt 13a)

| Kennzahl | Wert |
|---|---|
| Dokumente im State | **85** (alle `verbindlich` oder `verbindlich_fortgeltend`, keines `relevanz_unklar`) |
| Fassungen gesamt / maßgeblich | 402 / **86** (Verzeichnisdienst API: zwei Bestandteile, Schema v0.9) |
| Widersprüche BNetzA ↔ BDEW (Version oder Gültigkeit) | **0** |
| Bezeichnungsabweichung zwischen Quellen | 1 (O-14, PID 4.0 ↔ DVGW, nicht BNetzA ↔ BDEW) |
| offene Punkte | 8 (Abschnitt 9), davon 1 Produktentscheidung (P-1) |
| Vollständigkeit gegen BDEW | 90 von 90 Themen mit gültigem Eintrag erklärt (Abschnitt 3) |

## 2. Das Regulatory-State-Objekt

```text
Regulatory State
----------------
Name:               Marktkommunikation 01.10.2026
Stichtag:           01.10.2026
Basis:              BNetzA Mitteilung 56 (01.04.2026)
Fortgeltend aus:    Mitteilungen 19, 24, 33, 36, 43, 46, 51, 54, 58
Ergänzende Quellen: BDEW-MaKo · DVGW Service & Consult (SSQNOT) · GitHub EDI@Energy (API)
Status:             VALID (Vorschlag — gesetzt erst mit Bestätigung von Etappe 8)
```

| Zweig (Abschnitt 14) | Dokumente | Inhalt |
|---|---|---|
| EDIFACT | 37 | 18 Nachrichtentypen: je AHB + MIG, UTILMD 4 (Strom/Gas getrennt), SSQNOT 1 |
| XML | 28 | 9 Redispatch-/Kaskade-Formate × AWT/FB/XSD + Änderungshistorie |
| Codelisten | 8 | Konfigurationen, Verwendungszwecke, OBIS, Artikelnummern, Zeitreihentypen, Ländercodes, Lokationsbündel, SLP TU München |
| API | 4 | API-Guideline 1.0b; API-Webdienste Steuerungshandlungen, MaLo-ID, Verzeichnisdienst API (je 1.0.0) |
| Übertragungsweg | 3 | Regelungen zum Übertragungsweg 1.10, RzÜ API-Webdienste 1.2, Regelungen zum Verzeichnisdienst 1.1 |
| AS4 | 2 | AS4-Profil 1.2, RzÜ AS4 2.6 |
| PID · EBD · Sonstiges | 1 · 1 · 1 | PID 4.0 (Stand 12.08.2026) · EBD 4.3 (Stand 23.06.2026) · Allgemeine Festlegungen 6.1d |

Je Eintrag enthält das JSON: Version, gültig ab/bis, Status, Mitteilung, Aufnahmekriterium,
die maßgebliche(n) Fassung(en) mit Quelle, URL, SHA-256 und Mitteilungsbezug sowie den
Begründungssatz. Die vollständige Provenienz bleibt in den Etappendateien, auf die jeder Eintrag
verweist.

**Verhältnis zu `RegulatoryVersion` (9b, bestätigt):** Der State steht oberhalb der RVs, 1:n über
das nullable Feld `regulatory_state_id`. Zugeordnet wird nur **RV 2** (Mitteilung 56, Gas). RV 1
(Gas G1.1, ab 01.04.2026) und RV 3 (Strom 2.1, ab 06.06.2025) bleiben `NULL`.

> **P-1 bleibt offen und gehört sichtbar ins Ergebnis:** Der State enthält 81 Dokumente mit
> Strom-Bezug (36 Strom, 45 beide), hätte nach dem Modell aber nur die Gas-RV 2. Ob eine
> Strom-RV für den 01.10.2026 angelegt wird und was mit RV 3 geschieht, ist eine
> Produktentscheidung, kein Rechercheergebnis.

## 3. Vollständigkeitsprüfung gegen BDEW-MaKo

Geprüft gegen den unveränderten Abzug (1.752 Einträge):

* **231 Einträge** sind am 01.10.2026 gültig, verteilt auf **90 Themen**.
* **83 Themen** sind durch Datensätze abgedeckt. In diesen Themen gibt es **keinen** gültigen
  Eintrag, der nicht als Fassung erfasst ist, und **keinen** mit abweichender Versionsangabe.
* Die **7 übrigen Themen** sind genau die in Etappe 4 mit Negativbeleg ausgeschlossenen
  Dokumente: Temperaturanbieter, Anwendungshilfe Solarpaket, Gruppierungen, Änderungsantrag EBD,
  drei BDEW-Anwendungshilfen vom 18.08.2026.
* **0 Einträge** mit Gültigkeit nach dem Stichtag — Frage 6 ist damit auch von BDEW-Seite
  geschlossen.
* Außerhalb von BDEW: SSQNOT (DVGW). API-Webdienste und Verzeichnisdienst hängen an BDEW-Thema
  247 bzw. 241 (Verweis auf GitHub).

Ergebnis: Jeder am Stichtag bei BDEW gültige Eintrag ist entweder im State oder mit Beleg
ausgeschlossen.

## 4. Kernbefund K-1 im Endstand

| | Etappe 1–2 | Etappe 3–5 | Etappe 6 | **gesamt** |
|---|---|---|---|---|
| Dokumente | 36 | 12 | 37 | **85** |
| maßgebliche Fassung ohne Mitteilungsbezug | 11 | 9 | 18 | **38 (45 %)** |

Die 38 Fälle: 33 BDEW-Stände (29 konsolidierte Fehlerkorrekturstände, 4 außerordentliche
Veröffentlichungen — u. a. alle vier UTILMD, PID Stand 12.08.2026, EBD Stand 23.06.2026, acht
Redispatch-Stände vom 19.02.2026 und die SLP-Codeliste TU München, die nie Mitteilungsanlage
war), die Änderungshistorie XML (19.02.2026), die drei GitHub-Releases und SSQNOT (DVGW, keine
Mitteilungsreihe).

Über alle 402 Fassungen: 142 Mitteilungsanlagen bytegleich, 9 nicht bytegleich (textgleich,
zeilengleich oder anderer Dateistand), 33 Konsultationsanlagen, **216 ohne
Mitteilungsbezug**, 2 außerhalb der Mitteilungsreihe.

**Lesart für Etappe 8:** Fast jede zweite am Stichtag maßgebliche Fassung ist bei der BNetzA
nicht zu finden. Wer nur die Mitteilungen auswertet, liegt bei 38 von 85 Dokumenten auf einem
veralteten Stand — bei den zentralen Dokumenten UTILMD, PID und EBD ausnahmslos.

## 5. Fragenkatalog Abschnitt 8, konsolidiert

| Frage | Ergebnis über 85 Dokumente |
|---|---|
| 6 — neuere, veröffentlichte, noch nicht gültige Version | **0** (BNetzA: keine Inkrafttretens-Mitteilung nach Nr. 56; BDEW: kein Eintrag nach dem Stichtag) |
| 7 — Konsultationsfassung vorhanden | **25** Dokumente — genau die Liste der Mitteilung 57 (23 Dokumente) plus Release 2.0.0 für die zwei API-Webdienste Strom |
| 8 — Widerspruch BNetzA ↔ BDEW | **0** bei Version und Gültigkeit; 1 Bezeichnungsabweichung (O-14, PID ↔ DVGW) |

**Abweichungen, die keine Widersprüche sind** (belegt und erklärt, ohne Einfluss auf die
Auswahl):

| Fall | Erklärung |
|---|---|
| 7 M54-Anlagen nicht bytegleich | anders serialisiert; 5 textgleich, 2 zeilengleich |
| Lokationsbündel: M32-Anlage ≠ BDEW | M32 war Konsultation; M33-Anlage liefert HTTP 404 (O-15) |
| Verzeichnisdienst API: M46 v03 ≠ BDEW v04 | gleiche Version 1.0, abweichendes „Anzuwenden ab“ (03.04. ↔ 04.04.2025) |
| APERAK AHB 1.1 als „Informatorische Lesefassung“ verlinkt | bytegleich mit der BDEW-Basis (O-1, gelöst) |
| „StatusRequest_MarketDokument“ in M51 | Schreibfehler der Mitteilung; Datei bytegleich |
| Termine MaLo-ID | M43 „verbindlich ab 04.04.2025“ ↔ Release-Notiz/BDEW 06.06.2025; ohne Wirkung am Stichtag |

## 6. Sparte: belegt oder angenommen (11d)

| Belegart | Dokumente | Beispiele |
|---|---|---|
| belegt aus PID 4.0 (Spalten Strom/Gas) | 30 | 13 spartenübergreifende Nachrichtentypen, UTILTS (nur Strom), SSQNOT (Gas), EBD |
| belegt aus Titel/Deckblatt | 4 | UTILMD AHB/MIG Strom, Gas |
| belegt aus dem Dokument selbst | 1 | PID 4.0 |
| belegt aus Herkunft | 30 | Redispatch 2.0, Repository `api-electricity` (Strom) |
| belegt aus Referenzen (Etappe 7) | 7 | Allgemeine Festlegungen, Konfigurationen, OBIS, Ländercodes (beide); Zeitreihentypen, Lokationsbündel (Strom); SLP TU München (Gas) |
| **nur indirekt** | 2 | Verwendungszwecke, Artikelnummern: „beide“, aber keine Fundstelle in einem Gas-spezifischen Dokument |
| **angenommen, ohne Einzelnachweis** | 4 | **APERAK AHB/MIG, CONTRL AHB/MIG** — keine PID-Zeile; bleiben ausdrücklich getrennt von den belegten Fällen |
| **angenommen, ohne Spartenangabe** | 7 | RzÜ 1.10, AS4-Profil, RzÜ AS4, API-Guideline, RzV, RzÜ API, Verzeichnisdienst API |

## 7. Korrektur aus der Konsolidierung (zur Bestätigung)

Bei der Sparten-Auswertung fiel ein eigener Fehler aus Etappe 4 auf: Alle zehn
Querschnittsdokumente standen auf „beide“, mit der Pauschalbegründung „die Referenzen stammen aus
Dokumenten beider Sparten“. Die Referenzsuche über alle maßgeblichen Fassungen der Etappen 1–5
widerlegt das für drei Codelisten:

| Codeliste | Fundstellen | bisher | jetzt |
|---|---|---|---|
| Zeitreihentypen 1.1d | nur UTILMD MIG **Strom** (9) | beide | **Strom** |
| Lokationsbündelstrukturen 1.0 | nur UTILMD AHB **Strom** (2) | beide | **Strom** |
| Standardlastprofile nach TU München 1.1 | nur UTILMD AHB/MIG **Gas** (9) | beide | **Gas** |

Die Datensätze sind korrigiert und tragen je einen Hinweis `querpruefung`. Bei allen zehn steht
jetzt die tatsächliche Referenzverteilung im `sparte_beleg`. Die Versionsauswahl ändert sich
nicht. Das Skript liegt als `fix_e4_sparte.py` im Arbeitsverzeichnis.

## 8. Geprüft und ausgeschlossen (Negativbelege)

| Reihe / Dokument | Prüfung | Ergebnis |
|---|---|---|
| DVGW-Gastransport: TSIMSG, ALOCAT, IMBNOT, NOMINT, TRANOT, CHACAP, SCHEDL, DELRES, NOMRES, NÜVOR | je 0 Treffer in PID 4.0, keine Referenz | nicht im State (Aufnahmeregel §3) |
| Codeliste der Temperaturanbieter 1.0i | keine Mitteilung, keine PID-Zeile, 0 Referenzen | nicht im State |
| Gruppierungen EDI@Energy 2.2 · Änderungsantrag EBD 1.5 · Anwendungshilfe Solarpaket 1.1 | Übersicht, Formular, Anwendungshilfe | nicht im State |
| 3 BDEW-Anwendungshilfen (18.08.2026) | nur Gattungsnennung „Anwendungshilfe“ | nicht im State (11e) |
| GeLi Gas 3.0 | keine Formatwirkung, vertraglich | nicht im Dokumentbaum; Kontext für Abschnitt 12/16 |
| Konsultationen M57 (23 Dokumente) und Release 2.0.0 (zwei API-Dokumente) | nicht verbindlich | Frage 7 (25 Datensätze) |
| REQOTE MIG 1.3d · Verzeichnisdienst API 1.1 | konsultiert, nicht übernommen | nicht im State |

## 9. Register der offenen Punkte

| Punkt | Inhalt | Stand |
|---|---|---|
| **P-1** | Strom-RegulatoryVersion für 01.10.2026 fehlt | **Produktentscheidung offen** |
| **O-14** | PI 70096: „RLP“ (PID) ↔ „RLM“ (SSQNOT) | bewusst nicht aufgelöst |
| **O-5 (Rest)** | Name „SSQNOT zur Übermittlung von Mehr-/Mindermengen“ aus PID 4.0 existiert als Dokument nicht | offen, ohne Wirkung auf die Auswahl |
| **O-15** | Lokationsbündel: M33-Anlage HTTP 404, zwei Stände 12./13.12.2024 (Faktor 7) | offen |
| **O-17** | S_0088 (PI 55024) ohne Ziel | bewusst nicht aufgelöst |
| **O-19(b)** | RzV 1.1 ↔ API 1.0 | **Teilantwort zur Bestätigung:** RzV 4.6 setzt API 1.1 nicht voraus, die Pflicht hat aber kein Schnittstellenfeld |
| **O-20** | Kanalwechsel-Regel: Beleg „Inhalt unverändert“ bei allen drei API-Dokumenten nur indirekt | offene Beobachtung für Etappe 8 |
| **O-10** | MIG Gas G1.2: Vermerk „erst zum 1.4.2026“ | für die fachliche Analyse (12/16) |

Gelöst seit Etappe 0: O-1, O-2, O-3, O-4, O-6, O-7, O-8, O-9, O-11 (mit O-12), O-13, O-16, O-18,
O-19(a).

## 10. Nächster Schritt

Etappe 8: Übergabebericht als PR — K-1 (38 von 85) und K-2 prominent, dazu P-1, O-20 und die
Liste der Annahmen (Abschnitt 6). Voraussetzung: Bestätigung der Sparten-Korrektur
(Abschnitt 7) und der Teilantwort zu O-19(b).

**Ticket:** #64
