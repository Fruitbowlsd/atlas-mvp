from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from . import models, schemas
from .auth import require_auth

router = APIRouter(prefix="/api", tags=["reference"], dependencies=[Depends(require_auth)])


# Bewusst NICHT hinter require_internal: der Kunden-Wizard braucht diese Liste, um
# den Stand auszuwaehlen, gegen den gemessen wird. RegulatoryVersion ist laut
# Abschnitt 13.1 geteiltes Plattform-Wissen, kein Kundengeheimnis -- intern ist nur
# das KURATIEREN (anlegen/aendern), nicht das Lesen.
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
