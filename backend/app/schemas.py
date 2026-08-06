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


class AssessmentOut(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    market_role: Optional[str] = None
    business_scenario: str
    customer_segments: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


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


class SapCloudAlmImportRequest(BaseModel):
    token_url: str
    client_id: str
    client_secret: str
    base_url: str
    api_path: str = "/api/test-management/v1/test-cases"
