from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProcessIdentifierOut(BaseModel):
    id: int
    pi_number: str
    name: str
    sender_role: Optional[str]
    receiver_role: Optional[str]
    message_type: str
    criticality: str

    class Config:
        from_attributes = True


class ProcessGroupOut(BaseModel):
    id: int
    code: str
    name: str
    sequence: int
    pis: List[ProcessIdentifierOut] = []

    class Config:
        from_attributes = True


class RequirementOut(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str]
    pi_id: Optional[int]
    transaction_reason: Optional[str]
    response_code: Optional[str]
    criticality: str
    weight: float
    applies_to_slp: bool
    applies_to_rlm: bool

    class Config:
        from_attributes = True


class AssessmentRequirementUpdate(BaseModel):
    implementation_status: Optional[str] = None
    test_status: Optional[str] = None
    result_status: Optional[str] = None
    evidence_status: Optional[str] = None
    comment: Optional[str] = None
    responsible_person: Optional[str] = None


class AssessmentRequirementOut(BaseModel):
    id: int
    requirement_id: int
    relevance_status: str
    implementation_status: str
    test_status: str
    result_status: str
    evidence_status: str
    comment: Optional[str]
    responsible_person: Optional[str]
    requirement: RequirementOut

    class Config:
        from_attributes = True


class ScoreResultOut(BaseModel):
    regulatory_coverage: float
    quality_grade: float
    implementation_quality: float
    test_quality: float
    evidence_quality: float
    actuality: float

    class Config:
        from_attributes = True


class FindingOut(BaseModel):
    id: int
    severity: str
    title: str
    description: Optional[str]
    recommendation: Optional[str]

    class Config:
        from_attributes = True


class AssessmentCreate(BaseModel):
    customer_name: str
    market_role: str  # "lieferant" | "grund_ersatzversorger" | "beides"
    customer_segments: str  # CSV, z.B. "slp" | "rlm" | "slp,rlm"
    business_scenario: str = "lieferantenwechsel"  # im MVP fest
    # Gegen welchen regulatorischen Stand gemessen wird -- vorher implizit immer die
    # aktive Version, jetzt explizite Auswahl im Wizard (Abschnitt 12.4).
    regulatory_version_id: int


class AssessmentForCustomerCreate(BaseModel):
    """Weiteres Assessment fuer einen BESTEHENDEN Kunden (Abschnitt 12.3) -- Marktrolle
    und Segmente werden vom Kunden bzw. seinem letzten Assessment uebernommen, es wird
    nur noch die Version abgefragt."""
    regulatory_version_id: int


class AssessmentOut(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    market_role: Optional[str] = None
    business_scenario: str
    customer_segments: str
    status: str
    created_at: datetime
    regulatory_version_id: Optional[int] = None
    regulatory_version_name: Optional[str] = None
    # Live aus dem Stichtag der Version abgeleitet, NICHT gespeichert (Abschnitt 12.5)
    assessment_type: Optional[str] = None  # readiness | compliance | historisch

    class Config:
        from_attributes = True


class AssessmentHistoryItem(BaseModel):
    """Ein Eintrag der Assessment-Historie eines Kunden (Abschnitt 12.3)."""
    id: int
    regulatory_version_id: Optional[int]
    regulatory_version_name: Optional[str]
    assessment_type: str  # readiness | compliance | historisch
    status: str
    created_at: datetime
    regulatory_coverage: Optional[float] = None
    quality_grade: Optional[float] = None


class AssessmentDetailOut(BaseModel):
    assessment: AssessmentOut
    requirement_statuses: List[AssessmentRequirementOut]
    score: Optional[ScoreResultOut]
    findings: List[FindingOut]
    process_groups: List[ProcessGroupOut]


class ImportSuggestion(BaseModel):
    row_index: int
    raw_title: str
    raw_status: str
    requirement_id: Optional[int]
    requirement_code: Optional[str]
    requirement_title: Optional[str]
    confidence: float
    implementation_status: str
    test_status: str
    result_status: str


class ImportPreviewOut(BaseModel):
    source_name: str
    suggestions: List[ImportSuggestion]


class ImportConfirmItem(BaseModel):
    requirement_id: int
    implementation_status: str
    test_status: str
    result_status: str


class ImportConfirmRequest(BaseModel):
    source_name: str
    items: List[ImportConfirmItem]


class RegulatoryVersionOut(BaseModel):
    id: int
    name: str
    sector: str
    status: str
    source_reference: Optional[str]
    is_active: bool
    valid_from: Optional[datetime]
    predecessor_version_id: Optional[int]
    summary: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RegulatoryVersionUpdate(BaseModel):
    """Nachpflegen der Versions-Metadaten -- im MVP vor allem die kuratierte
    Zusammenfassung fuer die Kunden-Vorschau."""
    name: Optional[str] = None
    status: Optional[str] = None  # konsultation | final | verbindlich
    valid_from: Optional[datetime] = None
    source_reference: Optional[str] = None
    summary: Optional[str] = None


class RegulatoryVersionCreate(BaseModel):
    name: str
    sector: str = "gas"
    status: str = "konsultation"  # konsultation | final
    source_reference: Optional[str] = None
    valid_from: Optional[datetime] = None
    predecessor_version_id: Optional[int] = None


class RegulatoryChangeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str  # neuer_prozess | neues_pflichtfeld | neuer_code | neue_qualitaetsregel | neuer_testfall
    process_group_id: Optional[int] = None
    pi_id: Optional[int] = None
    risk: str = "mittel"    # hoch | mittel | niedrig
    effort: str = "mittel"  # hoch | mittel | niedrig
    effort_person_days: Optional[int] = None
    recommendation: Optional[str] = None
    message_type: Optional[str] = None  # leer -> wird aus dem verknuepften PI abgeleitet
    source_url: Optional[str] = None
    regulatory_version_id: int


class RegulatoryChangeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    process_group_id: Optional[int] = None
    pi_id: Optional[int] = None
    risk: Optional[str] = None
    effort: Optional[str] = None
    effort_person_days: Optional[int] = None
    recommendation: Optional[str] = None
    message_type: Optional[str] = None
    source_url: Optional[str] = None
    status: Optional[str] = None  # zu_pruefen | entwurf | veroeffentlicht


class RegulatoryChangeOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    process_group_id: Optional[int]
    process_group_name: Optional[str] = None
    pi_id: Optional[int]
    pi_number: Optional[str] = None
    risk: str
    effort: str
    effort_person_days: Optional[int] = None
    recommendation: Optional[str] = None
    message_type: Optional[str] = None          # eigener Wert (leer = aus PI abgeleitet)
    effective_message_type: Optional[str] = None  # tatsaechlich geltender Wert
    source_url: Optional[str]
    status: str
    origin: str
    regulatory_version_id: int
    created_at: datetime


class RequirementDiffOut(BaseModel):
    change_type: str  # neu | geaendert | entfallen
    requirement_code: str
    title: str
    pi_number: Optional[str]
    changed_fields: List[str] = []
    old_title: Optional[str] = None


class RegulatoryDiffSummary(BaseModel):
    old_version_id: int
    new_version_id: int
    added_count: int
    changed_count: int
    removed_count: int
    entries: List[RequirementDiffOut]


class RegulatoryImpactRequirementRef(BaseModel):
    requirement_code: str
    title: str
    pi_number: Optional[str] = None


class RegulatoryImpactChange(BaseModel):
    """Eine kundensichtbare (= veroeffentlichte) Aenderung inkl. Handlungsempfehlung
    und Herkunft, damit der Kunde einschaetzen kann, worauf er sich verlaesst."""
    id: int
    title: str
    description: Optional[str]
    category: str
    risk: str
    effort: str
    effort_person_days: Optional[int]
    recommendation: Optional[str]
    message_type: Optional[str]
    source_url: Optional[str]
    process_group_name: Optional[str]
    pi_number: Optional[str]
    origin: str  # manuell | ki_vorschlag
    # Kundensichtbar sind ausschliesslich veroeffentlichte Eintraege -- die haben die
    # Kuration durchlaufen und gelten damit als redaktionell geprueft.
    is_reviewed: bool


class RegulatoryImpactOut(BaseModel):
    has_upcoming_version: bool
    # Kontext zur Version des Assessments SELBST -- noetig, um bei fehlender
    # Folgeversion zwei Faelle zu unterscheiden: "es ist nichts Neues bekannt" vs.
    # "ihr messt bereits gegen den neuesten bekannten Stand".
    current_version_name: Optional[str] = None
    current_version_valid_from: Optional[datetime] = None
    is_latest_known_version: bool = False
    known_version_count: int = 0
    upcoming_version_id: Optional[int] = None
    upcoming_version_name: Optional[str] = None
    upcoming_version_valid_from: Optional[datetime] = None
    upcoming_version_status: Optional[str] = None  # konsultation | final | verbindlich
    # Kuratierte Kurzfassung (manuell gepflegt, keine Live-Generierung)
    upcoming_version_summary: Optional[str] = None
    # Juengster Aenderungszeitpunkt aus Version + zugehoerigen veroeffentlichten Changes
    upcoming_version_last_updated: Optional[datetime] = None

    current_coverage: Optional[float] = None
    projected_coverage: Optional[float] = None

    remain_valid_count: int = 0
    remain_valid: List[RegulatoryImpactRequirementRef] = []
    newly_required: List[RegulatoryImpactRequirementRef] = []
    dropped: List[RegulatoryImpactRequirementRef] = []

    published_change_count: int = 0
    risk_hoch_count: int = 0
    risk_mittel_count: int = 0
    risk_niedrig_count: int = 0
    # Hoechstes vorkommendes Einzelrisiko bestimmt das Gesamtrisiko -- eine einzige
    # "hoch"-Aenderung macht die gesamte Umstellung zum Hochrisiko-Vorhaben.
    overall_risk: Optional[str] = None  # hoch | mittel | niedrig
    total_person_days: Optional[int] = None  # Summe, sofern ueberhaupt gepflegt
    affected_process_groups: List[str] = []
    affected_message_types: List[str] = []
    new_test_case_count: int = 0
    changes: List[RegulatoryImpactChange] = []


class SapCloudAlmImportRequest(BaseModel):
    token_url: str
    client_id: str
    client_secret: str
    base_url: str
    api_path: str = "/api/test-management/v1/test-cases"


# --- Admin-Bereich (Issue #13) ---------------------------------------------

class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    email_domain: Optional[str] = None
    sso_provider: Optional[str] = None
    sso_tenant_id: Optional[str] = None
    is_active: bool = True
    user_count: int = 0
    customer_count: int = 0
    created_at: Optional[datetime] = None


class TenantCreate(BaseModel):
    name: str
    slug: str
    email_domain: Optional[str] = None
    sso_provider: Optional[str] = None
    sso_tenant_id: Optional[str] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    email_domain: Optional[str] = None
    sso_provider: Optional[str] = None
    sso_tenant_id: Optional[str] = None
    is_active: Optional[bool] = None


class AdminUserOut(BaseModel):
    id: int
    email: str
    tenant_id: int
    tenant_name: Optional[str] = None
    is_active: bool
    is_atlas_admin: bool
    is_sso_user: bool
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class AdminUserCreate(BaseModel):
    email: str
    password: str
    tenant_id: int
    is_atlas_admin: bool = False


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_atlas_admin: Optional[bool] = None


class AdminAssessmentRow(BaseModel):
    id: int
    tenant_id: Optional[int]
    tenant_name: Optional[str]
    customer_name: Optional[str]
    regulatory_version_name: Optional[str]
    assessment_type: str
    status: str
    regulatory_coverage: Optional[float] = None
    quality_grade: Optional[float] = None
    created_at: datetime


class SystemHealthOut(BaseModel):
    api_ok: bool
    database_ok: bool
    database_error: Optional[str] = None
    tenant_count: int
    user_count: int
    assessment_count: int
    customer_count: int
    regulatory_version_count: int
