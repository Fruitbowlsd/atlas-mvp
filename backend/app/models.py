from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date, Text, UniqueConstraint
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
    # Relevanz-Dimensionen (Abschnitt 14.2). Die beiden Segment-Flags gab es
    # zuerst; sie bleiben unveraendert bestehen, weil diff.py sie als
    # vergleichsrelevante Spalten fuehrt -- ein Umbenennen liesse beim naechsten
    # Versionsvergleich JEDES Requirement als geaendert erscheinen.
    applies_to_slp = Column(Boolean, default=True)
    applies_to_rlm = Column(Boolean, default=True)
    applies_to_imsys = Column(Boolean, default=False)
    applies_to_tlp = Column(Boolean, default=False)
    # Sparte. Der Katalog ist heute reiner Gas-Katalog, deshalb strom=False:
    # lieber ein ehrlicher Leerzustand als Gas-Anforderungen, die faelschlich
    # als fuer Strom geprueft erscheinen. Strom-Requirements folgen aus der
    # Grundanalyse.
    applies_to_gas = Column(Boolean, default=True)
    applies_to_strom = Column(Boolean, default=False)
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
    is_active = Column(Boolean, default=True)
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
    # Atlas-internes Personal (Issue #13). Bewusst ein Nutzer-Flag und nicht nur ein
    # Umgebungs-Token: der Admin-Bereich zeigt tenant-uebergreifende Daten, der
    # Zugang darf deshalb nicht davon abhaengen, ob eine Variable gesetzt ist.
    is_atlas_admin = Column(Boolean, default=False)
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
    # Sparte auf dem Assessment, obwohl sie auch am Customer haengt -- gleiche
    # Begruendung wie bei tenant_id: die Relevanzfilterung laeuft ueber das
    # Assessment und soll dafuer keinen Join brauchen. Beim Anlegen aus dem
    # Customer uebernommen.
    # Sparten als CSV-Menge: "gas" | "strom" | "gas,strom". Stadtwerke betreiben
    # oft beides; der bisherige Einzelwert bleibt als einelementige Menge gueltig,
    # deshalb dieselbe Spalte statt einer neuen.
    sector = Column(String, default="gas")
    # Segmente je Sparte, bewusst getrennt statt einer gemeinsamen Menge: bei
    # "Gas(SLP) + Strom(iMSys)" wuerde eine gemeinsame Menge {slp,imsys} eine
    # Anforderung durchlassen, die nur fuer Gas UND nur fuer iMSys gilt -- eine
    # Kombination, die dieser Kunde gar nicht hat.
    segments_gas = Column(String, default="")      # slp,rlm,tlp
    segments_strom = Column(String, default="")    # slp,rlm,imsys,tlp
    # Vereinigung beider Mengen, NUR zur Anzeige (Kundenprofil, Admin-Tabelle,
    # Sidebar). Wird an genau einer Stelle beim Speichern mitgeschrieben und ist
    # nie Grundlage einer Filterung -- dafuer sind die beiden Felder oben da.
    customer_segments = Column(String, default="slp,rlm")
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


# --- Regulatorische Wissensbasis (Abschnitt 14.2) ---------------------------
#
# Diese sieben Tabellen sind das Fundament fuer EDIFACT-Generator,
# Nachrichtensimulation und abgeleitete Testfaelle. Sie werden hier bewusst nur
# als Struktur angelegt: befuellt werden sie aus der Grundanalyse, die ein
# eigener Schritt ist.
#
# Sie haengen an regulatory_version_id und NICHT am Tenant: es ist geteiltes
# Atlas-Wissen wie der Requirement-Katalog, kein Kundengeheimnis (Abschnitt 13.1).


class MessageDefinition(Base):
    """Ein Nachrichtentyp in einer konkreten regulatorischen Fassung -- z.B.
    UTILMD in D:11A:UN:G1.1 fuer Gas.

    Granularitaet ist bewusst EIN Eintrag je Pruefidentifikator, nicht je
    Anwendungsuebersicht: eine AHB-Tabelle wie "Anmeldung" fuehrt 44001, 44002
    und 44003 nebeneinander und vergibt fuer dasselbe Feld je PI
    unterschiedliche Muss/Soll/Kann-Auspraegungen. Eine MessageDefinition je
    Tabelle wuerde genau diese Unterscheidung einebnen.
    """
    __tablename__ = "message_definitions"
    # Regulatorische Identitaet (Abschnitt 7 des Auftrags): derselbe PI in einer
    # anderen Fassung ist fachlich NICHT dasselbe Objekt, deshalb gehoert die
    # Version in den Schluessel. quelle_kapitel ist mit drin, weil ein PI in
    # mehreren Anwendungsuebersichten auftauchen kann (z.B. 44111 in 5.11.3 und
    # 5.12.4) und beide Vorkommen eigenstaendige Auspraegungen sind.
    __table_args__ = (
        UniqueConstraint(
            "regulatory_version_id", "nachrichtentyp", "pi_nummer", "quelle_kapitel",
            name="uq_message_definition_per_version_pi_chapter",
        ),
    )

    id = Column(Integer, primary_key=True)
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"), nullable=False)
    nachrichtentyp = Column(String, nullable=False)   # UTILMD | MSCONS | APERAK | ...
    version = Column(String)                          # z.B. "D:11A:UN:G1.1"
    sparte = Column(String, default="gas")            # "gas" | "strom"
    beschreibung = Column(Text)
    # Pruefidentifikator. pi_nummer ist die im Dokument gedruckte Nummer und wird
    # IMMER gefuellt; pi_id bleibt NULL, solange der PI nicht im kuratierten
    # ProcessIdentifier-Katalog steht. Bewusst so herum: der Katalog wird nicht
    # automatisch aus dem PDF erweitert (das waere geraten), die Information aus
    # dem Dokument geht aber trotzdem nicht verloren.
    pi_nummer = Column(String)
    pi_id = Column(Integer, ForeignKey("process_identifiers.id"), nullable=True)
    # Provenance (Abschnitt 6.2). quelle_hash ist der SHA-256 der Originaldatei
    # und traegt zugleich die Re-Import-Erkennung (Abschnitt 15).
    quelle_dokument = Column(String)
    quelle_hash = Column(String)
    quelle_kapitel = Column(String)
    quelle_kapitel_titel = Column(String)
    quelle_seite_von = Column(Integer)
    quelle_seite_bis = Column(Integer)
    # Herkunft der Grammatik (ADR-001). "MIG" kennzeichnet eine generische, NICHT
    # an einen Pruefidentifikator gebundene Nachrichtenstruktur; NULL heisst
    # "nicht aus der MIG" und gilt damit fuer den gesamten AHB-Bestand. Der wird
    # bewusst nicht nachtraeglich umgeschrieben -- die Herkunft bereits
    # importierter Daten wird nicht rueckwirkend umgedeutet.
    grammatik_quelle = Column(String)                 # "MIG" | NULL

    regulatory_version = relationship("RegulatoryVersion")
    pi = relationship("ProcessIdentifier")
    segments = relationship(
        "MessageSegment", back_populates="message_definition", order_by="MessageSegment.position"
    )


class MessageSegment(Base):
    """Ein Segment innerhalb einer Nachricht (BGM, DTM, LOC, NAD, ...).
    position haelt die Reihenfolge fest, in der das Segment in der Nachricht
    steht -- fuer den Generator ist das die Bauanleitung."""
    __tablename__ = "message_segments"

    id = Column(Integer, primary_key=True)
    message_definition_id = Column(Integer, ForeignKey("message_definitions.id"), nullable=False)
    segment_code = Column(String, nullable=False)     # BGM | DTM | LOC | NAD | ...
    position = Column(Integer, default=0)
    bezeichnung = Column(String)
    pflicht = Column(Boolean, default=False)
    kardinalitaet = Column(String)                    # "1" | "0..1" | "1..9"
    wiederholbar = Column(Boolean, default=False)
    # Segmentgruppe und AHB-Zeilennummer stehen im Dokument in eigenen Spalten
    # ("SG4" / "00022") und sind die Adresse, unter der ein Mensch die Zeile im
    # PDF wiederfindet -- deshalb erhalten, nicht in segment_code mischen.
    segmentgruppe = Column(String)                    # "SG4"
    ahb_zeile = Column(String)                        # "00022"
    # pflicht (Boolean) kann Muss/Soll/Kann nicht unterscheiden. Die Spalte
    # bleibt fuer bestehende Leser erhalten (Muss -> True), die volle
    # Auspraegung steht in pflichtigkeit -- Abschnitt 12 verlangt, dass die
    # Pflichtigkeit fuer den spaeteren Validator nicht verlorengeht.
    pflichtigkeit = Column(String)                    # "Muss" | "Soll" | "Kann"
    bedingung = Column(Text)                          # aufgeloeste Fussnoten
    bedingung_raw = Column(Text)                      # Zellinhalt, z.B. "Muss [28] ∧ [64]"
    bedingung_referenzen = Column(String)             # "28,64"
    quelle_seite = Column(Integer)
    # --- Ab hier: generische Nachrichtengrammatik aus der MIG (ADR-001).
    # Von der AHB-Extraktion nicht befuellt, von der MIG-Extraktion immer.
    #
    # mig_nr ist die Spalte "Nr" ("Laufende Segmentnummer im Guide"). Sie ist
    # innerhalb EINES Dokuments eindeutig (148/148 in G1.1) und damit der einzige
    # brauchbare Positionsschluessel -- kein inhaltsbasierter Kandidat kommt an
    # Eindeutigkeit heran, weil sich SG8 vierzehnmal mit gleichlautenden
    # Positionen wiederholt.
    #
    # ACHTUNG (ADR-001, Leitsatz 2): mig_nr ist KEINE versionsuebergreifende
    # Identitaet. Die Nummerierung laeuft lueckenlos, und die Aenderungshistorie
    # der G1.1 belegt ein eingefuegtes Segment -- jede nachfolgende Nummer hat
    # sich dadurch verschoben. Ein Delta darf ein Segment deshalb NIE allein
    # anhand einer geaenderten mig_nr als geaendert werten; verglichen wird der
    # strukturelle Inhalt (segment_code, Pfad, Ebene, Zaehler, Name, Status,
    # Format, MaxWdh).
    mig_nr = Column(String)                           # "00038"
    mig_zaehler = Column(String)                      # "0360" -- Position im UN/CEFACT-Standard
    # Vollstaendiger Segmentgruppenpfad. segmentgruppe (oben) haelt nur die
    # innerste Gruppe; erst der Pfad unterscheidet SG4/SG6 von SG4/SG8.
    segmentgruppen_pfad = Column(String)              # "SG4/SG6"
    ebene = Column(Integer)                           # 0..4
    # Zwei Status-, zwei MaxWdh-Spalten: die MIG fuehrt den allgemeinen
    # EDIFACT-Standard und die BDEW-Festlegung nebeneinander, und sie weichen
    # regelmaessig voneinander ab. pflicht/kardinalitaet/wiederholbar koennen das
    # nicht tragen -- siehe Klassendoc von MessageField.status_bdew_raw.
    status_standard_raw = Column(String)              # "M" | "C"
    status_bdew_raw = Column(String)                  # "M" | "R" | "D" | "N" | "O"
    max_wdh_standard = Column(String)                 # "9", "99999"
    max_wdh_bdew = Column(String)                     # "1", "5"
    # Block "Bemerkung:" bzw. "Beispiel:" unter der Datenelementtabelle. Bewusst
    # eigene Felder: bedingung traegt AHB-Fussnotensemantik, und das
    # EDIFACT-Beispiel ist ein Segment-, kein Feldattribut. 131 von 148 Segmenten
    # tragen eine Bemerkung, 148 von 148 ein Beispiel -- das sind keine Randnotizen.
    anwendungshinweis = Column(Text)
    beispiel_edifact = Column(Text)                   # "DTM+137:199904081315?+00:303'"

    message_definition = relationship("MessageDefinition", back_populates="segments")
    fields = relationship("MessageField", back_populates="segment")


class MessageField(Base):
    """Ein Datenelement innerhalb eines Segments. position ist die EDIFACT-
    Notation ("1001", "C507.2380"), deshalb String und nicht Integer."""
    __tablename__ = "message_fields"

    id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey("message_segments.id"), nullable=False)
    position = Column(String, nullable=False)         # "1001" | "C507.2380"
    bezeichnung = Column(String)
    datentyp = Column(String)                         # "an" | "n" | "a"
    laenge = Column(Integer)
    pflicht = Column(Boolean, default=False)
    # Wenn gesetzt, sind nur Werte aus dieser Codeliste zulaessig -- Grundlage
    # sowohl fuer die Generierung als auch fuer die spaetere Validierung.
    codelist_id = Column(Integer, ForeignKey("code_lists.id"), nullable=True)
    beispielwert = Column(String)
    # Freitext fuer Wenn-Dann-Regeln, die sich nicht in Spalten abbilden lassen
    # ("nur bei Transaktionsgrund E03"). Bewusst Text und keine Regelsprache --
    # welche Formen wirklich vorkommen, weiss erst die Grundanalyse.
    bedingung = Column(Text)
    # bedingung_raw ist der unveraenderte Zellinhalt ("X [931] [494]") und darf
    # laut Abschnitt 6.2/8 NIE verworfen werden: die Aufloesung in bedingung ist
    # eine Interpretation, der Rohwert bleibt die pruefbare Quelle.
    bedingung_raw = Column(Text)
    bedingung_referenzen = Column(String)             # "931,494"
    segmentgruppe = Column(String)                    # "SG4"
    code = Column(String)                             # Qualifier, z.B. "92", "E01", "Z36"
    pflichtigkeit = Column(String)                    # "X" wenn im PI genutzt, sonst leer
    quelle_seite = Column(Integer)
    # --- Ab hier: Rohwerte der MIG (ADR-001, Leitsatz "Raw Regulatory Data
    # zuerst, Atlas-Semantik danach"). Von der AHB-Extraktion nicht befuellt.
    #
    # Die MIG fuehrt je Datenelement ZWEI Status- und ZWEI Formatangaben: den
    # allgemeinen EDIFACT-Standard und die BDEW-Festlegung. In 536 von 755
    # Datenelementen der G1.1 weichen die Statuswerte voneinander ab.
    #
    # pflicht (Boolean) kann das nicht abbilden und ist deshalb NICHT die
    # regulatorische Wahrheit, sondern eine abgeleitete Kompatibilitaetsspalte
    # (Ableitungsregel: siehe pflicht_aus_status in
    # regulatory_extraction_mig_layout.py). Konkret gehen dort zwei fachlich
    # GEGENSAETZLICHE Zustaende auf denselben Wert:
    #   D = "Abhaengig von/Dependent" -> bedingt erlaubt   -> pflicht = False
    #   N = "Nicht benutzt/Not used"  -> verboten          -> pflicht = False
    # Ein Validator MUSS status_bdew_raw lesen, nicht pflicht.
    status_standard_raw = Column(String)              # "M" | "C"
    status_bdew_raw = Column(String)                  # "M" | "R" | "D" | "N" | "O"
    # Format als unveraenderter String, NICHT zerlegt in datentyp/laenge: die
    # Zerlegung verloere die Unterscheidung fest/variabel -- "n5" (genau 5) und
    # "n..6" (bis zu 6) waeren danach nicht mehr auseinanderzuhalten.
    format_standard_raw = Column(String)              # "an..70"
    format_bdew_raw = Column(String)                  # "n5"
    # Zusammengefuehrte Zelle "Anwendung / Bemerkung". Kann sehr lang sein -- die
    # groesste Zelle der G1.1 umfasst 144 Zeilen (die Pruefidentifikator-Liste).
    anwendung_raw = Column(Text)

    segment = relationship("MessageSegment", back_populates="fields")
    codelist = relationship("CodeList")
    codelist_referenzen = relationship(
        "MessageFieldCodeList", back_populates="message_field", cascade="all, delete-orphan"
    )


class MessageFieldCodeList(Base):
    """Verweis eines Datenelements auf eine Codeliste -- n:m (ADR-001).

    MessageField.codelist_id ist eine 1:1-Beziehung und bildet die Realitaet
    nicht ab: DE1131 des STS-Segments referenziert in EINER Zelle 50 Codelisten
    ("G_0002 Codeliste Gas Nr. G_0002", "GS_001 Codeliste Gas und Strom ...").
    Eine davon auszuwaehlen waere geraten, alle zu verwerfen waere Verlust.

    referenz_raw haelt den unveraenderten Zellinhalt, referenz_id die daraus
    gelesene Kennung. codelist_id bleibt NULL, solange die referenzierte
    Codeliste nicht importiert ist -- die Referenz geht dadurch nicht verloren
    und wird nachtraeglich aufloesbar, ohne den Parser anzufassen.
    """
    __tablename__ = "message_field_code_lists"
    __table_args__ = (
        UniqueConstraint(
            "message_field_id", "referenz_id",
            name="uq_message_field_codelist_referenz",
        ),
    )

    id = Column(Integer, primary_key=True)
    message_field_id = Column(Integer, ForeignKey("message_fields.id"), nullable=False)
    # NULL = Referenz im Dokument vorhanden, Codeliste (noch) nicht importiert.
    codelist_id = Column(Integer, ForeignKey("code_lists.id"), nullable=True)
    referenz_id = Column(String, nullable=False)      # "G_0002"
    referenz_raw = Column(String)                     # "G_0002 Codeliste Gas Nr. G_0002"
    quelle_seite = Column(Integer)

    message_field = relationship("MessageField", back_populates="codelist_referenzen")
    codelist = relationship("CodeList")


class CodeList(Base):
    """Eine Codeliste in einer regulatorischen Fassung (z.B. "ZC", "E01")."""
    __tablename__ = "code_lists"

    id = Column(Integer, primary_key=True)
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"), nullable=False)
    name = Column(String, nullable=False)
    nachrichtentyp = Column(String)
    beschreibung = Column(Text)
    # Provenienz, analog zu MessageDefinition (Issue #48). Erst mit der ersten
    # echten Codelisten-Extraktion noetig geworden -- vorher war die Tabelle leer.
    # quelle_hash ist zugleich der Schluessel fuer den idempotenten Re-Import.
    quelle_dokument = Column(String)
    quelle_hash = Column(String)
    # Kapitelnummer des Quelldokuments ("4.5"). Macht nachvollziehbar, aus
    # welchem Abschnitt die Liste stammt, ohne den Namen parsen zu muessen.
    quelle_kapitel = Column(String)

    regulatory_version = relationship("RegulatoryVersion")
    entries = relationship("CodeListEntry", back_populates="codelist")


class CodeListEntry(Base):
    """Ein einzelner Code. gueltig_bis = NULL bedeutet 'noch gueltig' -- damit
    laesst sich zu jedem Stichtag bestimmen, welche Codes zulaessig waren, ohne
    Zeilen zu loeschen."""
    __tablename__ = "code_list_entries"

    id = Column(Integer, primary_key=True)
    codelist_id = Column(Integer, ForeignKey("code_lists.id"), nullable=False)
    code = Column(String, nullable=False)             # z.B. "ZC9" oder "7-b:3.0.0"
    bedeutung = Column(String)
    gueltig_ab = Column(Date)
    gueltig_bis = Column(Date, nullable=True)
    # --- Ab hier: strukturierte Zusatzattribute der OBIS-Codelisten (Issue #48).
    # Die Codeliste der OBIS-Kennzahlen fuehrt je Code mehrere eigenstaendige
    # Merkmale in eigenen Tabellenspalten. Sie werden bewusst NICHT zu einem
    # String in `bedeutung` verkettet -- das wuerde strukturierte Information in
    # eine Zeichenkette aufloesen, die spaeter niemand mehr sauber trennen kann.
    # Jedes Feld traegt den unveraenderten Zellwert der jeweiligen Quellspalte.
    werteart = Column(String)      # "Zählerstand", "Profilwert (stündlich)"
    status = Column(String)        # "Vorläufig"/"Endgültig", "ungestört"/"gestört"
    richtung = Column(String)      # "Ausspeisung"/"Einspeisung", "Bezug (+)"
    hinweise = Column(Text)        # Inhalt der Spalte "Hinweise"
    # Prüfidentifikatoren als ROHWERT der Quellspalte, bewusst ohne FK auf
    # ProcessIdentifier: die hier referenzierten PIs sind MSCONS-PIs (13xxx),
    # der Bestand kennt bisher nur UTILMD (44xxx). Eine FK liefe zu 100% ins
    # Leere. Sobald die MSCONS-PIs importiert sind, laesst sich daraus eine
    # echte Beziehung ableiten, ohne den Parser anzufassen.
    pruefidentifikatoren = Column(String)
    quelle_seite = Column(Integer)

    codelist = relationship("CodeList", back_populates="entries")


class Testkonstellation(Base):
    """Ein Testfall, abgeleitet aus Profil (Sparte/Segment/Marktrolle) und
    Prozess. ist_negativfall trennt die Faelle, in denen ein Ablehnen das
    RICHTIGE Ergebnis ist -- sonst wuerde ein bestandener Negativtest wie ein
    Fehler aussehen."""
    __tablename__ = "testkonstellationen"

    id = Column(Integer, primary_key=True)
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"), nullable=False)
    titel = Column(String, nullable=False)
    sparte = Column(String)
    segment = Column(String)
    marktrolle = Column(String)
    prozess_pi_id = Column(Integer, ForeignKey("process_identifiers.id"), nullable=True)
    ist_negativfall = Column(Boolean, default=False)
    beschreibung = Column(Text)
    erwartetes_ergebnis = Column(Text)

    regulatory_version = relationship("RegulatoryVersion")
    prozess_pi = relationship("ProcessIdentifier")
    schritte = relationship(
        "TestkonstellationSchritt",
        back_populates="konstellation",
        order_by="TestkonstellationSchritt.reihenfolge",
    )


class TestkonstellationSchritt(Base):
    """Ein Nachrichtenaustausch innerhalb eines Testfalls. reihenfolge haelt den
    Ablauf fest, sender_rolle/empfaenger_rolle die Richtung."""
    __tablename__ = "testkonstellation_schritte"

    id = Column(Integer, primary_key=True)
    konstellation_id = Column(Integer, ForeignKey("testkonstellationen.id"), nullable=False)
    reihenfolge = Column(Integer, default=0)
    nachrichtentyp = Column(String)
    sender_rolle = Column(String)
    empfaenger_rolle = Column(String)
    pi_nummer = Column(String, nullable=True)
    beschreibung = Column(Text)
    edifact_beispiel = Column(Text, nullable=True)

    konstellation = relationship("Testkonstellation", back_populates="schritte")
