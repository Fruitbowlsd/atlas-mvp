"""CLI fuer den PID-Import der Pruefidentifikatoren (Issue #54, Scoping A).

Wie bei AHB, MIG, OBIS und EBD bewusst ein Kommandozeilenwerkzeug und KEIN
API-Endpunkt: der Import ist ein kuratierter Vorgang, dessen Report gelesen wird.

    cd backend && ./venv/bin/python -m app.import_pid \\
        --pdf data/regulatory/PID_3_3_Konsultationsfassung_20250801.pdf \\
        --mig data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf

Uebernommen wird ausschliesslich das Paar Pruefidentifikator -> Bezeichnung
(Freigabe Scoping A). Alle uebrigen Spalten und die Tabellen 2 bis 5 werden
gelesen und im Report bilanziert, aber nicht modelliert.

``--mig`` ist optional und schaltet den Konsistenzabgleich mit Prompt 1 zu
(Auftrag Abschnitt 9). Ohne die Angabe laeuft der Import unveraendert, der
Report weist den Abgleich dann als nicht durchgefuehrt aus.
"""
from __future__ import annotations

import argparse
import sys

from .database import Base, SessionLocal, engine
from . import models  # noqa: F401  (registriert alle Modelle fuer create_all)
from .migrations import run_light_migrations
from .regulatory_extraction_pid import (
    import_pid_process_identifiers,
    resolve_active_regulatory_version,
)

_DEFAULT_PDF = "data/regulatory/PID_3_3_Konsultationsfassung_20250801.pdf"
_DEFAULT_MIG = "data/regulatory/UTILMD_MIG_Gas_G1_1_20251001.pdf"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prüfidentifikatoren aus der PID-Übersicht in die Wissensbasis übernehmen"
    )
    parser.add_argument("--pdf", default=_DEFAULT_PDF,
                        help=f"Pfad zur PID-Datei (Default: {_DEFAULT_PDF})")
    parser.add_argument("--mig", default=_DEFAULT_MIG,
                        help=f"MIG-Datei für den Konsistenzabgleich (Default: {_DEFAULT_MIG}); "
                             "'' schaltet den Abgleich ab")
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
            # Ueber is_active aufloesen, nicht ueber den Namensstring.
            version = resolve_active_regulatory_version(db)
        if version is None:
            print("FEHLER: keine aktive RegulatoryVersion gefunden.", file=sys.stderr)
            return 2

        before = db.query(models.ProcessIdentifier).count()
        print(f"RegulatoryVersion: [{version.id}] {version.name}", flush=True)
        print(f"Dokument:          {args.pdf}", flush=True)
        print(f"ProcessIdentifier vorher: {before}", flush=True)
        print("=" * 78, flush=True)

        report = import_pid_process_identifiers(
            db, args.pdf, version.id, mig_pdf_path=args.mig or None
        )
        after = db.query(models.ProcessIdentifier).count()
        print(report.format_report(), flush=True)
        print(f"\nProcessIdentifier vorher/nachher: {before} -> {after}", flush=True)
        return 1 if report.errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
