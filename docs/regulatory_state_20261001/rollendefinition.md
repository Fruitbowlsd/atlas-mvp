# Rollen einer Fassung — „ersetzt“ ist nicht „verworfen“

**Ticket:** #64 · gilt ab Schema v0.1 (`provenienz_schema.json`, Feld `fassungen[].rolle`); Erweiterung um außerordentliche Veröffentlichungen in v0.2 (Etappe 2, **zur Bestätigung**)

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

## Erweiterung v0.2 — außerordentliche Veröffentlichung (Etappe 2, zur Bestätigung)

In Etappe 2 aufgetreten bei CONTRL AHB 1.0, CONTRL MIG 2.0b, INSRPT AHB 1.1g und INSRPT MIG
1.1a. Befund am Dokument:

* Deckblatt: „Außerordentliche Veröffentlichung [wegen Layoutanpassung]“, eigenes
  **Stand**-Datum, gleiche **Version**, „Ursprüngliches Publikationsdatum“. Es ist also eine
  weitere Fassung derselben Version, keine neue Version.
* Die Änderungshistorie ist **kumuliert** wie bei der konsolidierten Fassung: frühere
  Fehlerkorrekturen („Fehler (30.03.2023)“) plus Anpassungen („Anpassung (26.07.2024)“ Layout,
  „Anpassung (11.12.2025)“ Segmentzähler/Tabellenlayout; für CONTRL Änd-ID 26091 ausdrücklich
  „kein Implementierungsaufwand“) und vereinzelt neue Fehlerkorrekturen („Fehler (11.12.2025)“
  bei INSRPT AHB, Deckblattdatum).
* Sie ist in keiner BNetzA-Mitteilung angekündigt, genau wie konsolidierte
  Fehlerkorrekturfassungen.

**Regel (vorläufig angewandt):** Außerordentliche Veröffentlichungen und konsolidierte
Fehlerkorrekturfassungen bilden **eine** Stand-Reihe je Version. Schritte 3 und 4 gelten für
beide Typen gemeinsam: Der neueste Stand (PDF) ist `massgeblich`, ältere Stände sind
`ersetzt`. Eine Fassung ohne Stand-Datum im Titel (einzelne XML-Dateien) lässt sich nicht
einordnen und wird `informativ`, mit Hinweis.

Die UTILMD-Datensätze aus Etappe 1 folgen dieser Reihenfolge bereits. Mit v0.1 kommt dort
nur `ersetzt_durch` hinzu.
