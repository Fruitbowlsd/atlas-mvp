from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from . import models, schemas, services
from .auth import require_auth

router = APIRouter(prefix="/api/assessments", tags=["assessments"], dependencies=[Depends(require_auth)])


def _get_assessment_or_404(db: Session, assessment_id: int) -> models.Assessment:
    assessment = (
        db.query(models.Assessment)
        .options(
            joinedload(models.Assessment.customer),
            joinedload(models.Assessment.requirement_statuses).joinedload(models.AssessmentRequirement.requirement),
            joinedload(models.Assessment.score_result),
            joinedload(models.Assessment.findings),
        )
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment nicht gefunden")
    return assessment


def _to_assessment_out(assessment: models.Assessment) -> schemas.AssessmentOut:
    return schemas.AssessmentOut(
        id=assessment.id,
        customer_id=assessment.customer_id,
        customer_name=assessment.customer.name if assessment.customer else None,
        market_role=assessment.customer.market_role if assessment.customer else None,
        business_scenario=assessment.business_scenario,
        customer_segments=assessment.customer_segments,
        status=assessment.status,
        created_at=assessment.created_at,
    )


@router.post("", response_model=schemas.AssessmentOut)
def create_assessment(payload: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    valid_roles = {"lieferant", "grund_ersatzversorger", "beides"}
    if payload.market_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"market_role muss einer von {valid_roles} sein")

    segments = {s.strip() for s in payload.customer_segments.split(",") if s.strip()}
    if not segments or not segments.issubset({"slp", "rlm"}):
        raise HTTPException(status_code=400, detail="customer_segments muss 'slp', 'rlm' oder 'slp,rlm' sein")

    # Im MVP gibt es nur den regulatorischen Stand + Requirement-Katalog fuer Gas /
    # Lieferbeginn -> jede neue Bewertung nutzt denselben Referenzkatalog.
    reg_version = db.query(models.RegulatoryVersion).first()
    if not reg_version:
        raise HTTPException(status_code=500, detail="Referenzdaten nicht geseedet")

    customer = models.Customer(name=payload.customer_name, market_role=payload.market_role, sector="gas")
    db.add(customer)
    db.flush()

    assessment = models.Assessment(
        customer_id=customer.id,
        regulatory_version_id=reg_version.id,
        business_scenario="lieferantenwechsel",  # im MVP fest
        customer_segments=payload.customer_segments,
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

    db.commit()
    db.refresh(assessment)
    assessment.customer = customer
    return _to_assessment_out(assessment)


@router.get("")
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(models.Assessment).options(joinedload(models.Assessment.customer)).all()
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
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    groups = (
        db.query(models.ProcessGroup)
        .options(joinedload(models.ProcessGroup.pis))
        .order_by(models.ProcessGroup.sequence)
        .all()
    )
    return schemas.AssessmentDetailOut(
        assessment=_to_assessment_out(assessment),
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
):
    ar = db.query(models.AssessmentRequirement).filter(
        models.AssessmentRequirement.id == assessment_requirement_id
    ).first()
    if not ar:
        raise HTTPException(status_code=404, detail="Requirement-Status nicht gefunden")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ar, field, value)

    db.commit()
    db.refresh(ar)
    return ar


@router.post("/{assessment_id}/calculate")
def calculate(assessment_id: int, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
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
def results(assessment_id: int, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    if not assessment.score_result:
        raise HTTPException(status_code=400, detail="Bewertung wurde noch nicht berechnet")
    heatmap = services.process_group_heatmap(db, assessment)
    return {
        "score": schemas.ScoreResultOut.model_validate(assessment.score_result),
        "findings": [schemas.FindingOut.model_validate(f) for f in assessment.findings],
        "heatmap": heatmap,
    }
