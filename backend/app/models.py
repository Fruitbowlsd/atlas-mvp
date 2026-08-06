from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class RegulatoryVersion(Base):
    __tablename__ = "regulatory_versions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)          # z.B. "GeLi Gas 2.0 / UTILMD Gas G1.1"
    sector = Column(String, nullable=False)         # "gas"
    status = Column(String, default="konsultation")  # konsultation | final
    source_reference = Column(String)

    requirements = relationship("Requirement", back_populates="regulatory_version")


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

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
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


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    market_role = Column(String, default="lieferant")
    sector = Column(String, default="gas")

    assessments = relationship("Assessment", back_populates="customer")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    regulatory_version_id = Column(Integer, ForeignKey("regulatory_versions.id"))
    business_scenario = Column(String, default="lieferantenwechsel")
    customer_segments = Column(String, default="slp,rlm")   # einfache CSV-Liste im MVP
    status = Column(String, default="in_bearbeitung")
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="assessments")
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
