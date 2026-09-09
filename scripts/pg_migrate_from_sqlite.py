"""Datenuebertragung SQLite -> Postgres (Auftrag Schritt 3.5).

Quelle:  verifizierte lokale Sicherung (der erarbeitete Extraktionsbestand)
Ausnahme: Tabelle `users` stammt aus der verifizierten PRODUKTIONS-Sicherung,
          damit der bestehende Demo-Login (Hash aus ATLAS_DEMO_PASSWORD der
          Railway-Umgebung) erhalten bleibt. Die lokale users-Zeile traegt einen
          abweichenden Hash aus der Entwicklungsumgebung.

Gelesen wird ueber SQLAlchemy Core mit derselben Metadata wie das Ziel -- damit
uebernimmt SQLAlchemy die Typkonvertierung (Boolean 0/1 -> bool, DateTime-String
-> datetime) statt sie zu raten. Keine Zeile wird uebersprungen; bei einer
ungeloesten Referenz bricht das Skript ab.
"""
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
import sqlalchemy as sa

quelle_lokal, quelle_prod, ziel_url = sys.argv[1], sys.argv[2], sys.argv[3]
os.environ['DATABASE_URL'] = ziel_url
from app.database import Base
from app import models  # noqa: F401

src = sa.create_engine(f'sqlite:///{quelle_lokal}')
src_prod = sa.create_engine(f'sqlite:///{quelle_prod}')
dst = sa.create_engine(ziel_url)
assert dst.dialect.name == 'postgresql'

AUS_PRODUKTION = {'users'}
protokoll = []

with dst.begin() as dc:            # eine Transaktion: alles oder nichts
    dc.execute(sa.text('SET CONSTRAINTS ALL DEFERRED'))
    for tabelle in Base.metadata.sorted_tables:      # topologische FK-Reihenfolge
        herkunft = src_prod if tabelle.name in AUS_PRODUKTION else src
        etikett = 'PROD' if tabelle.name in AUS_PRODUKTION else 'lokal'
        with herkunft.connect() as sc:
            zeilen = [dict(r._mapping) for r in sc.execute(sa.select(tabelle))]
        if zeilen:
            dc.execute(tabelle.insert(), zeilen)
        n = dc.execute(sa.select(sa.func.count()).select_from(tabelle)).scalar()
        if n != len(zeilen):
            raise SystemExit(f'ABBRUCH {tabelle.name}: gelesen {len(zeilen)}, geschrieben {n}')
        protokoll.append((tabelle.name, etikett, len(zeilen), n))

# Sequences nachziehen: sonst kollidiert der naechste INSERT mit bestehenden IDs.
with dst.begin() as dc:
    for tabelle in Base.metadata.sorted_tables:
        for spalte in tabelle.primary_key.columns:
            if not isinstance(spalte.type, sa.Integer):
                continue
            seq = dc.execute(sa.text(
                "SELECT pg_get_serial_sequence(:t, :c)"), {'t': tabelle.name, 'c': spalte.name}).scalar()
            if seq:
                dc.execute(sa.text(
                    f'SELECT setval(:s, COALESCE((SELECT MAX("{spalte.name}") FROM "{tabelle.name}"), 0) + 1, false)'),
                    {'s': seq})

print(f"{'Tabelle':40}{'Quelle':>8}{'gelesen':>10}{'geschrieben':>13}  Status")
for name, etikett, gelesen, geschrieben in protokoll:
    print(f'{name:40}{etikett:>8}{gelesen:>10}{geschrieben:>13}  {"OK" if gelesen==geschrieben else "FEHLER"}')
print()
print('Zeilen gesamt:', sum(p[2] for p in protokoll))
