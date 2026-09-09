"""Schema-Kompatibilitaetscheck (Auftrag Schritt 3.3): bilden die SQLAlchemy-
Modelle das TATSAECHLICHE Schema der gesicherten SQLite-Datenbank ab?
Rein lesend, aendert nichts und gleicht nichts automatisch an."""
import sqlite3, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
os.environ['DATABASE_URL'] = 'sqlite:///' + sys.argv[1]   # nur Metadaten, kein Schreibzugriff
from app.database import Base
from app import models  # noqa: F401  registriert alle Modelle

quelle = sys.argv[1]
con = sqlite3.connect(f'file:{quelle}?mode=ro', uri=True)

sqlite_tabs = {r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
modell_tabs = set(Base.metadata.tables.keys())

print('=== A) TABELLEN ===')
nur_db = sorted(sqlite_tabs - modell_tabs)
nur_modell = sorted(modell_tabs - sqlite_tabs)
print(f'  SQLite: {len(sqlite_tabs)}   Modelle: {len(modell_tabs)}')
print(f'  nur in SQLite (Modell kennt sie NICHT): {nur_db or "keine"}')
print(f'  nur in Modellen (in SQLite nicht angelegt): {nur_modell or "keine"}')

print()
print('=== B) SPALTEN je gemeinsamer Tabelle ===')
abweichungen = []
for t in sorted(sqlite_tabs & modell_tabs):
    db_cols = {r[1]: (r[2], bool(r[3]), r[5]) for r in con.execute(f'PRAGMA table_info("{t}")')}
    mdl_cols = {c.name: c for c in Base.metadata.tables[t].columns}
    fehlt_im_modell = sorted(set(db_cols) - set(mdl_cols))
    fehlt_in_db = sorted(set(mdl_cols) - set(db_cols))
    if fehlt_im_modell or fehlt_in_db:
        abweichungen.append((t, fehlt_im_modell, fehlt_in_db))
        print(f'  {t}:')
        if fehlt_im_modell:
            print(f'      in SQLite, aber NICHT im Modell: {fehlt_im_modell}')
        if fehlt_in_db:
            print(f'      im Modell, aber NICHT in SQLite: {fehlt_in_db}')
if not abweichungen:
    print('  keine Spaltenabweichung in allen', len(sqlite_tabs & modell_tabs), 'gemeinsamen Tabellen')

print()
print('=== C) ERGEBNIS ===')
kritisch = bool(nur_db) or any(a[1] for a in abweichungen)
if kritisch:
    print('  ABWEICHUNG: SQLite enthaelt Struktur, die die Modelle nicht abbilden.')
    print('  -> Daten koennten bei der Migration verloren gehen. STOP.')
    sys.exit(1)
elif nur_modell or abweichungen:
    print('  Modelle sind ein ECHTES OBERMENGE des SQLite-Schemas.')
    print('  -> Kein Datenverlust moeglich; neue Struktur bleibt in Postgres leer/Default.')
    sys.exit(2)
else:
    print('  Schemata deckungsgleich.')
    sys.exit(0)
