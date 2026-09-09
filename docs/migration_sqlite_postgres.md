# Migration SQLite → PostgreSQL (Issue #60)

Persistenz für die Atlas-Produktionsdatenbank. PostgreSQL ist ab dem Cutover das
alleinige produktive System of Record; SQLite dient nur noch als historische
Quelle der Sicherung.

## 1. Ausgangsbefund

Die Anwendung lief auf Railway ohne gesetzte `DATABASE_URL` und damit auf dem
Default aus `backend/app/database.py:5` — `sqlite:///./atlas.db`, im Container
`/app/atlas.db`. Ohne Volume verwirft jeder Redeploy das Dateisystem. Der Code
benennt das in `backend/app/migrations.py` selbst: „Auf Railway wird die DB je
Deploy neu aufgebaut."

Gemessen im laufenden Container (`railway ssh`, `sqlite3` mit `mode=ro`) am
09.09.2026:

| Tabelle | Produktion | Bedeutung |
|---|---|---|
| `process_identifiers` | 16 | exakt die Seed-Menge aus `seed_data.PROCESS_IDENTIFIERS` |
| `message_definitions` | 0 | |
| `message_segments` | 0 | |
| `message_fields` | 0 | |
| `code_lists` | 0 | |
| `code_list_entries` | 0 | |
| `requirements` | 269 | 133 Basis + 136 Folgeversion, reiner Seed |

Die Statusverteilung in `assessment_requirements` stimmte Zeile für Zeile mit der
deterministischen Seed-Erwartung (`random.Random(42)`) überein — es existierte
keine handgepflegte Zeile.

**Die Extraktionsdaten der vorangegangenen PRs waren nie in der Produktion.**
Alle fünf Importe (`import_pid`, `import_mig`, `import_ahb`, `import_obis`,
`import_ebd`) sind CLI-Werkzeuge ohne API-Router, und eine SQLite-Datei im
Container ist über kein Netzwerkprotokoll erreichbar. Kein Router erzeugt
`MessageDefinition`, `MessageSegment`, `MessageField`, `CodeList` oder
`CodeListEntry`. Der erarbeitete Bestand lag ausschließlich lokal in
`backend/atlas.db` — nicht versioniert (`.gitignore`), nicht gesichert.

## 2. Sicherungen

Beide über `sqlite3.backup()` erzeugt, damit sie auch bei geöffneter Datenbank
konsistent sind, und vor jeder Änderung geprüft: Dateigröße, Öffnen in SQLite,
`PRAGMA integrity_check`, erwartete Tabellen, Zeilenzahlen.

| Datei | Inhalt | Größe | integrity_check |
|---|---|---|---|
| `atlas_RAILWAY_PRODUKTION_20260909_222710.db` | Produktion, nur Seed | 196.608 B | ok |
| `atlas_lokal_20260909_220135.db` | lokaler Extraktionsbestand | 6.291.456 B | ok |

Beide liegen außerhalb des Repositorys in `~/atlas-backups/` und werden nach dem
Cutover als Rückfallebene aufbewahrt.

## 3. Schema-Kompatibilitätscheck

`scripts/pg_schema_check.py` vergleicht die SQLAlchemy-Modelle mit dem
tatsächlichen Schema der gesicherten Datei, bevor `create_all()` läuft — weil
`create_all()` nach dem aktuellen Codestand anlegt und keine Migration eines
bestehenden Schemas ist. Ergebnis für beide Sicherungen: 23 Tabellen auf beiden
Seiten, keine Tabelle nur auf einer Seite, keine Spaltenabweichung.

## 4. Datenübertragung

`scripts/pg_migrate_from_sqlite.py`. Gelesen wird über SQLAlchemy Core mit
derselben Metadata wie das Ziel, damit die Typkonvertierung (SQLite-Integer 0/1 →
Postgres `boolean`, Datums-String → `timestamp`) von SQLAlchemy kommt statt
geraten zu werden. Reihenfolge ist `Base.metadata.sorted_tables`, also
topologisch nach Fremdschlüsseln. Alles in einer Transaktion; eine Abweichung
zwischen gelesener und geschriebener Zeilenzahl bricht ab, statt Zeilen zu
überspringen. `PRAGMA foreign_key_check` auf der Quelle war leer.

Übertragen: **29.561 Zeilen** über 23 Tabellen.

Eine Ausnahme, bewusst und dokumentiert: Die Tabelle `users` stammt aus der
**Produktions**sicherung, nicht aus der lokalen. Der lokale Datensatz trägt einen
Passwort-Hash aus der Entwicklungsumgebung; ihn zu übernehmen hätte den
Demo-Login mit dem in der Railway-Umgebung gesetzten `ATLAS_DEMO_PASSWORD`
unbrauchbar gemacht. `id` und `tenant_id` sind in beiden Quellen identisch, es
entsteht keine Fremdschlüssellücke.

Nach dem Insert werden die Sequences auf `MAX(id) + 1` gesetzt, sonst kollidiert
der erste neue Datensatz mit bestehenden IDs.

## 5. Verifikation

`scripts/pg_verify_fingerprints.py` bildet je Tabelle einen SHA-256 über alle
Spalten aller nach Primärschlüssel sortierten, kanonisch formatierten Zeilen.
Das erfasst in einem Wert, was Einzelprüfungen einzeln suchen müssten: Werte,
NULLs, Unicode, Booleans, Datumswerte.

**Ergebnis: 23 von 23 Tabellen mit identischem Fingerabdruck.**

`scripts/pg_verify_details.py` prüft ergänzend, damit eine Abweichung benennbar
wäre statt nur „Hash ungleich":

| Prüfung | Umfang | Abweichungen |
|---|---|---|
| NULL-Verteilung je Spalte | 229 Spalten | 0 |
| Fremdschlüssel-Referenzen in Postgres | alle FKs | 0 |
| Unicode in Freitext-/Rohdatenfeldern (`∧`, `∨`, Umlaute, `→`, `≥`) | 91 Zeichen/Spalten-Kombinationen mit Vorkommen | 0 |
| Boolean-Verteilung | 13 Spalten | 0 |
| Maximale Stringlänge (Truncation) | alle Textspalten ≥ 100 Zeichen | 0 |
| Unique-/PK-Constraints | 31 aktiv | alle erfüllt |
| Sequences `nextval > MAX(id)` | 18 Tabellen mit Daten | 0 |

## 6. Cutover-Probe

Vor dem Umschalten wurde die Startup-Sequenz aus `main.py:47` gegen die migrierte
Datenbank ausgeführt — `create_all()`, `run_light_migrations()`, `run_seed()` —
und anschließend die Fingerabdruck-Verifikation wiederholt. Alle 23 Werte
unverändert: `run_seed` ist gegen den migrierten Bestand idempotent und legt
nichts doppelt an.

## 7. Backup-Lage der neuen Instanz

Der Postgres-Service bringt ein eigenes Volume mit (`RAILWAY_VOLUME_*`); das
Persistenzproblem aus Abschnitt 1 ist damit strukturell gelöst. Davon unabhängig
ist die Frage regelmäßiger Sicherungen — **nicht Teil dieses Auftrags, nur
festgehalten**:

- Volume-Backups nach Zeitplan: täglich (6 Tage Aufbewahrung), wöchentlich
  (27 Tage), monatlich (89 Tage). Abrechnung inkrementell, Copy-on-Write.
- Manuelle Sicherungen jederzeit, begrenzt auf 50 % der Volume-Größe.
- Point-in-Time Recovery über pgBackRest, Wiederherstellung auf einen beliebigen
  Zeitpunkt im Archivfenster; verwaltet über `railway postgres pitr`.
- Wiederherstellung erzeugt ein neues Volume und muss bewusst deployed werden;
  das alte bleibt unmountiert erhalten.

Stand nach dem Anlegen: **PITR `disabled`, kein Backup-Zeitplan konfiguriert.**
Beides ist eine eigene Entscheidung und wurde hier nicht verändert.
