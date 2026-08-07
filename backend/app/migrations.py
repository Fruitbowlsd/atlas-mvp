"""Leichtgewichtige Schema-Migration ohne Alembic.

`Base.metadata.create_all()` (siehe main.py) legt fehlende TABELLEN an, aendert
aber niemals Spalten einer bereits existierenden Tabelle. Fuer neue Spalten an
`regulatory_versions` (Mehrfach-Versionen-Konzept, Abschnitt 11.7) braucht es
deshalb diesen kleinen, idempotenten Nachzieh-Schritt. Portabel fuer SQLite
(lokal/aktuelles Railway-Deployment) und Postgres (dokumentierte Option via
DATABASE_URL) -- ueber den SQLAlchemy-Inspector geprueft, keine DB-spezifischen
Annahmen.
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from . import models

# (Spaltenname, DDL-Typ inkl. Default) -- alle Spalten, die nachtraeglich zu
# regulatory_versions dazugekommen sind.
_PENDING_COLUMNS = [
    ("is_active", "BOOLEAN DEFAULT FALSE"),
    ("valid_from", "TIMESTAMP"),
    ("created_at", "TIMESTAMP"),
    ("predecessor_version_id", "INTEGER"),
]


def run_light_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    if "regulatory_versions" not in inspector.get_table_names():
        return  # Tabelle wird gleich frisch von create_all() angelegt, nichts nachzuziehen

    existing_columns = {c["name"] for c in inspector.get_columns("regulatory_versions")}

    with engine.begin() as conn:
        for column, ddl in _PENDING_COLUMNS:
            if column in existing_columns:
                continue
            conn.execute(text(f"ALTER TABLE regulatory_versions ADD COLUMN {column} {ddl}"))

        # Bestandsdaten aus der Zeit vor dem Mehrfach-Versionen-Konzept haben
        # is_active noch nicht gesetzt -- genau eine aktive Version sicherstellen,
        # sonst liefert get_active_regulatory_version() plötzlich nichts mehr.
        has_active = conn.execute(
            text("SELECT COUNT(*) FROM regulatory_versions WHERE is_active = TRUE")
        ).scalar()
        if not has_active:
            conn.execute(text(
                "UPDATE regulatory_versions SET is_active = TRUE "
                "WHERE id = (SELECT MIN(id) FROM regulatory_versions)"
            ))

    _migrate_requirement_code_uniqueness(engine)


def _migrate_requirement_code_uniqueness(engine: Engine) -> None:
    """Requirement.code war anfangs global unique -- fuer die Regulatory-
    Intelligence-Diff-Logik (Abschnitt 11.2/11.7) muss derselbe Code aber in
    mehreren RegulatoryVersion-Katalogen parallel vorkommen koennen (z.B.
    unveraendert von der alten in die neue Version uebernommen)."""
    inspector = inspect(engine)
    if "requirements" not in inspector.get_table_names():
        return  # frische DB -- create_all() legt die Tabelle gleich mit dem neuen Schema an

    has_old_global_unique = any(
        uc["column_names"] == ["code"] for uc in inspector.get_unique_constraints("requirements")
    ) or any(
        idx.get("unique") and idx["column_names"] == ["code"]
        for idx in inspector.get_indexes("requirements")
    )
    if not has_old_global_unique:
        return  # schon migriert

    if engine.dialect.name != "sqlite":
        raise RuntimeError(
            "requirements.code hat noch die alte globale UNIQUE-Constraint. Fuer "
            f"'{engine.dialect.name}' unterstuetzt diese leichte Migration keinen "
            "automatischen Rebuild -- bitte manuell per ALTER TABLE ... DROP "
            "CONSTRAINT / ADD CONSTRAINT UNIQUE (code, regulatory_version_id) nachziehen."
        )

    # SQLite kennt kein ALTER TABLE ... DROP CONSTRAINT -- Tabelle wird deshalb
    # unter neuem Namen mit dem aktuellen Modell-Schema neu angelegt und die
    # Daten 1:1 (inkl. id, wegen bestehender Fremdschluessel aus assessment_
    # requirements/findings) umkopiert.
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE requirements RENAME TO requirements_pre_versioning"))
        models.Requirement.__table__.create(bind=conn)
        columns = ", ".join(c.name for c in models.Requirement.__table__.columns)
        conn.execute(text(
            f"INSERT INTO requirements ({columns}) SELECT {columns} FROM requirements_pre_versioning"
        ))
        conn.execute(text("DROP TABLE requirements_pre_versioning"))
