"""CLI fuer den kapitelweisen AHB-Import (Issue #40, Auftrag Abschnitt 17).

Bewusst ein Kommandozeilenwerkzeug und KEIN API-Endpunkt: der Import ist ein
kuratierter Vorgang, der vom Menschen angestossen und dessen Report gelesen
wird. Ein Endpunkt und eine Admin-UI sind ausdruecklich nicht Teil dieses
Auftrags (Abschnitt 16).

    cd backend && ./venv/bin/python -m app.import_ahb \\
        --pdf data/regulatory/UTILMD_AHB_Gas_1_1_20251001.pdf \\
        --chapters 5 7
"""
from __future__ import annotations

import argparse
import sys

from .database import Base, SessionLocal, engine
from . import models  # noqa: F401  (registriert alle Modelle fuer create_all)
from .migrations import run_light_migrations
from .regulatory_extraction import (
    ChapterResult,
    import_ahb_document,
    resolve_active_regulatory_version,
)

_DEFAULT_PDF = "data/regulatory/UTILMD_AHB_Gas_1_1_20251001.pdf"


def _print_progress(result: ChapterResult) -> None:
    """Zwischenstand nach jedem Kapitel (Auftrag Abschnitt 2).

    Es soll waehrend des Laufs sichtbar sein, wo der Import steht -- nicht erst
    am Ende ein grosser Sammelbericht.
    """
    print(result.format_progress(), flush=True)
    print("-" * 72, flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AHB kapitelweise in die Wissensbasis importieren")
    parser.add_argument("--pdf", default=_DEFAULT_PDF, help=f"Pfad zur PDF-Datei (Default: {_DEFAULT_PDF})")
    parser.add_argument(
        "--chapters", nargs=2, metavar=("VON", "BIS"), default=None,
        help='Kapitelbereich ueber Nummernpraefix, z.B. --chapters 5 7',
    )
    parser.add_argument("--version-id", type=int, default=None,
                        help="RegulatoryVersion-ID; ohne Angabe wird die aktive Version verwendet")
    parser.add_argument("--nachrichtentyp", default="UTILMD")
    parser.add_argument("--sparte", default="gas")
    parser.add_argument("--message-version", default=None, help='z.B. "D:11A:UN:G1.1"')
    parser.add_argument("--reimport", action="store_true",
                        help="bereits importierten Dokumentstand kontrolliert neu aufbauen")
    args = parser.parse_args(argv)

    Base.metadata.create_all(bind=engine)
    run_light_migrations(engine)

    db = SessionLocal()
    try:
        if args.version_id is not None:
            version = db.get(models.RegulatoryVersion, args.version_id)
        else:
            # Ueber is_active aufloesen, nicht ueber den Namensstring -- der Name
            # ist kuratierter Freitext (Auftrag Abschnitt 3, Rueckfrage 5).
            version = resolve_active_regulatory_version(db)
        if version is None:
            print("FEHLER: keine aktive RegulatoryVersion gefunden.", file=sys.stderr)
            return 2

        print(f"RegulatoryVersion: [{version.id}] {version.name}", flush=True)
        print(f"Dokument:          {args.pdf}", flush=True)
        print("=" * 72, flush=True)

        report = import_ahb_document(
            db=db,
            pdf_path=args.pdf,
            regulatory_version_id=version.id,
            chapter_range=tuple(args.chapters) if args.chapters else None,
            nachrichtentyp=args.nachrichtentyp,
            sparte=args.sparte,
            message_version=args.message_version,
            reimport=args.reimport,
            progress=_print_progress,
        )
        print(report.format_report(), flush=True)
        return 1 if report.errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
