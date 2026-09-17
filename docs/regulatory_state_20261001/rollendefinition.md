# Rollen einer Fassung — „ersetzt“ ist nicht „verworfen“

**Ticket:** #64 · gilt ab Schema v0.1 (`provenienz_schema.json`, Feld `fassungen[].rolle`), erweitert in v0.2/v0.3 um Fassungen ohne Mitteilungsbezug (O-11, **vom Nutzer bestätigt am 17.09.2026**)

> Hinweis zur Herkunft: Der Auftrag hat keinen Abschnitt 11a. Diese Definition geht auf deine
> Ergänzung vom 17.09.2026 zurück und ist seit Commit 4617854 schriftlich festgelegt; hier
> kommt die Anwendung auf den O-11-Fall dazu.

## Grundsatz

**Das Schema kennt keine Rolle „verworfen“, und zwar mit Absicht.** Keine gefundene Fassung
wird aus einem Datensatz entfernt oder als ungültig gestrichen (Abschnitt 10: Versionen nie
überschreiben; Arbeitsweise: kein Feld geht still verloren). Jede Fassung bekommt eine
Rolle, die ihr Verhältnis zur maßgeblichen Fassung beschreibt, und behält Hash, URL und
Belege.

## Die fünf Rollen

| Rolle | Bedeutung | Kriterium | Zeitbezug |
|---|---|---|---|
| `massgeblich` | Die Fassung, die am Stichtag gilt | genau eine je Dokumentversion; PDF | — |
| `ergaenzend` | Nicht maßgeblich, aber fachlich **nötig**, weil sie Information enthält, die der maßgeblichen Fassung fehlt | Basis-PDF, sobald eine konsolidierte Fassung existiert (einzige Quelle der Änderungshistorie gegenüber der Vorversion); ohne konsolidierte Fassung ist die Basis selbst maßgeblich | — |
| **`ersetzt`** | **Zeitlich abgelöst.** Fassung eines **älteren Fehlerkorrekturstands derselben Version**. Zu ihrem Zeitpunkt war sie der richtige Stand, inzwischen gibt es einen neueren. | Fassungstyp `konsolidiert_fehlerkorrektur` (PDF oder XML), Stand älter als der neueste; **`ersetzt_durch` ist Pflicht** | ja: galt, bis der neuere Stand erschien |
| `informativ` | **Aus Typgründen nie maßgeblich**, unabhängig vom Zeitpunkt | informatorische Lesefassungen (Word), Formatnebenfassungen (XML-Basis, XML des neuesten Stands neben dem PDF) | nein |
| `nicht_verbindlich` | Hatte nie Verbindlichkeit | Konsultationsfassungen | nein |

## Abgrenzung in einem Satz

**`ersetzt`** sagt: *Diese Fassung war einmal die richtige und wurde durch eine neuere
derselben Version abgelöst.* Sie wäre die Antwort auf die Frage „Welche Fassung galt am
10.07.2026?“ und wird deshalb mit Nachfolger (`ersetzt_durch`) aufbewahrt.
**„Verworfen“** würde heißen: *Diese Fassung war nie richtig oder gehört nicht hierher.*
Diesen Fall löst das Schema nicht über eine Rolle:

* **Nie maßgeblich wegen des Typs** → `informativ` oder `nicht_verbindlich`
* **Zweifel, ob die Fassung zu dieser Version gehört oder korrekt ist** (z. B. falsch
  beschriftet, widersprüchlicher Deckblattvermerk wie bei APERAK AHB 1.1) → die Fassung
  behält ihre Typrolle, der Zweifel steht in `hinweise[]` (`dokumentauffaelligkeit` /
  `offene_frage`). Ist dadurch die Auswahl selbst unsicher, wird
  `dokumentversion.dokumentstatus = relevanz_unklar` gesetzt. Nichts wird gestrichen.

## Reihenfolge der Rollenvergabe (deterministisch)

1. `konsultationsfassung` → `nicht_verbindlich`
2. informatorische Lesefassung (jeder Stand) → `informativ`
3. neueste konsolidierte Fassung (ab v0.2: oder außerordentliche Veröffentlichung), PDF → `massgeblich`; dieselbe als XML → `informativ`
4. ältere konsolidierte Fassung (PDF oder XML) → `ersetzt`, `ersetzt_durch` = gleichformatige
   Fassung des nächstneueren Stands
5. Basis-PDF → `ergaenzend`, wenn Schritt 3 griff, sonst `massgeblich`
6. Basis in anderem Format → `informativ`
7. Fassungstyp, den diese Regeln nicht kennen → **keine stille Einordnung**: im
   Etappenbericht als Fall ausweisen und die Regel ausdrücklich ergänzen

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
