from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class RegulatoryVersion(Base):
    __tablename__ = "regulatory_versions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)          # z.B. "GeLi Gas 2.0 / UTILMD Gas G1.1"
    sector = Column(String, nullable=False)         # "gas"
    status = Column(String, default="konsultation")  # konsultation | final | verbindlich
    source_reference = Column(String)
    # Ab hier: Mehrfach-Versionen-Konzept (Abschnitt 11.7 der Planung) -- vorher gab
    # es im System immer nur genau eine RegulatoryVersion.
    is_active = Column(Boolean, default=False)       # genau eine Version = Default fuer neue Assessments
    valid_from = Column(DateTime, nullable=True)     # z.B. Stichtag "01.10.2027"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    predecessor_version_id = Column(Integer, ForeignKey("regulatory_versions.id"), nullable=True)
    # Kuratierte Kurzfassung "was aendert sich mit diesem Release" fuer die Kunden-
    # Vorschau. Bewusst ein manuell gepflegtes Feld, KEINE Live-Generierung -- im MVP
    # gibt es keine Analyse-Pipeline, die das laufend erzeugen koennte (Abschnitt 11.8).
    summary = Column(Text, nullable=True)

    requirements = relationship("Requirement", back_populates="regulatory_version")
    changes = relationship("RegulatoryChange", back_populates="regulatory_version")
    predecessor = relationship("RegulatoryVersion", remote_side=[id])


class ProcessGroup(Base):
    __tablename__ = "process_groups"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)   # z.B. "registration"
    name = Column(String, nullable=False)                # "Anmeldung"
    sequence = Column(Integer, default=0)

    pis = relationship("ProcessIdentifier", back_populates="process_group")


class ProcessIdentifier(Base):
    __tablename__ = "process_identifiers"

    id = Column(Integer, primary_key=True)
    pi_number = Column(String, unique=True, nullable=False)   # "44001"
    name = Column(String, nullable=False)
    sender_role = Column(String)
    receiver_role = Column(String)
    message_type = Column(String, default="UTILMD")
    process_group_id = Column(Integer, ForeignKey("process_groups.id"))
    criticality = Column(String, default="mittel")   # kritisch | hoch | mittel | niedrig
    weight = Column(Float, default=1.0)

    process_group = relationship("ProcessGroup", back_populates="pis")
    requirements = relationship("Requirement", back_populates="pi")


class Requirement(Base):
    __tablename__ = "requirements"
    # code ist NICHT mehr global unique, sondern nur je RegulatoryVersion: fuer die
    # Diff-Logik (Abschnitt 11.2/11.7) muss derselbe Code in mehreren Versionen
    # parallel vorkommen koennen, z.B. unveraendert von der alten in die neue
    # Version uebernommen.
    __table_args__ = (UniqueConstraint("code", "regulatory_version_id", name="uq_requirement_code_per_version"),)

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    pi_id = Column(Integer, ForeignKey("process_identifiers.id"))
    transaction_reason = Column(String)     # z.B. "E03 - Wechsel"
    response_code = Column(String)          # z.B. "E15", "ZC5"
    criticality = Column(String, default="mittel")
    weight = Column(Float, default=1.0)
    applies_to_slp = Column(Boolean, default=True)
    applies_to_rlm = Column(Boolean, default=True)
    is_conditional = Column(Boolean, default=False)
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"))

    pi = relationship("ProcessIdentifier", back_populates="requirements")
    regulatory_version = relationship("RegulatoryVersion", back_populates="requirements")


class Tenant(Base):
    """Organisation, die Atlas nutzt (Abschnitt 13.2). Die Grenze, an der Kundendaten
    getrennt werden -- geteilte Plattformdaten (Requirement-Katalog, RegulatoryVersion,
    RegulatoryChange) haengen bewusst NICHT am Tenant (13.1)."""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)                 # z.B. "Demo Gaslieferant GmbH"
    slug = Column(String, unique=True, nullable=False)    # z.B. "demo-gaslieferant"
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- SSO (Abschnitt 13.4) ---
    # Domain der Firmen-Mailadressen, z.B. "stadtwerke-x.de". Steuert zweierlei:
    # welcher Login-Weg im zweiten Schritt angeboten wird, UND welchem Tenant ein
    # per SSO neu auftauchender Nutzer zugeordnet wird.
    email_domain = Column(String, nullable=True)
    sso_provider = Column(String, nullable=True)   # None | "entra"
    # Verzeichnis-ID beim Anbieter (bei Entra der "tid"-Claim). Wird beim Login
    # gegen das ID-Token geprueft -- ohne diese Pruefung koennte sich sonst jeder
    # beliebige Microsoft-Account anmelden, nicht nur die eigene Organisation.
    sso_tenant_id = Column(String, nullable=True)

    customers = relationship("Customer", back_populates="tenant")
    users = relationship("User", back_populates="tenant")


class User(Base):
    """Individuelles Nutzerkonto (Abschnitt 13.4) -- loest das eine gemeinsame
    Passwort ab. Jeder Nutzer gehoert zu genau einem Tenant; daraus leitet sich ab,
    welche Kundendaten er sieht (siehe auth.get_current_tenant_id)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    # Leer bei SSO-Nutzern -- die haben bei uns bewusst kein lokales Passwort.
    password_hash = Column(String, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="users")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    market_role = Column(String, default="lieferant")
    sector = Column(String, default="gas")
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)

    tenant = relationship("Tenant", back_populates="customers")
    assessments = relationship("Assessment", back_populates="customer")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    # Bewusst zusaetzlich zu Customer.tenant_id: Assessments werden an mehreren
    # Stellen ueber die nackte ID geladen (Import, Impact, calculate). Mit eigener
    # Spalte ist der Tenant-Filter dort eine sichtbare Einzeile statt eines leicht
    # vergessenen Joins. Wird beim Anlegen aus dem Customer uebernommen und nie
    # unabhaengig davon geaendert.
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"))
    business_scenario = Column(String, default="lieferantenwechsel")
    customer_segments = Column(String, default="slp,rlm")   # einfache CSV-Liste im MVP
    status = Column(String, default="in_bearbeitung")
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="assessments")
    regulatory_version = relationship("RegulatoryVersion")
    requirement_statuses = relationship("AssessmentRequirement", back_populates="assessment")
    score_result = relationship("ScoreResult", back_populates="assessment", uselist=False)
    findings = relationship("Finding", back_populates="assessment")


class AssessmentRequirement(Base):
    __tablename__ = "assessment_requirements"

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    requirement_id = Column(Integer, ForeignKey("requirements.id"))

    relevance_status = Column(String, default="relevant")      # relevant | nicht_relevant
    implementation_status = Column(String, default="nicht_implementiert")
    test_status = Column(String, default="nicht_getestet")
    result_status = Column(String, default="offen")            # erfolgreich | fehlgeschlagen | offen
    evidence_status = Column(String, default="fehlt")          # vorhanden | fehlt
    comment = Column(Text)
    responsible_person = Column(String)
    last_test_date = Column(DateTime, nullable=True)
    data_source = Column(String, default="manuell")            # manuell | import
    import_source_name = Column(String, nullable=True)         # z.B. "CSV-Import", "SAP Cloud ALM"
    last_synced_at = Column(DateTime, nullable=True)

    assessment = relationship("Assessment", back_populates="requirement_statuses")
    requirement = relationship("Requirement")


class ScoreResult(Base):
    __tablename__ = "score_results"

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), unique=True)
    regulatory_coverage = Column(Float)
    quality_grade = Column(Float)
    implementation_quality = Column(Float)
    test_quality = Column(Float)
    evidence_quality = Column(Float)
    actuality = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="score_result")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    severity = Column(String, default="mittel")
    title = Column(String)
    description = Column(Text)
    recommendation = Column(Text)

    assessment = relationship("Assessment", back_populates="findings")
    requirement = relationship("Requirement")


class RegulatoryChange(Base):
    """Einzelne regulatorische Aenderung einer (neuen) RegulatoryVersion -- Kernentitaet
    der Regulatory Intelligence (Planungsdokument Abschnitt 11.3). Wird zunaechst
    manuell durch einen Kurator angelegt (11.4); die Anthropic-Anbindung (11.2, Schritt
    4) ergaenzt spaeter KI-Vorschlaege ueber das origin-Feld -- Muster wie bei
    AssessmentRequirement.data_source ("System schlaegt vor, Mensch bestaetigt")."""
    __tablename__ = "regulatory_changes"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    # neuer_prozess | neues_pflichtfeld | neuer_code | neue_qualitaetsregel | neuer_testfall
    category = Column(String, nullable=False)
    process_group_id = Column(Integer, ForeignKey("process_groups.id"), nullable=True)
    pi_id = Column(Integer, ForeignKey("process_identifiers.id"), nullable=True)
    risk = Column(String, default="mittel")        # hoch | mittel | niedrig
    effort = Column(String, default="mittel")      # hoch | mittel | niedrig
    # Konkrete Aufwandsschaetzung zusaetzlich zur groben Stufe -- mit "mittel" allein
    # laesst sich keine Ressourcenplanung machen. Optional, weil nicht jede Aenderung
    # zum Kurationszeitpunkt schon belastbar schaetzbar ist.
    effort_person_days = Column(Integer, nullable=True)
    # Handlungsempfehlung fuer den Kunden ("was ist jetzt zu tun") -- Gegenstueck zu
    # Finding.recommendation im Assessment-Bereich.
    recommendation = Column(Text, nullable=True)
    source_url = Column(String)
    # Nachrichtentyp (UTILMD, MSCONS, ...). Bewusst nullable: ist ein PI verknuepft,
    # steht der Typ schon an ProcessIdentifier.message_type und wird von dort
    # abgeleitet (siehe effective_message_type) -- dieses Feld dient als Angabe fuer
    # katalogweite Aenderungen ohne PI. So gibt es nie zwei widersprechende Werte.
    message_type = Column(String, nullable=True)
    status = Column(String, default="entwurf")     # zu_pruefen | entwurf | veroeffentlicht (Kanban-Spalten)
    origin = Column(String, default="manuell")     # manuell | ki_vorschlag
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def effective_message_type(self) -> str | None:
        """Nachrichtentyp der Aenderung: eigener Wert hat Vorrang, sonst der des
        verknuepften PI. Eine einzige Quelle fuer die Anzeige und die KPI-Zaehlung."""
        if self.message_type:
            return self.message_type
        return self.pi.message_type if self.pi else None

    regulatory_version = relationship("RegulatoryVersion", back_populates="changes")
    process_group = relationship("ProcessGroup")
    pi = relationship("ProcessIdentifier")
    technology_mappings = relationship("RegulatoryChangeTechnologyMapping", back_populates="regulatory_change")


class TechnologySystem(Base):
    """Ebene 2 (optionaler 'Technology Pack'), z.B. 'SAP Utilities'. In dieser Session
    noch ohne Kuratoren-UI/Scraper -- Tabelle wird bereits angelegt, um eine zweite
    Schema-Aenderung zu vermeiden, wenn Ebene 2 umgesetzt wird (siehe 11.7)."""
    __tablename__ = "technology_systems"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)   # z.B. "SAP Utilities"
    vendor = Column(String)                 # z.B. "SAP"

    release_notes = relationship("TechnologyReleaseNote", back_populates="technology_system")


class TechnologyReleaseNote(Base):
    """Nur Referenz: Titel + eigene Kurzfassung + Link -- NIE Volltexte spiegeln.
    Herstellerdokumente wie SAP Notes sind lizenzpflichtig/nicht frei
    weiterverbreitbar (siehe 11.1)."""
    __tablename__ = "technology_release_notes"

    id = Column(Integer, primary_key=True)
    technology_system_id = Column(Integer, ForeignKey("technology_systems.id"), nullable=False)
    title = Column(String, nullable=False)
    own_summary = Column(Text)
    external_url = Column(String)

    technology_system = relationship("TechnologySystem", back_populates="release_notes")


class RegulatoryChangeTechnologyMapping(Base):
    """Verknuepfung n:m -- welche RegulatoryChange wird durch welche
    TechnologyReleaseNote in einem konkreten System umgesetzt."""
    __tablename__ = "regulatory_change_technology_mappings"

    id = Column(Integer, primary_key=True)
    regulatory_change_id = Column(Integer, ForeignKey("regulatory_changes.id"), nullable=False)
    technology_release_note_id = Column(Integer, ForeignKey("technology_release_notes.id"), nullable=False)

    regulatory_change = relationship("RegulatoryChange", back_populates="technology_mappings")
    technology_release_note = relationship("TechnologyReleaseNote")
