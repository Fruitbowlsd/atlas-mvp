"""Admin-Bereich fuer das Atlas-Team (Issue #13).

Bewusst OHNE Tenant-Filterung: hier wird tenant-uebergreifend verwaltet. Genau
deshalb haengt der gesamte Router an require_atlas_admin -- ein Tenant-Nutzer
bekommt hier unter keinen Umstaenden Daten zu sehen.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from . import auth, models, schemas, services
from .database import get_db
from .seed_runner import run_seed

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(auth.require_atlas_admin)])


# --- A) Organisationen ------------------------------------------------------

def _tenant_out(t: models.Tenant, user_count: int, customer_count: int) -> schemas.TenantOut:
    return schemas.TenantOut(
        id=t.id,
        name=t.name,
        slug=t.slug,
        email_domain=t.email_domain,
        sso_provider=t.sso_provider,
        sso_tenant_id=t.sso_tenant_id,
        is_active=bool(t.is_active),
        user_count=user_count,
        customer_count=customer_count,
        created_at=t.created_at,
    )


@router.get("/tenants", response_model=list[schemas.TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    tenants = db.query(models.Tenant).order_by(models.Tenant.id).all()
    # Zaehlungen gebuendelt statt pro Tenant einzeln -- sonst waeren es 2 Abfragen je Zeile.
    users = dict(
        db.query(models.User.tenant_id, func.count(models.User.id))
        .group_by(models.User.tenant_id).all()
    )
    customers = dict(
        db.query(models.Customer.tenant_id, func.count(models.Customer.id))
        .group_by(models.Customer.tenant_id).all()
    )
    return [_tenant_out(t, users.get(t.id, 0), customers.get(t.id, 0)) for t in tenants]


@router.post("/tenants", response_model=schemas.TenantOut)
def create_tenant(payload: schemas.TenantCreate, db: Session = Depends(get_db)):
    slug = payload.slug.strip().lower()
    if not slug:
        raise HTTPException(status_code=400, detail="Slug darf nicht leer sein")
    if db.query(models.Tenant).filter(models.Tenant.slug == slug).first():
        raise HTTPException(status_code=400, detail="Dieser Slug ist bereits vergeben")

    tenant = models.Tenant(
        name=payload.name.strip(),
        slug=slug,
        email_domain=(payload.email_domain or "").strip().lower() or None,
        sso_provider=payload.sso_provider or None,
        sso_tenant_id=payload.sso_tenant_id or None,
        is_active=True,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return _tenant_out(tenant, 0, 0)


@router.patch("/tenants/{tenant_id}", response_model=schemas.TenantOut)
def update_tenant(tenant_id: int, payload: schemas.TenantUpdate, db: Session = Depends(get_db)):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organisation nicht gefunden")

    data = payload.model_dump(exclude_unset=True)
    if "slug" in data:
        data["slug"] = (data["slug"] or "").strip().lower()
        clash = (
            db.query(models.Tenant)
            .filter(models.Tenant.slug == data["slug"], models.Tenant.id != tenant_id)
            .first()
        )
        if clash:
            raise HTTPException(status_code=400, detail="Dieser Slug ist bereits vergeben")
    if "email_domain" in data:
        data["email_domain"] = (data["email_domain"] or "").strip().lower() or None

    for field, value in data.items():
        setattr(tenant, field, value)
    db.commit()
    db.refresh(tenant)

    user_count = db.query(models.User).filter(models.User.tenant_id == tenant.id).count()
    customer_count = db.query(models.Customer).filter(models.Customer.tenant_id == tenant.id).count()
    return _tenant_out(tenant, user_count, customer_count)


# --- B) Nutzer --------------------------------------------------------------

def _user_out(u: models.User) -> schemas.AdminUserOut:
    return schemas.AdminUserOut(
        id=u.id,
        email=u.email,
        tenant_id=u.tenant_id,
        tenant_name=u.tenant.name if u.tenant else None,
        is_active=bool(u.is_active),
        is_atlas_admin=bool(u.is_atlas_admin),
        is_sso_user=u.password_hash is None,
        created_at=u.created_at,
        last_login_at=u.last_login_at,
    )


@router.get("/users", response_model=list[schemas.AdminUserOut])
def list_users(tenant_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.User).options(joinedload(models.User.tenant))
    if tenant_id is not None:
        query = query.filter(models.User.tenant_id == tenant_id)
    return [_user_out(u) for u in query.order_by(models.User.email).all()]


@router.post("/users", response_model=schemas.AdminUserOut)
def create_user(payload: schemas.AdminUserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Bitte eine gueltige E-Mail-Adresse angeben")
    if not payload.password:
        raise HTTPException(status_code=400, detail="Passwort darf nicht leer sein")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Diese E-Mail-Adresse ist bereits vergeben")
    if not db.query(models.Tenant).filter(models.Tenant.id == payload.tenant_id).first():
        raise HTTPException(status_code=404, detail="Organisation nicht gefunden")

    user = models.User(
        email=email,
        password_hash=auth.hash_password(payload.password),
        tenant_id=payload.tenant_id,
        is_active=True,
        is_atlas_admin=payload.is_atlas_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_out(user)


@router.patch("/users/{user_id}", response_model=schemas.AdminUserOut)
def update_user(
    user_id: int,
    payload: schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.require_atlas_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Nutzer nicht gefunden")

    data = payload.model_dump(exclude_unset=True)
    # Sich selbst auszusperren waere unumkehrbar, solange es keine zweite
    # Verwaltungsmoeglichkeit gibt -- deshalb hier blockiert.
    if user.id == current.id:
        if data.get("is_active") is False:
            raise HTTPException(status_code=400, detail="Das eigene Konto kann nicht deaktiviert werden")
        if data.get("is_atlas_admin") is False:
            raise HTTPException(status_code=400, detail="Die eigenen Admin-Rechte koennen nicht entzogen werden")

    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return _user_out(user)


# --- C) Assessments (read-only) --------------------------------------------

@router.get("/assessments", response_model=list[schemas.AdminAssessmentRow])
def list_all_assessments(tenant_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Assessment).options(
        joinedload(models.Assessment.customer),
        joinedload(models.Assessment.regulatory_version),
        joinedload(models.Assessment.score_result),
    )
    if tenant_id is not None:
        query = query.filter(models.Assessment.tenant_id == tenant_id)

    assessments = query.order_by(models.Assessment.created_at.desc()).all()
    all_versions = db.query(models.RegulatoryVersion).all()
    tenant_names = dict(db.query(models.Tenant.id, models.Tenant.name).all())

    return [
        schemas.AdminAssessmentRow(
            id=a.id,
            tenant_id=a.tenant_id,
            tenant_name=tenant_names.get(a.tenant_id),
            customer_name=a.customer.name if a.customer else None,
            regulatory_version_name=a.regulatory_version.name if a.regulatory_version else None,
            assessment_type=(
                services.derive_assessment_type(a.regulatory_version, all_versions)
                if a.regulatory_version else "historisch"
            ),
            status=a.status,
            regulatory_coverage=a.score_result.regulatory_coverage if a.score_result else None,
            quality_grade=a.score_result.quality_grade if a.score_result else None,
            created_at=a.created_at,
        )
        for a in assessments
    ]


@router.get("/assessments/{assessment_id}", response_model=schemas.AssessmentDetailOut)
def get_any_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Read-only Detailansicht ueber alle Tenants hinweg. Bewusst ein eigener
    Endpunkt statt einer Aufweichung des tenant-gefilterten Kunden-Endpunkts."""
    assessment = (
        db.query(models.Assessment)
        .options(
            joinedload(models.Assessment.customer),
            joinedload(models.Assessment.regulatory_version),
            joinedload(models.Assessment.requirement_statuses).joinedload(models.AssessmentRequirement.requirement),
            joinedload(models.Assessment.score_result),
            joinedload(models.Assessment.findings),
        )
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment nicht gefunden")

    all_versions = db.query(models.RegulatoryVersion).all()
    groups = (
        db.query(models.ProcessGroup)
        .options(joinedload(models.ProcessGroup.pis))
        .order_by(models.ProcessGroup.sequence)
        .all()
    )
    version = assessment.regulatory_version
    return schemas.AssessmentDetailOut(
        assessment=schemas.AssessmentOut(
            id=assessment.id,
            customer_id=assessment.customer_id,
            customer_name=assessment.customer.name if assessment.customer else None,
            market_role=assessment.customer.market_role if assessment.customer else None,
            sector=assessment.sector,
            business_scenario=assessment.business_scenario,
            customer_segments=assessment.customer_segments,
            status=assessment.status,
            created_at=assessment.created_at,
            regulatory_version_id=assessment.regulatory_version_id,
            regulatory_version_name=version.name if version else None,
            assessment_type=(
                services.derive_assessment_type(version, all_versions) if version else None
            ),
        ),
        requirement_statuses=assessment.requirement_statuses,
        score=assessment.score_result,
        findings=assessment.findings,
        process_groups=groups,
    )


# --- E) System --------------------------------------------------------------

@router.get("/system/health", response_model=schemas.SystemHealthOut)
def system_health(db: Session = Depends(get_db)):
    database_ok = True
    database_error = None
    counts = {"tenants": 0, "users": 0, "assessments": 0, "customers": 0, "versions": 0}
    try:
        db.execute(text("SELECT 1"))
        counts["tenants"] = db.query(models.Tenant).count()
        counts["users"] = db.query(models.User).count()
        counts["assessments"] = db.query(models.Assessment).count()
        counts["customers"] = db.query(models.Customer).count()
        counts["versions"] = db.query(models.RegulatoryVersion).count()
    except Exception as e:  # noqa: BLE001 -- Zweck ist gerade, JEDEN DB-Fehler zu melden
        database_ok = False
        database_error = str(e)

    return schemas.SystemHealthOut(
        api_ok=True,
        database_ok=database_ok,
        database_error=database_error,
        tenant_count=counts["tenants"],
        user_count=counts["users"],
        assessment_count=counts["assessments"],
        customer_count=counts["customers"],
        regulatory_version_count=counts["versions"],
    )


@router.post("/system/reseed")
def reseed(db: Session = Depends(get_db)):
    """Seed erneut ausfuehren. Idempotent -- vorhandene Daten bleiben unveraentert,
    fehlende werden ergaenzt. Nichts wird geloescht."""
    started = datetime.utcnow()
    run_seed(db)
    return {
        "status": "ok",
        "started_at": started,
        "tenant_count": db.query(models.Tenant).count(),
        "user_count": db.query(models.User).count(),
        "regulatory_version_count": db.query(models.RegulatoryVersion).count(),
    }
