"""CLI fuer den MIG-Import der PI-Bezeichnungen (Issue #46).

Wie beim AHB bewusst ein Kommandozeilenwerkzeug und KEIN API-Endpunkt: der
Import ist ein kuratierter Vorgang, dessen Report gelesen wird.

    cd backend && ./venv/bin/python -m app.import_mig \\
        --pdf data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf
"""
from __future__ import annotations

import argparse
import sys

from .database import Base, SessionLocal, engine
from . import models  # noqa: F401  (registriert alle Modelle fuer create_all)
from .migrations import run_light_migrations
from .regulatory_extraction_mig import (
    import_mig_process_identifiers,
    resolve_active_regulatory_version,
)

_DEFAULT_PDF = "data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prüfidentifikator-Bezeichnungen aus der MIG in die Wissensbasis übernehmen"
    )
    parser.add_argument("--pdf", default=_DEFAULT_PDF, help=f"Pfad zur PDF-Datei (Default: {_DEFAULT_PDF})")
    parser.add_argument("--version-id", type=int, default=None,
                        help="RegulatoryVersion-ID; ohne Angabe wird die aktive Version verwendet")
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

        before = db.query(models.ProcessIdentifier).count()
        print(f"RegulatoryVersion: [{version.id}] {version.name}", flush=True)
        print(f"Dokument:          {args.pdf}", flush=True)
        print(f"ProcessIdentifier vorher: {before}", flush=True)
        print("=" * 72, flush=True)

        report = import_mig_process_identifiers(db, args.pdf, version.id)
        after = db.query(models.ProcessIdentifier).count()
        print(report.format_report(), flush=True)
        print(f"\nProcessIdentifier vorher/nachher: {before} -> {after}", flush=True)
        return 1 if report.errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
