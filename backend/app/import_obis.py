"""CLI fuer den Import der Codeliste der OBIS-Kennzahlen und Medien (Issue #48).

Wie beim AHB und der MIG bewusst ein Kommandozeilenwerkzeug und KEIN
API-Endpunkt: der Import ist ein kuratierter Vorgang, dessen Report gelesen wird.

    cd backend && ./venv/bin/python -m app.import_obis \\
        --pdf data/regulatory/Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf
"""
from __future__ import annotations

import argparse
import sys

from .database import Base, SessionLocal, engine
from . import models  # noqa: F401  (registriert alle Modelle fuer create_all)
from .migrations import run_light_migrations
from .regulatory_extraction_obis import (
    import_obis_codelists,
    resolve_active_regulatory_version,
)

_DEFAULT_PDF = "data/regulatory/Codeliste_OBIS_Kennzahlen_Medien_2_5c_20251001.pdf"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Codelisten der OBIS-Kennzahlen und Medien in die Wissensbasis übernehmen"
    )
    parser.add_argument("--pdf", default=_DEFAULT_PDF,
                        help=f"Pfad zur PDF-Datei (Default: {_DEFAULT_PDF})")
    parser.add_argument("--version-id", type=int, default=None,
                        help="RegulatoryVersion-ID; ohne Angabe wird die aktive Version verwendet")
    parser.add_argument("--reimport", action="store_true",
                        help="vorigen Stand derselben Datei ersetzen statt zu überspringen")
    args = parser.parse_args(argv)

    Base.metadata.create_all(bind=engine)
    run_light_migrations(engine)

    db = SessionLocal()
    try:
        if args.version_id is not None:
            version = db.get(models.RegulatoryVersion, args.version_id)
        else:
            # Ueber is_active aufloesen, nicht ueber den Namensstring
            # (Auftrag Abschnitt 3).
            version = resolve_active_regulatory_version(db)
        if version is None:
            print("FEHLER: keine aktive RegulatoryVersion gefunden.", file=sys.stderr)
            return 2

        before_lists = db.query(models.CodeList).count()
        before_entries = db.query(models.CodeListEntry).count()
        print(f"RegulatoryVersion: [{version.id}] {version.name}", flush=True)
        print(f"Dokument:          {args.pdf}", flush=True)
        print(f"CodeList/CodeListEntry vorher: {before_lists} / {before_entries}", flush=True)
        print("=" * 72, flush=True)

        report = import_obis_codelists(db, args.pdf, version.id, reimport=args.reimport)
        after_lists = db.query(models.CodeList).count()
        after_entries = db.query(models.CodeListEntry).count()
        print(report.format_report(), flush=True)
        print(
            f"\nCodeList vorher/nachher:      {before_lists} -> {after_lists}"
            f"\nCodeListEntry vorher/nachher: {before_entries} -> {after_entries}",
            flush=True,
        )
        return 1 if report.errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
