# Regulatorische Quelldokumente

Die PDF-Dateien selbst liegen **nicht** im Repository (mehrere MB je Datei, siehe
`.gitignore`). Sie werden aus der offiziellen Quelle bezogen; der SHA-256 jeder
importierten Datei steht in `message_definitions.quelle_hash` und macht den
Dokumentstand nachvollziehbar.

## UTILMD Anwendungshandbuch Gas 1.1

| | |
|---|---|
| Dateiname | `UTILMD_AHB_Gas_1_1_20251001.pdf` |
| Version | 1.1, Stand MIG G1.1 |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 |
| Seiten | 329 |
| SHA-256 | `b8950fb45134dd0927c95e5b8f5f0bd98ce59bb2fc7911c5105f552d18c96ae0` |

Bezug:

```bash
curl -L -o backend/data/regulatory/UTILMD_AHB_Gas_1_1_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/UTILMD_AHB_Gas_1_1_20251001.pdf?__blob=publicationFile&v=1"
```

Uebersichtsseite der Mitteilung Nr. 54:
<https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Mitteilung_Nr_54.html>

> Hinweis: Das Deckblatt der Datei traegt die Aufschrift "Konsultationsfassung".
> Das ist der von der BNetzA unter Mitteilung Nr. 54 veroeffentlichte Stand; die
> Mitteilung selbst weist die Fassung als ab 01.04.2026 anzuwenden aus.

## UTILMD Nachrichtenbeschreibung (MIG) Gas G1.1

| | |
|---|---|
| Dateiname | `UTILMD_MIG_Gas_G1_1_20251001.pdf` |
| Version | G1.1 |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 |
| Seiten | 168 |
| SHA-256 | `f5191a473b650dd6e5de2a673f97b6db685f57de8f6b8d2da7d6ccebb2bfe634` |

Bezug:

```bash
curl -L -o backend/data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/UTILMD_MIG_Gas_G1_1_20251001.pdf?__blob=publicationFile&v=1"
```

> Anders als das AHB traegt diese Datei **keinen** Konsultationsvermerk -- es ist
> die finale, unter Mitteilung Nr. 54 veroeffentlichte Fassung.

Genutzt wird daraus die amtliche Zuordnung Pruefidentifikator -> Prozessbezeichnung
(Segmentlayout, SG6/RFF, Datenelement 1154, S. 51-53; 91 Eintraege). Struktur-
befund und Parserform siehe Issue #46.


## Codeliste der OBIS-Kennzahlen und Medien

| | |
|---|---|
| Dateiname | `Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf` |
| Version | 2.5c |
| Publikationsdatum | 01.10.2025 |
| Anzuwenden ab | 01.04.2026 |
| Quelle | Bundesnetzagentur, Mitteilung Nr. 54 (Autor laut PDF-Metadaten: BDEW) |
| Seiten | 46 |
| SHA-256 | `bc43ff890fde3d02203e72b67e10bfeb966c53791d85246067c54c45a67c8aef` |

Bezug:

```bash
curl -L -o backend/data/regulatory/Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf \
  "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_54/Anlagen/Codeliste-OBIS-Kennzahlen_Medien_2_5c_20251001.pdf?__blob=publicationFile&v=1"
```

> Die Uebersichtsseite der Mitteilung Nr. 54 verlinkt diese Anlage relativ, also
> auf derselben Domain wie AHB und MIG. Eine zusaetzlich kursierende URL unter
> `dsc.bund.de` wird **nicht** verwendet -- sie ist nicht noetig, der direkte
> Abruf oben liefert HTTP 200 ohne Redirect.

Das Dokument enthaelt **zehn** strukturell verschiedene Tabellenformen. Importiert
werden die sieben, die tatsaechlich Wertelisten sind; sie verteilen sich auf die
Kapitel 2.2, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5 und 5 (zwei Formen kommen je
zweimal vor, einmal fuer Strom und einmal fuer Gas). Ergebnis: 12 `CodeList`-
Eintraege mit 224 `CodeListEntry`.

Bewusst NICHT importiert:

* **Kapitel 3.3.x / 4.6.x** (Messprodukt-Code -> zulaessige OBIS-Kennzahlen):
  eine Zuordnungstabelle mit Bedingungen, keine Werteliste. Zurueckgestellt als
  eigenes Wissensobjekt.
* **Kapitel 3.3.4** (Korrekturenergiemenge): Merkmalskombination -> OBIS.
* **Kapitel 7** (Aenderungshistorie): Dokumentationstabelle. Sie zitiert 14
  OBIS-Kennzahlen und 4 Messprodukt-Codes frueherer Staende, teils inzwischen
  geloescht -- expliziter Nicht-Datenbereich, per Regressionstest abgesichert.

Strukturbefund und Formspezifikationen siehe Issue #48.

## Import

```bash
cd backend && ./venv/bin/python -m app.import_ahb --help
cd backend && ./venv/bin/python -m app.import_mig --help
cd backend && ./venv/bin/python -m app.import_obis --help
```

Alle drei Importe sind idempotent. Beim AHB wird derselbe Dateihash beim zweiten Lauf
erkannt und sauber uebersprungen (`--reimport` erzwingt einen kontrollierten
Neuaufbau). Der MIG-Import veraendert einen bestehenden `ProcessIdentifier`
grundsaetzlich nicht und braucht deshalb keinen Schalter. Der OBIS-Import
erkennt denselben Dateihash und ueberspringt ihn; `--reimport` erzwingt einen
kontrollierten Neuaufbau.

## Tests

Die Tests in `backend/tests/` ueberspringen sich selbst, wenn die jeweilige
PDF-Datei nicht vorliegt. Abweichende Ablageorte lassen sich ueber die
Umgebungsvariablen `ATLAS_AHB_GAS_11_PDF`, `ATLAS_MIG_GAS_G11_PDF` und
`ATLAS_OBIS_CODELISTE_PDF` setzen.
