import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from . import models, schemas, matching, sap_cloud_alm
from .auth import require_auth, get_current_tenant_id

router = APIRouter(prefix="/api/assessments", tags=["import"], dependencies=[Depends(require_auth)])


def _get_assessment(db: Session, assessment_id: int, tenant_id: int) -> models.Assessment:
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id, models.Assessment.tenant_id == tenant_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment nicht gefunden")
    return assessment


def _build_suggestions(rows: list[tuple[str, str]], db: Session, assessment: models.Assessment) -> list[schemas.ImportSuggestion]:
    requirements = matching.get_requirements(db, assessment.regulatory_version_id)
    suggestions = []
    for i, (title, status_text) in enumerate(rows):
        candidate = matching.match_row(title, requirements)
        impl, test, result = matching.status_from_text(status_text)
        suggestions.append(schemas.ImportSuggestion(
            row_index=i,
            raw_title=title,
            raw_status=status_text,
            requirement_id=candidate.requirement_id if candidate else None,
            requirement_code=candidate.requirement_code if candidate else None,
            requirement_title=candidate.requirement_title if candidate else None,
            confidence=candidate.confidence if candidate else 0.0,
            implementation_status=impl,
            test_status=test,
            result_status=result,
        ))
    return suggestions


@router.post("/{assessment_id}/import/csv", response_model=schemas.ImportPreviewOut)
async def import_csv_preview(
    assessment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    assessment = _get_assessment(db, assessment_id, tenant_id)
    raw = (await file.read()).decode("utf-8-sig", errors="ignore")

    # Erkennt Semikolon oder Komma als Trenner (deutsche Excel-Exporte nutzen oft ";")
    delimiter = ";" if raw.count(";") > raw.count(",") else ","
    reader = csv.reader(io.StringIO(raw), delimiter=delimiter)
    all_rows = list(reader)
    if not all_rows:
        raise HTTPException(status_code=400, detail="Datei ist leer")

    header = [h.strip().lower() for h in all_rows[0]]
    title_idx = next((i for i, h in enumerate(header) if h in ("titel", "title", "testfall", "name")), 0)
    status_idx = next((i for i, h in enumerate(header) if h in ("status", "ergebnis", "result")), None)

    rows = []
    for row in all_rows[1:]:
        if not row or not any(c.strip() for c in row):
            continue
        title = row[title_idx] if title_idx < len(row) else ""
        status_text = row[status_idx] if status_idx is not None and status_idx < len(row) else ""
        rows.append((title, status_text))

    suggestions = _build_suggestions(rows, db, assessment)
    return schemas.ImportPreviewOut(source_name=f"CSV-Import ({file.filename})", suggestions=suggestions)


@router.post("/{assessment_id}/import/sap-cloud-alm", response_model=schemas.ImportPreviewOut)
async def import_sap_cloud_alm_preview(
    assessment_id: int,
    payload: schemas.SapCloudAlmImportRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    assessment = _get_assessment(db, assessment_id, tenant_id)
    try:
        token = await sap_cloud_alm.get_access_token(payload.token_url, payload.client_id, payload.client_secret)
        items = await sap_cloud_alm.fetch_test_cases(payload.base_url, payload.api_path, token)
    except sap_cloud_alm.SapCloudAlmError as e:
        raise HTTPException(status_code=502, detail=str(e))

    rows = [(item["title"], item["status"]) for item in items]
    suggestions = _build_suggestions(rows, db, assessment)
    return schemas.ImportPreviewOut(source_name="SAP Cloud ALM", suggestions=suggestions)


@router.post("/{assessment_id}/import/confirm")
def import_confirm(
    assessment_id: int,
    payload: schemas.ImportConfirmRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    assessment = _get_assessment(db, assessment_id, tenant_id)
    now = datetime.utcnow()
    updated = 0

    ar_by_req_id = {
        ar.requirement_id: ar
        for ar in db.query(models.AssessmentRequirement).filter(
            models.AssessmentRequirement.assessment_id == assessment.id
        ).all()
    }

    for item in payload.items:
        ar = ar_by_req_id.get(item.requirement_id)
        if not ar:
            continue
        ar.implementation_status = item.implementation_status
        ar.test_status = item.test_status
        ar.result_status = item.result_status
        ar.evidence_status = "vorhanden" if item.result_status == "erfolgreich" else ar.evidence_status
        ar.data_source = "import"
        ar.import_source_name = payload.source_name
        ar.last_synced_at = now
        updated += 1

    db.commit()
    return {"updated": updated}
