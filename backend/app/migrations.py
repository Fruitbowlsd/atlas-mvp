"""Leichtgewichtige Schema-Migration ohne Alembic.

`Base.metadata.create_all()` (siehe main.py) legt fehlende TABELLEN an, aendert
aber niemals Spalten einer bereits existierenden Tabelle. Fuer nachtraeglich
hinzugekommene Spalten braucht es deshalb diesen kleinen, idempotenten
Nachzieh-Schritt. Portabel fuer SQLite (lokal/aktuelles Railway-Deployment) und
Postgres (dokumentierte Option via DATABASE_URL) -- ueber den SQLAlchemy-
Inspector geprueft, keine DB-spezifischen Annahmen.
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from . import models

# Tabelle -> [(Spaltenname, DDL-Typ inkl. Default)] fuer alle Spalten, die nach
# der ersten Version des Schemas dazugekommen sind. Alle hier gelisteten Spalten
# sind nullable bzw. haben einen Default -- damit reicht ein einfaches
# ALTER TABLE ADD COLUMN, ein Tabellen-Rebuild ist nicht noetig.
_PENDING_COLUMNS = {
    # Mehrfach-Versionen-Konzept (Abschnitt 11.7), spaeter ergaenzt um die
    # kuratierte Zusammenfassung + Aenderungszeitstempel fuer die Kunden-Vorschau.
    "regulatory_versions": [
        ("is_active", "BOOLEAN DEFAULT FALSE"),
        ("valid_from", "TIMESTAMP"),
        ("created_at", "TIMESTAMP"),
        ("predecessor_version_id", "INTEGER"),
        ("summary", "TEXT"),
        ("updated_at", "TIMESTAMP"),
    ],
    # Konkrete Aufwandsschaetzung + Handlungsempfehlung fuer die Kunden-Ansicht,
    # plus Nachrichtentyp und Aenderungszeitstempel.
    "regulatory_changes": [
        ("effort_person_days", "INTEGER"),
        ("recommendation", "TEXT"),
        ("message_type", "VARCHAR"),
        ("updated_at", "TIMESTAMP"),
    ],
    # Multi-Tenancy (Abschnitt 13.2). Auf Railway wird die DB je Deploy neu
    # aufgebaut, hier geht es nur darum, dass lokale Entwicklungsdatenbanken
    # nicht kaputtgehen -- kein neuer Mechanismus, nur zwei weitere Spalten.
    "customers": [("tenant_id", "INTEGER")],
    "assessments": [
        ("tenant_id", "INTEGER"),
        ("sector", "VARCHAR DEFAULT 'gas'"),
        # Segmente je Sparte (Issue #16). Bestandszeilen werden unten aus
        # customer_segments nachgezogen.
        ("segments_gas", "VARCHAR DEFAULT ''"),
        ("segments_strom", "VARCHAR DEFAULT ''"),
    ],
    "users": [("is_atlas_admin", "BOOLEAN DEFAULT FALSE")],
    # Erste echte Codelisten-Extraktion (Issue #48). Beide Tabellen waren bis
    # dahin leer -- die Spalten sind rein additiv und nullable, ein Backfill
    # bestehender Zeilen ist deshalb nicht noetig.
    "code_lists": [
        ("quelle_dokument", "VARCHAR"),
        ("quelle_hash", "VARCHAR"),
        ("quelle_kapitel", "VARCHAR"),
    ],
    "code_list_entries": [
        ("werteart", "VARCHAR"),
        ("status", "VARCHAR"),
        ("richtung", "VARCHAR"),
        ("hinweise", "TEXT"),
        ("pruefidentifikatoren", "VARCHAR"),
        ("quelle_seite", "INTEGER"),
    ],
    # EVU-Profil (Abschnitt 14.2): Relevanz von einer Dimension (SLP/RLM) auf
    # drei erweitert. Die Defaults bilden den Ist-Stand ab -- der Katalog ist
    # heute reiner Gas-Katalog fuer SLP/RLM, deshalb strom/imsys/tlp auf FALSE.
    # Bestandszeilen bekommen damit genau die Werte, die inhaltlich stimmen.
    "requirements": [
        ("applies_to_imsys", "BOOLEAN DEFAULT FALSE"),
        ("applies_to_tlp", "BOOLEAN DEFAULT FALSE"),
        ("applies_to_gas", "BOOLEAN DEFAULT TRUE"),
        ("applies_to_strom", "BOOLEAN DEFAULT FALSE"),
    ],
    # SSO-Konfiguration je Tenant (Abschnitt 13.4)
    "tenants": [
        ("email_domain", "VARCHAR"),
        ("sso_provider", "VARCHAR"),
        ("sso_tenant_id", "VARCHAR"),
        ("is_active", "BOOLEAN DEFAULT TRUE"),
    ],
    # Regulatory-Extraction-Pipeline (Issue #40): Pruefidentifikator-Bezug und
    # Provenance an der Wissensbasis. Die drei Tabellen waren bisher leer, die
    # Spalten sind trotzdem als ALTER TABLE formuliert -- lokale Entwicklungs-
    # datenbanken haben die (leeren) Tabellen bereits im alten Schema angelegt.
    "message_definitions": [
        ("pi_nummer", "VARCHAR"),
        ("pi_id", "INTEGER"),
        ("quelle_dokument", "VARCHAR"),
        ("quelle_hash", "VARCHAR"),
        ("quelle_kapitel", "VARCHAR"),
        ("quelle_kapitel_titel", "VARCHAR"),
        ("quelle_seite_von", "INTEGER"),
        ("quelle_seite_bis", "INTEGER"),
    ],
    "message_segments": [
        ("segmentgruppe", "VARCHAR"),
        ("ahb_zeile", "VARCHAR"),
        ("pflichtigkeit", "VARCHAR"),
        ("bedingung", "TEXT"),
        ("bedingung_raw", "TEXT"),
        ("bedingung_referenzen", "VARCHAR"),
        ("quelle_seite", "INTEGER"),
    ],
    "message_fields": [
        ("bedingung_raw", "TEXT"),
        ("bedingung_referenzen", "VARCHAR"),
        ("segmentgruppe", "VARCHAR"),
        ("code", "VARCHAR"),
        ("pflichtigkeit", "VARCHAR"),
        ("quelle_seite", "INTEGER"),
    ],
}

# Neu hinzugekommene updated_at-Spalten waeren fuer Bestandszeilen NULL -- die
# Kunden-Vorschau wuerde dann "Zuletzt aktualisiert: -" anzeigen, obwohl ein
# sinnvoller Wert bekannt ist. Daher einmalig aus created_at nachziehen.
_UPDATED_AT_BACKFILL = ["regulatory_versions", "regulatory_changes"]


def run_light_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table, columns in _PENDING_COLUMNS.items():
        if table not in existing_tables:
            continue  # wird gleich frisch von create_all() angelegt, nichts nachzuziehen

        existing_columns = {c["name"] for c in inspector.get_columns(table)}
        missing = [(name, ddl) for name, ddl in columns if name not in existing_columns]
        if not missing:
            continue

        with engine.begin() as conn:
            for name, ddl in missing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))

            if table in _UPDATED_AT_BACKFILL and any(n == "updated_at" for n, _ in missing):
                conn.execute(text(
                    f"UPDATE {table} SET updated_at = created_at WHERE updated_at IS NULL"
                ))

            # Segmente je Sparte (Issue #16): Bestandszeilen tragen ihre Segmente
            # noch in der gemeinsamen Spalte. Ohne dieses Nachziehen stuenden sie
            # nach der Migration mit leeren Segmentmengen da -- und ein bestehendes
            # Assessment zeigte auf einmal gar keine Anforderungen mehr an.
            if table == "assessments" and any(n == "segments_gas" for n, _ in missing):
                conn.execute(text(
                    "UPDATE assessments SET segments_gas = COALESCE(customer_segments, '') "
                    "WHERE (segments_gas IS NULL OR segments_gas = '') "
                    "AND COALESCE(sector, 'gas') LIKE '%gas%'"
                ))
                conn.execute(text(
                    "UPDATE assessments SET segments_strom = COALESCE(customer_segments, '') "
                    "WHERE (segments_strom IS NULL OR segments_strom = '') "
                    "AND COALESCE(sector, '') LIKE '%strom%'"
                ))

    if "regulatory_versions" in existing_tables:
        with engine.begin() as conn:
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
    _ensure_message_definition_uniqueness(engine)


def _ensure_message_definition_uniqueness(engine: Engine) -> None:
    """Doppelte MessageDefinition je (Version, Nachrichtentyp, PI, Kapitel)
    verhindern -- Abschnitt 15/19 des Auftrags: ein erneuter Import derselben
    Datei darf keine unkontrollierten Duplikate erzeugen.

    Bewusst als UNIQUE INDEX und nicht als Tabellen-Constraint: SQLite kann
    einer bestehenden Tabelle per ALTER TABLE keinen Constraint hinzufuegen,
    ein Tabellen-Rebuild waere fuer diesen Zweck unverhaeltnismaessig. Der
    Index wirkt in SQLite wie in Postgres identisch; das __table_args__ im
    Modell greift zusaetzlich fuer frisch angelegte Datenbanken.
    """
    inspector = inspect(engine)
    if "message_definitions" not in inspector.get_table_names():
        return  # create_all() legt die Tabelle gleich mit dem Constraint an

    with engine.begin() as conn:
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_message_definition_per_version_pi_chapter "
            "ON message_definitions (regulatory_version_id, nachrichtentyp, pi_nummer, quelle_kapitel)"
        ))


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
