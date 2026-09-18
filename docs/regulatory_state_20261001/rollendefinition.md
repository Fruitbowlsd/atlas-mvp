# Rollen einer Fassung — „ersetzt“ ist nicht „verworfen“

**Ticket:** #64 · gilt ab Schema v0.1 (`provenienz_schema.json`, Feld `fassungen[].rolle`), erweitert in v0.2/v0.3 um Fassungen ohne Mitteilungsbezug (O-11, **vom Nutzer bestätigt am 17.09.2026**)

> Hinweis zur Herkunft: Der Auftrag hat keinen Abschnitt 11a. Diese Definition geht auf deine
> Ergänzung vom 17.09.2026 zurück und ist seit Commit 4617854 schriftlich festgelegt; hier
> kommt die Anwendung auf den O-11-Fall dazu.

## Grundsatz

Keine gefundene Fassung wird aus einem Datensatz entfernt oder als ungültig gestrichen
(Auftrag Abschnitt 10: Versionen nie überschreiben; Arbeitsweise: kein Feld geht still
verloren). Jede Fassung bekommt eine Rolle, die ihr Verhältnis zur maßgeblichen Fassung
beschreibt, und behält Hash, URL und Belege.

> **Korrektur am 18.09.2026:** Bis Schema v0.5 kannte dieses Dokument die Rolle `verworfen`
> bewusst nicht. Der Auftrag (Abschnitt 11a) führt sie jedoch ausdrücklich. Ab **v0.6** gibt
> es sie deshalb, mit der Definition des Auftrags: *fehlerhaft oder zurückgezogen, unabhängig
> vom Vorhandensein einer neueren Fassung.* Sie ist damit **keine** Abstufung von `ersetzt`,
> sondern ein Qualitätsurteil über die Fassung selbst und verlangt einen ausdrücklichen Beleg.
> **Vergeben ist sie derzeit an keine einzige der 209 Fassungen** (Begründung unten).

## Die fünf Rollen

| Rolle | Bedeutung | Kriterium | Zeitbezug |
|---|---|---|---|
| `massgeblich` | Die Fassung, die am Stichtag gilt | genau eine je Dokumentversion; PDF (ohne PDF: die Fachdatei, R-6a). **Ausnahme ab v0.9:** Bilden mehrere Fassungen über dieselbe `bestandteil_gruppe` gemeinsam die Dokumentversion, ist je `bestandteil` genau eine maßgeblich | — |
| `ergaenzend` | Nicht maßgeblich, aber fachlich **nötig**, weil sie Information enthält, die der maßgeblichen Fassung fehlt | Basis-PDF, sobald eine konsolidierte Fassung existiert (einzige Quelle der Änderungshistorie gegenüber der Vorversion); ohne konsolidierte Fassung ist die Basis selbst maßgeblich | — |
| **`ersetzt`** | **Zeitlich abgelöst.** Fassung eines **älteren Fehlerkorrekturstands derselben Version**. Zu ihrem Zeitpunkt war sie der richtige Stand, inzwischen gibt es einen neueren. | Fassungstyp `konsolidiert_fehlerkorrektur` (PDF oder XML), Stand älter als der neueste; **`ersetzt_durch` ist Pflicht** | ja: galt, bis der neuere Stand erschien |
| `informativ` | **Aus Typgründen nie maßgeblich**, unabhängig vom Zeitpunkt | informatorische Lesefassungen (Word), Formatnebenfassungen (XML-Basis, XML des neuesten Stands neben dem PDF) | nein |
| `nicht_verbindlich` | Hatte nie Verbindlichkeit | Konsultationsfassungen | nein |
| **`verworfen`** | **Fehlerhaft oder zurückgezogen** — die Fassung hätte so nie gelten sollen | ausdrücklicher Beleg nötig (Rücknahme durch die Quelle, erklärter Fehler); **Pflichtangabe in `rolle_begruendung`** | nein: gilt unabhängig davon, ob es eine neuere Fassung gibt |

## Abgrenzung in einem Satz

**`ersetzt`** sagt: *Diese Fassung war einmal die richtige und wurde durch eine neuere
derselben Version abgelöst.* Sie wäre die Antwort auf die Frage „Welche Fassung galt am
10.07.2026?“ und wird deshalb mit Nachfolger (`ersetzt_durch`) aufbewahrt.
**`verworfen`** sagt: *Diese Fassung ist fehlerhaft oder zurückgezogen und hätte so nie
gelten sollen.* Das ist ein Urteil über die Fassung, kein Zeitverhältnis — es gilt auch
ohne neuere Fassung. Ohne ausdrücklichen Beleg wird die Rolle nicht vergeben; die übrigen
Zweifelsfälle laufen weiterhin so:

* **Nie maßgeblich wegen des Typs** → `informativ` oder `nicht_verbindlich`
* **Zweifel, ob die Fassung zu dieser Version gehört oder korrekt ist** (z. B. falsch
  beschriftet, widersprüchlicher Deckblattvermerk wie bei APERAK AHB 1.1) → die Fassung
  behält ihre Typrolle, der Zweifel steht in `hinweise[]` (`dokumentauffaelligkeit` /
  `offene_frage`). Ist dadurch die Auswahl selbst unsicher, wird
  `dokumentversion.dokumentstatus = relevanz_unklar` gesetzt. Nichts wird gestrichen.

## Reihenfolge der Rollenvergabe (deterministisch)

1. `konsultationsfassung` → `nicht_verbindlich`
2. informatorische Lesefassung (jeder Stand) → `informativ`
3. Fassung mit Beleg für Fehlerhaftigkeit oder Rücknahme → `verworfen` (ab v0.6), mit Beleg
4. neueste konsolidierte Fassung (ab v0.2: oder außerordentliche Veröffentlichung), PDF → `massgeblich`; dieselbe als XML → `informativ`
5. ältere konsolidierte Fassung (PDF oder XML) → `ersetzt`, `ersetzt_durch` = gleichformatige
   Fassung des nächstneueren Stands
6. Basis-PDF → `ergaenzend`, wenn Schritt 4 griff, sonst `massgeblich`
7. Basis in anderem Format → `informativ`
8. Fassungstyp, den diese Regeln nicht kennen → **keine stille Einordnung**: im
   Etappenbericht als Fall ausweisen und die Regel ausdrücklich ergänzen

### Warum bisher keine Fassung `verworfen` ist

Der naheliegende Kandidat wäre das Muster **`validTo` vor `validFrom`** in den BDEW-Daten:
15 Fassungen tragen es (u. a. die XML-Basisdateien von UTILMD AHB Gas 1.2 und ORDERS AHB
1.1b). Das Muster taugt aber **nicht** als Beleg für „zurückgezogen“, denn es trifft
genauso die regulär abgelösten Fehlerkorrekturstände (z. B. UTILMD MIG Strom S2.2 Stand
29.06.2026, korrekt `ersetzt`). Es ist die Art, wie die Plattform eine Datei beendet, nicht
eine Aussage über ihre Richtigkeit. Ohne eine ausdrückliche Rücknahme- oder Fehlermeldung
der Quelle wird deshalb nicht `verworfen` vergeben — Raten wäre hier schlimmer als eine
leere Kategorie.

## Erweiterung v0.2 / v0.3 — Fassungen ohne Mitteilungsbezug (O-11, bestätigt)

O-11 (außerordentliche Veröffentlichung) und O-12 (Fehlerkorrekturfassungen ohne Mitteilung)
sind **dasselbe Muster** und werden hier als ein Punkt geführt: **BDEW veröffentlicht
Fassungen, die in keiner BNetzA-Mitteilung stehen.** Das Schema macht das ab v0.3 an jeder
Fassung sichtbar, statt es im Fließtext zu lassen:

```json
"mitteilungsbezug": { "art": "kein_mitteilungsbezug", "mitteilung_nummer": null,
                      "vermerk": "Außerordentliche Veröffentlichung; ausschließlich auf BDEW-MaKo veröffentlicht, in keiner BNetzA-Mitteilung genannt" }
```

`art` kennt vier Werte: `anlage_der_mitteilung_bytegleich` (per SHA-256 geprüft),
`anlage_der_mitteilung`, `konsultationsanlage`, `kein_mitteilungsbezug`.

Stand heute (Etappen 1 und 2, 36 Dokumente, 209 Fassungen): 61 Fassungen sind Anlagen einer
Mitteilung und bytegleich, 32 sind Konsultationsanlagen, **116 haben keinen
Mitteilungsbezug**. Darunter sind **11 der 36 maßgeblichen Fassungen** — die amtliche Quelle
kennt in knapp einem Drittel der Fälle die Fassung nicht, die am Stichtag gilt.

### Zwei getrennte Typen, eine gemeinsame Stand-Reihe

Beide Typen bleiben **eigenständig benannt und getrennt datiert** (ab v0.3 erzwungen):

| | `konsolidiert_fehlerkorrektur` | `ausserordentliche_veroeffentlichung` |
|---|---|---|
| Datumsfeld | `fehlerkorrekturstand` | `stand_ausserordentlich` |
| Deckblatt | „Konsolidierte Lesefassung mit Fehlerkorrekturen, Stand …“ | „Außerordentliche Veröffentlichung [wegen Layoutanpassung], Stand …“ |
| Anlass | inhaltliche Fehlerkorrekturen (Status „Fehler (Datum)“) | überwiegend redaktionell: Layout, Segmentzähler, Kapitelstruktur (Status „Anpassung (Datum)“), teils zusätzlich Fehlerkorrekturen |
| Historie | kumuliert | kumuliert, inklusive der früheren Fehlerkorrekturen |
| Mitteilungsbezug | keiner | keiner |

Gemeinsam ist nur die **Sortierung**: `stand_reihe_datum` (abgeleitet aus dem jeweils
gefüllten Feld) ordnet beide Typen in eine Reihe je Version. Der neueste Stand als PDF ist
`massgeblich`, ältere Stände sind `ersetzt`. Fassungen ohne Stand-Datum (drei XML-Dateien)
lassen sich nicht einordnen und bleiben `informativ`, mit Hinweis.

### Angewandt auf den O-11-Fall: CONTRL MIG 2.0b

| Fassung | Typ | Stand | Rolle | warum |
|---|---|---|---|---|
| bdew:6776 (PDF) | basis | — | `ergaenzend` | Anlage der Mitteilung 24, bytegleich; einzige Quelle der Änderungshistorie gegenüber der Vorversion |
| bdew:6777 (PDF) | konsolidiert | 06.12.2021 | `ersetzt` → bdew:7422 | war einmal der richtige Stand |
| bdew:7422 (PDF) | außerordentlich | 26.07.2024 | `ersetzt` → bdew:8195 | dito |
| bdew:8195 (PDF) | außerordentlich | 11.12.2025 | **`massgeblich`** | neuester Stand der Reihe |
| bdew:7561 (XML) | außerordentlich | — | `informativ` | kein Stand-Datum, nicht einzuordnen |
| bdew:8196, 7423 (Word) | informatorische Lesefassung | — | `informativ` | Typ |

**Kein Eintrag ist „verworfen“**, obwohl es zwei naheliegende Kandidaten gäbe: die
XML-Datei ohne Stand-Datum und die konsolidierte Fassung von 2021. Beide bleiben mit Hash,
URL und Begründung erhalten. Die Frage „Welche Fassung galt am 01.08.2024?“ lässt sich damit
weiterhin beantworten (bdew:7422).

**Bestätigt am 17.09.2026:** Der neueste Stand der gemeinsamen Reihe ist maßgeblich, für
CONTRL AHB/MIG und INSRPT AHB/MIG wie vorgeschlagen. Die Regel ist damit verbindlich für
alle weiteren Etappen; die Hinweise `offene_frage` in den vier Datensätzen sind auf
`quellenauffaelligkeit` zurückgestuft.

Die UTILMD-Datensätze aus Etappe 1 folgen dieser Reihenfolge bereits.

## Ergänzung Etappe 6 (18.09.2026) — Fassungen, die Schritt 1–7 nicht kennen

**Status: bestätigt am 18.09.2026** (zusammen mit Schema v0.8 und dem Zuschnitt der
API-Dokumente). Etappe 6 hat drei Fälle getroffen, die unter Schritt 8
fallen („keine stille Einordnung“). Sie werden hier ausdrücklich als Regel ergänzt, nicht im
Einzelfall entschieden.

| Nr. | Fall | Regel | Betroffen |
|---|---|---|---|
| **R-6a** | Dokument **ohne PDF**: XML-Schema (XSD) oder API-Spezifikation (OpenAPI-YAML) | Die Fachdatei **ist** das Dokument. Abschnitt 7 („PDF als Referenz“) greift nicht; Schritte 4–6 gelten sinngemäß mit dem Dokumentformat statt PDF: neueste konsolidierte XSD → `massgeblich`, ältere → `ersetzt`, Basis-XSD → `ergaenzend` bzw. `massgeblich`. `massgebliche_fassung_pdf_sha256` bleibt `null`, der SHA-256 der Fachdatei steht an der Fassung. | 9 XSD-Dokumente, 3 API-Dokumente |
| **R-6b** | **Wechsel des Veröffentlichungswegs** bei gleicher Version (Swagger/PDF-Verweis → GitHub-Release) | Die Fassung des abgelösten Wegs wird `ersetzt`, `ersetzt_durch` = Fassung des neuen Wegs. Voraussetzung ist ein Beleg, dass der Inhalt unverändert ist (hier: Release-Notiz „ohne inhaltliche Änderungen“) und dass der neue Weg geregelt ist (hier: API-Guideline 1.0b Kap. 4, Anlage der Mitteilung 56). Die amtliche Anlage der ursprünglichen Mitteilung bleibt `ergaenzend`, weil nur sie die Version mit der Mitteilung verbindet. | **derzeit kein erfüllter Anwendungsfall** (O-20): bei bdew:7313, 7314, 7650 fehlt der nachweisliche Inhaltsbeleg |
| **R-6c** | **Versionsloses Dokument**, das nur mit Publikationsdatum erscheint (Änderungshistorie XML) | Stand-Reihe nach Publikationsdatum des Deckblatts statt nach Fehlerkorrekturstand. Jüngste Veröffentlichung (PDF) → `massgeblich`, ältere PDF → `ersetzt` mit `ersetzt_durch` = nächstjüngere (BDEW bevorzugt, sonst BNetzA). | Änderungshistorie zu den XML-Datenformaten |

**O-19(a) gelöst (bestätigt 18.09.2026, Schema v0.9):** Ein Release aus mehreren gleichrangigen,
normativ untrennbaren Dateien (Verzeichnisdienst API: Web-API und WebSocket-API) bleibt **ein**
Dokument. Die Fassungen tragen dieselbe `bestandteil_gruppe` und je einen `bestandteil`; je
Bestandteil ist genau eine Fassung `massgeblich`, die Auswahl nennt alle in
`auswahl.massgebliche_bestandteile`. Voraussetzung: Die Quellen führen die Teile selbst als eine
Einheit (eine Mitteilungsanlage, ein Release, ein Eintrag). Trennen die Quellen selbst — wie bei
Steuerungshandlungen/MaLo-ID (Mitteilungen 36/43) —, bleiben es getrennte Dokumente.

**O-20 (zu R-6b):** Bei allen drei API-Dokumenten ist Beleg (1) „Inhalt unverändert“ nur indirekt
erbracht (Herausgebererklärung in der Release-Notiz, unveränderte Datei seit dem Import, beim
Verzeichnisdienst zusätzlich Inhaltsmerkmale der Version 1.0). Ein Direktvergleich ist nicht
möglich, weil SwaggerHub die Spezifikationen gelöscht hat, und die alten PDFs sind nur
Linkblätter. **Entschieden 18.09.2026:** R-6b verlangt einen nachweislichen Beleg; er fehlt bei
allen drei. Die alten PDFs sind deshalb `ergaenzend`, nicht `ersetzt`. Die Regel selbst bleibt
bestehen. Die Beleglage wird im Übergabebericht als offene Beobachtung geführt.
