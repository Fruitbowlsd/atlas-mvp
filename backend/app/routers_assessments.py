from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from . import models, schemas, services
from .auth import require_auth, get_current_tenant_id

router = APIRouter(prefix="/api/assessments", tags=["assessments"], dependencies=[Depends(require_auth)])
# Kundenbezogene Endpunkte -- ein Kunde kann mehrere Assessments haben (Abschnitt 12.3)
customer_router = APIRouter(prefix="/api/customers", tags=["customers"], dependencies=[Depends(require_auth)])


def _get_assessment_or_404(db: Session, assessment_id: int, tenant_id: int) -> models.Assessment:
    """tenant_id ist bewusst ein Pflichtparameter -- so faellt beim Hinzufuegen eines
    neuen Endpunkts sofort auf, dass der Tenant mitgegeben werden muss."""
    assessment = (
        db.query(models.Assessment)
        .options(
            joinedload(models.Assessment.customer),
            joinedload(models.Assessment.requirement_statuses).joinedload(models.AssessmentRequirement.requirement),
            joinedload(models.Assessment.score_result),
            joinedload(models.Assessment.findings),
        )
        .filter(
            models.Assessment.id == assessment_id,
            models.Assessment.tenant_id == tenant_id,
        )
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment nicht gefunden")
    return assessment


def _get_customer_or_404(db: Session, customer_id: int, tenant_id: int) -> models.Customer:
    """Kunden nur innerhalb des eigenen Tenants auffindbar -- ein fremder Kunde
    liefert bewusst 404 (nicht 403), damit die Existenz nicht verraten wird."""
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.id == customer_id, models.Customer.tenant_id == tenant_id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return customer


def _to_assessment_out(assessment: models.Assessment, db: Session) -> schemas.AssessmentOut:
    version = assessment.regulatory_version
    assessment_type = None
    if version is not None:
        all_versions = db.query(models.RegulatoryVersion).all()
        assessment_type = services.derive_assessment_type(version, all_versions)

    return schemas.AssessmentOut(
        id=assessment.id,
        customer_id=assessment.customer_id,
        customer_name=assessment.customer.name if assessment.customer else None,
        market_role=assessment.customer.market_role if assessment.customer else None,
        business_scenario=assessment.business_scenario,
        customer_segments=assessment.customer_segments,
        status=assessment.status,
        created_at=assessment.created_at,
        regulatory_version_id=assessment.regulatory_version_id,
        regulatory_version_name=version.name if version else None,
        assessment_type=assessment_type,
    )


def _create_assessment_for(
    db: Session,
    customer: models.Customer,
    reg_version: models.RegulatoryVersion,
    segments_csv: str,
    segments: set[str],
) -> models.Assessment:
    """Legt ein Assessment samt seiner AssessmentRequirement-Zeilen an. Gemeinsam
    genutzt vom Wizard (neuer Kunde) und vom Anlegen eines weiteren Assessments
    fuer einen bestehenden Kunden (Abschnitt 12.3)."""
    assessment = models.Assessment(
        customer_id=customer.id,
        tenant_id=customer.tenant_id,  # nie unabhaengig setzen -- immer vom Kunden
        regulatory_version_id=reg_version.id,
        business_scenario="lieferantenwechsel",  # im MVP fest
        customer_segments=segments_csv,
        status="in_bearbeitung",
    )
    db.add(assessment)
    db.flush()

    requirements = db.query(models.Requirement).filter(
        models.Requirement.regulatory_version_id == reg_version.id
    ).all()
    for req in requirements:
        applies = (("slp" in segments and req.applies_to_slp) or ("rlm" in segments and req.applies_to_rlm))
        if not applies:
            continue
        db.add(models.AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req.id,
            relevance_status="relevant",
        ))
    return assessment


@router.post("", response_model=schemas.AssessmentOut)
def create_assessment(
    payload: schemas.AssessmentCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    valid_roles = {"lieferant", "grund_ersatzversorger", "beides"}
    if payload.market_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"market_role muss einer von {valid_roles} sein")

    segments = {s.strip() for s in payload.customer_segments.split(",") if s.strip()}
    if not segments or not segments.issubset({"slp", "rlm"}):
        raise HTTPException(status_code=400, detail="customer_segments muss 'slp', 'rlm' oder 'slp,rlm' sein")

    # Gegen welchen regulatorischen Stand gemessen wird, waehlt der Nutzer jetzt
    # explizit im Wizard (Abschnitt 12.4) -- vorher war das implizit immer die
    # aktive Version, was mit mehreren parallelen Versionen nicht mehr reicht.
    reg_version = db.query(models.RegulatoryVersion).filter(
        models.RegulatoryVersion.id == payload.regulatory_version_id
    ).first()
    if not reg_version:
        raise HTTPException(status_code=404, detail="RegulatoryVersion nicht gefunden")

    customer = models.Customer(
        name=payload.customer_name,
        market_role=payload.market_role,
        sector="gas",
        tenant_id=tenant_id,
    )
    db.add(customer)
    db.flush()

    assessment = _create_assessment_for(db, customer, reg_version, payload.customer_segments, segments)

    db.commit()
    db.refresh(assessment)
    assessment.customer = customer
    return _to_assessment_out(assessment, db)


@customer_router.get("/{customer_id}/assessments", response_model=list[schemas.AssessmentHistoryItem])
def list_customer_assessments(
    customer_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Assessment-Historie eines Kunden (Abschnitt 12.3). Der Typ je Eintrag wird
    live abgeleitet, damit er sich mit dem Zeitablauf mitbewegt."""
    _get_customer_or_404(db, customer_id, tenant_id)

    assessments = (
        db.query(models.Assessment)
        .options(joinedload(models.Assessment.regulatory_version), joinedload(models.Assessment.score_result))
        .filter(
            models.Assessment.customer_id == customer_id,
            models.Assessment.tenant_id == tenant_id,
        )
        .order_by(models.Assessment.created_at.desc())
        .all()
    )
    all_versions = db.query(models.RegulatoryVersion).all()

    return [
        schemas.AssessmentHistoryItem(
            id=a.id,
            regulatory_version_id=a.regulatory_version_id,
            regulatory_version_name=a.regulatory_version.name if a.regulatory_version else None,
            assessment_type=(
                services.derive_assessment_type(a.regulatory_version, all_versions)
                if a.regulatory_version else "historisch"
            ),
            status=a.status,
            created_at=a.created_at,
            regulatory_coverage=a.score_result.regulatory_coverage if a.score_result else None,
            quality_grade=a.score_result.quality_grade if a.score_result else None,
        )
        for a in assessments
    ]


@customer_router.post("/{customer_id}/assessments", response_model=schemas.AssessmentOut)
def create_assessment_for_customer(
    customer_id: int,
    payload: schemas.AssessmentForCustomerCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Weiteres Assessment fuer einen bestehenden Kunden (Abschnitt 12.3) -- fragt nur
    die Version ab, Marktrolle und Segmente kommen vom letzten Assessment des Kunden."""
    customer = _get_customer_or_404(db, customer_id, tenant_id)

    reg_version = db.query(models.RegulatoryVersion).filter(
        models.RegulatoryVersion.id == payload.regulatory_version_id
    ).first()
    if not reg_version:
        raise HTTPException(status_code=404, detail="RegulatoryVersion nicht gefunden")

    # Segmente vom juengsten Assessment uebernehmen -- der Nutzer soll die Kundendaten
    # nicht erneut angeben muessen. Mehrere Assessments gegen dieselbe Version sind
    # bewusst erlaubt (z.B. erneute Bewertung zu einem spaeteren Zeitpunkt).
    latest = (
        db.query(models.Assessment)
        .filter(
            models.Assessment.customer_id == customer_id,
            models.Assessment.tenant_id == tenant_id,
        )
        .order_by(models.Assessment.created_at.desc())
        .first()
    )
    segments_csv = latest.customer_segments if latest else "slp,rlm"
    segments = {s.strip() for s in segments_csv.split(",") if s.strip()}

    assessment = _create_assessment_for(db, customer, reg_version, segments_csv, segments)
    db.commit()
    db.refresh(assessment)
    assessment.customer = customer
    return _to_assessment_out(assessment, db)


@router.get("")
def list_assessments(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    assessments = (
        db.query(models.Assessment)
        .options(joinedload(models.Assessment.customer))
        .filter(models.Assessment.tenant_id == tenant_id)
        .all()
    )
    return [
        {
            "id": a.id,
            "customer_name": a.customer.name if a.customer else None,
            "business_scenario": a.business_scenario,
            "customer_segments": a.customer_segments,
            "status": a.status,
        }
        for a in assessments
    ]


@router.get("/{assessment_id}", response_model=schemas.AssessmentDetailOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_current_tenant_id)):
    assessment = _get_assessment_or_404(db, assessment_id, tenant_id)
    groups = (
        db.query(models.ProcessGroup)
        .options(joinedload(models.ProcessGroup.pis))
        .order_by(models.ProcessGroup.sequence)
        .all()
    )
    return schemas.AssessmentDetailOut(
        assessment=_to_assessment_out(assessment, db),
        requirement_statuses=assessment.requirement_statuses,
        score=assessment.score_result,
        findings=assessment.findings,
        process_groups=groups,
    )


@router.put("/requirement-status/{assessment_requirement_id}", response_model=schemas.AssessmentRequirementOut)
def update_requirement_status(
    assessment_requirement_id: int,
    payload: schemas.AssessmentRequirementUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    # AssessmentRequirement traegt bewusst KEINE eigene tenant_id (waere
    # Denormalisierung mit Drift-Risiko). Der Bezug kommt ueber den Join auf das
    # Assessment -- ohne den waere hier der Status eines fremden Tenants aenderbar,
    # weil der Endpunkt nur eine AR-ID entgegennimmt.
    ar = (
        db.query(models.AssessmentRequirement)
        .join(models.Assessment, models.AssessmentRequirement.assessment_id == models.Assessment.id)
        .filter(
            models.AssessmentRequirement.id == assessment_requirement_id,
            models.Assessment.tenant_id == tenant_id,
        )
        .first()
    )
    if not ar:
        raise HTTPException(status_code=404, detail="Requirement-Status nicht gefunden")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ar, field, value)

    db.commit()
    db.refresh(ar)
    return ar


@router.post("/{assessment_id}/calculate")
def calculate(assessment_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_current_tenant_id)):
    assessment = _get_assessment_or_404(db, assessment_id, tenant_id)
    score = services.calculate_score(db, assessment)
    findings = services.generate_findings(db, assessment)
    heatmap = services.process_group_heatmap(db, assessment)
    db.commit()
    return {
        "score": schemas.ScoreResultOut.model_validate(score),
        "findings": [schemas.FindingOut.model_validate(f) for f in findings],
        "heatmap": heatmap,
    }


@router.get("/{assessment_id}/results")
def results(assessment_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_current_tenant_id)):
    assessment = _get_assessment_or_404(db, assessment_id, tenant_id)
    if not assessment.score_result:
        raise HTTPException(status_code=400, detail="Bewertung wurde noch nicht berechnet")
    heatmap = services.process_group_heatmap(db, assessment)
    return {
        "score": schemas.ScoreResultOut.model_validate(assessment.score_result),
        "findings": [schemas.FindingOut.model_validate(f) for f in assessment.findings],
        "heatmap": heatmap,
    }
