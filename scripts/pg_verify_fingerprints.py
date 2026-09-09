"""Datenintegritaets-Verifikation SQLite vs. Postgres (Auftrag Schritt 4).

Kern ist ein deterministischer Fingerabdruck je Tabelle ueber ALLE Spalten
sortierter, kanonisch formatierter Zeilen. Der deckt in einem Wert ab, was
Einzelpruefungen einzeln suchen muessten: Werte, NULLs, Unicode, Booleans,
Datumswerte. Die Einzelpruefungen laufen zusaetzlich, damit eine Abweichung
benennbar wird statt nur "Hash ungleich".
"""
import sys, os, hashlib, datetime, decimal
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
import sqlalchemy as sa

quelle_lokal, quelle_prod, ziel_url = sys.argv[1], sys.argv[2], sys.argv[3]
os.environ['DATABASE_URL'] = ziel_url
from app.database import Base
from app import models  # noqa: F401

src = sa.create_engine(f'sqlite:///{quelle_lokal}')
src_prod = sa.create_engine(f'sqlite:///{quelle_prod}')
dst = sa.create_engine(ziel_url)
AUS_PRODUKTION = {'users'}

def kanonisch(w):
    if w is None:                      return 'NULL'
    if isinstance(w, bool):            return 'B:1' if w else 'B:0'
    if isinstance(w, (int,)):          return f'I:{w}'
    if isinstance(w, float):           return f'F:{w!r}'
    if isinstance(w, decimal.Decimal): return f'F:{float(w)!r}'
    if isinstance(w, datetime.datetime):
        return 'T:' + w.replace(tzinfo=None).isoformat(timespec='microseconds')
    if isinstance(w, datetime.date):   return 'D:' + w.isoformat()
    if isinstance(w, bytes):           return 'X:' + w.hex()
    return 'S:' + str(w)

def lies(engine, tabelle):
    spalten = sorted(tabelle.columns.keys())
    pk = [c.name for c in tabelle.primary_key.columns] or spalten
    with engine.connect() as c:
        zeilen = [dict(r._mapping) for r in c.execute(sa.select(tabelle))]
    zeilen.sort(key=lambda z: tuple(kanonisch(z[k]) for k in pk))
    return spalten, pk, zeilen

def fingerprint(spalten, zeilen):
    h = hashlib.sha256()
    for z in zeilen:
        h.update(('\x1f'.join(kanonisch(z[s]) for s in spalten) + '\x1e').encode())
    return h.hexdigest()[:16]

kopf = f"{'Tabelle':40}{'SQLite':>8}{'PG':>8}  {'Fingerabdruck':>17}  Status"
print(kopf); print('-' * len(kopf))
probleme = []
for tabelle in Base.metadata.sorted_tables:
    herkunft = src_prod if tabelle.name in AUS_PRODUKTION else src
    spalten, pk, q_zeilen = lies(herkunft, tabelle)
    _, _, z_zeilen = lies(dst, tabelle)
    fq, fz = fingerprint(spalten, q_zeilen), fingerprint(spalten, z_zeilen)
    ok = (len(q_zeilen) == len(z_zeilen)) and (fq == fz)
    status = 'OK' if ok else 'ABWEICHUNG'
    print(f'{tabelle.name:40}{len(q_zeilen):>8}{len(z_zeilen):>8}  {fq:>17}  {status}')
    if not ok:
        probleme.append(tabelle.name)
        # Abweichung konkret benennen statt nur zu melden
        qpk = {tuple(z[k] for k in pk) for z in q_zeilen}
        zpk = {tuple(z[k] for k in pk) for z in z_zeilen}
        if qpk - zpk: print(f'    PK nur in SQLite: {sorted(qpk-zpk)[:5]}')
        if zpk - qpk: print(f'    PK nur in Postgres: {sorted(zpk-qpk)[:5]}')
        qi = {tuple(z[k] for k in pk): z for z in q_zeilen}
        for schluessel in sorted(qpk & zpk):
            a = qi[schluessel]; b = next(z for z in z_zeilen if tuple(z[k] for k in pk) == schluessel)
            for s in spalten:
                if kanonisch(a[s]) != kanonisch(b[s]):
                    print(f'    PK {schluessel} Spalte {s}: SQLite {kanonisch(a[s])[:60]!r} != PG {kanonisch(b[s])[:60]!r}')
                    break
            else:
                continue
            break
print()
print('Tabellen mit Abweichung:', probleme or 'keine')
sys.exit(1 if probleme else 0)
