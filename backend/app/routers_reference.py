from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from . import models, schemas
from .auth import require_auth

router = APIRouter(prefix="/api", tags=["reference"], dependencies=[Depends(require_auth)])


@router.get("/regulatory-versions", response_model=list[schemas.RegulatoryVersionOut])
def list_regulatory_versions(db: Session = Depends(get_db)):
    return db.query(models.RegulatoryVersion).order_by(models.RegulatoryVersion.id).all()


@router.get("/process-groups", response_model=list[schemas.ProcessGroupOut])
def list_process_groups(db: Session = Depends(get_db)):
    return (
        db.query(models.ProcessGroup)
        .options(joinedload(models.ProcessGroup.pis))
        .order_by(models.ProcessGroup.sequence)
        .all()
    )


@router.get("/requirements", response_model=list[schemas.RequirementOut])
def list_requirements(db: Session = Depends(get_db)):
    return db.query(models.Requirement).all()
