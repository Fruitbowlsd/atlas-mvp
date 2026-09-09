import sys, os, sqlite3
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
import sqlalchemy as sa
quelle, quelle_prod, ziel_url = sys.argv[1], sys.argv[2], sys.argv[3]
os.environ['DATABASE_URL'] = ziel_url
from app.database import Base
from app import models  # noqa: F401
src = sa.create_engine(f'sqlite:///{quelle}')
dst = sa.create_engine(ziel_url)
AUS_PROD = {'users'}

print('=== A) NULL-Verteilung je Spalte (alle Tabellen, alle Spalten) ===')
abw = 0; geprueft = 0
for t in Base.metadata.sorted_tables:
    if t.name in AUS_PROD: continue
    for c in t.columns:
        with src.connect() as sc:
            a = sc.execute(sa.text(f'SELECT COUNT(*) FROM "{t.name}" WHERE "{c.name}" IS NULL')).scalar()
        with dst.connect() as dc:
            b = dc.execute(sa.text(f'SELECT COUNT(*) FROM "{t.name}" WHERE "{c.name}" IS NULL')).scalar()
        geprueft += 1
        if a != b:
            abw += 1; print(f'  ABWEICHUNG {t.name}.{c.name}: SQLite {a} NULL, PG {b} NULL')
print(f'  {geprueft} Spalten geprueft, Abweichungen: {abw}')

print()
print('=== B) Fremdschluessel in Postgres validieren ===')
with dst.connect() as dc:
    verletzt = 0
    for t in Base.metadata.sorted_tables:
        for fk in t.foreign_keys:
            z, zs = fk.column.table.name, fk.column.name
            q = fk.parent.name
            n = dc.execute(sa.text(
                f'SELECT COUNT(*) FROM "{t.name}" a WHERE a."{q}" IS NOT NULL '
                f'AND NOT EXISTS (SELECT 1 FROM "{z}" b WHERE b."{zs}" = a."{q}")')).scalar()
            if n: verletzt += 1; print(f'  VERLETZT {t.name}.{q} -> {z}.{zs}: {n} Zeilen')
    print(f'  Fremdschluessel-Verletzungen: {verletzt}')

print()
print('=== C) Unicode-Sonderzeichen in Freitext-/Rohdatenfeldern ===')
muster = ['∧', '∨', 'ä', 'ö', 'ü', 'ß', '→', '≥', '≤', '"', '–']
spalten = []
for t in Base.metadata.sorted_tables:
    if t.name in AUS_PROD: continue
    for c in t.columns:
        if isinstance(c.type, (sa.String, sa.Text)):
            spalten.append((t.name, c.name))
treffer = 0; abw_u = 0
for tn, cn in spalten:
    for m in muster:
        with src.connect() as sc:
            a = sc.execute(sa.text(f'SELECT COUNT(*) FROM "{tn}" WHERE "{cn}" LIKE :p'), {'p': f'%{m}%'}).scalar()
        if not a: continue
        with dst.connect() as dc:
            b = dc.execute(sa.text(f'SELECT COUNT(*) FROM "{tn}" WHERE "{cn}" LIKE :p'), {'p': f'%{m}%'}).scalar()
        treffer += 1
        if a != b:
            abw_u += 1; print(f'  ABWEICHUNG {tn}.{cn} Zeichen {m!r}: SQLite {a}, PG {b}')
print(f'  {treffer} Zeichen/Spalten-Kombinationen mit Vorkommen geprueft, Abweichungen: {abw_u}')

print()
print('=== D) Boolean-Spalten: Verteilung true/false ===')
abw_b = 0; nb = 0
for t in Base.metadata.sorted_tables:
    if t.name in AUS_PROD: continue
    for c in t.columns:
        if not isinstance(c.type, sa.Boolean): continue
        nb += 1
        with src.connect() as sc:
            a = sc.execute(sa.text(f'SELECT COUNT(*) FROM "{t.name}" WHERE "{c.name}"')).scalar()
        with dst.connect() as dc:
            b = dc.execute(sa.text(f'SELECT COUNT(*) FROM "{t.name}" WHERE "{c.name}" IS TRUE')).scalar()
        if a != b:
            abw_b += 1; print(f'  ABWEICHUNG {t.name}.{c.name}: SQLite true={a}, PG true={b}')
print(f'  {nb} Boolean-Spalten geprueft, Abweichungen: {abw_b}')

print()
print('=== E) Laengste Freitextwerte (Truncation-Test) ===')
abw_l = 0
for tn, cn in spalten:
    with src.connect() as sc:
        a = sc.execute(sa.text(f'SELECT MAX(LENGTH("{cn}")) FROM "{tn}"')).scalar() or 0
    if a < 100: continue
    with dst.connect() as dc:
        b = dc.execute(sa.text(f'SELECT MAX(LENGTH("{cn}")) FROM "{tn}"')).scalar() or 0
    if a != b:
        abw_l += 1; print(f'  ABWEICHUNG {tn}.{cn}: max. Laenge SQLite {a}, PG {b}')
print(f'  Abweichungen bei langen Strings: {abw_l}')

print()
print('=== F) Eindeutigkeits-Constraints in Postgres ===')
with dst.connect() as dc:
    n = dc.execute(sa.text("""SELECT COUNT(*) FROM pg_constraint c
        JOIN pg_class t ON t.oid=c.conrelid JOIN pg_namespace n ON n.oid=t.relnamespace
        WHERE n.nspname='public' AND c.contype IN ('u','p')""")).scalar()
    print(f'  {n} Unique-/Primary-Key-Constraints aktiv und erfuellt (Inserts waeren sonst gescheitert)')
