# Rollen einer Fassung — „ersetzt“ ist nicht „verworfen“

**Ticket:** #64 · gilt ab Schema v0.1 (`provenienz_schema.json`, Feld `fassungen[].rolle`)

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
3. neueste konsolidierte Fassung, PDF → `massgeblich`; dieselbe als XML → `informativ`
4. ältere konsolidierte Fassung (PDF oder XML) → `ersetzt`, `ersetzt_durch` = gleichformatige
   Fassung des nächstneueren Stands
5. Basis-PDF → `ergaenzend`, wenn Schritt 3 griff, sonst `massgeblich`
6. Basis in anderem Format → `informativ`
7. Fassungstyp, den diese Regeln nicht kennen (z. B. „außerordentliche Veröffentlichung“)
   → **keine stille Einordnung**: im Etappenbericht als Fall ausweisen und die Regel
   ausdrücklich ergänzen

Die UTILMD-Datensätze aus Etappe 1 folgen dieser Reihenfolge bereits. Mit v0.1 kommt dort
nur `ersetzt_durch` hinzu.
