from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from . import models, schemas, diff, ai_analysis, services
from .auth import require_auth

# Endpunkte fuer die interne Kuratoren-Oberflaeche (Planungsdokument Abschnitt 11.4).
# Rein intern -- nicht Teil der Kunden-Ansicht -- laeuft aber unter derselben
# Demo-Anmeldung wie der Rest des MVP (kein separates Rollenmodell im MVP).
router = APIRouter(prefix="/api", tags=["regulatory-intelligence"], dependencies=[Depends(require_auth)])

CATEGORIES = {"neuer_prozess", "neues_pflichtfeld", "neuer_code", "neue_qualitaetsregel", "neuer_testfall"}
RISK_EFFORT_LEVELS = {"hoch", "mittel", "niedrig"}
# Kanban-Spalten (Schritt 3/Korrektur): zu_pruefen = KI-Vorschlag noch nicht bestaetigt,
# entwurf = manuell in Bearbeitung, veroeffentlicht = live fuer Kunden sichtbar.
STATUSES = {"zu_pruefen", "entwurf", "veroeffentlicht"}
# Regulatorischer Reifegrad einer Version -- orthogonal zu is_active (= Standard-
# Katalog fuer neue Assessments) und zu den Kanban-Status oben.
VERSION_STATUSES = {"konsultation", "final", "verbindlich"}


def _validate_change_fields(category: str | None, risk: str | None, effort: str | None, status: str | None) -> None:
    if category is not None and category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"category muss einer von {sorted(CATEGORIES)} sein")
    if risk is not None and risk not in RISK_EFFORT_LEVELS:
        raise HTTPException(status_code=400, detail=f"risk muss einer von {sorted(RISK_EFFORT_LEVELS)} sein")
    if effort is not None and effort not in RISK_EFFORT_LEVELS:
        raise HTTPException(status_code=400, detail=f"effort muss einer von {sorted(RISK_EFFORT_LEVELS)} sein")
    if status is not None and status not in STATUSES:
        raise HTTPException(status_code=400, detail=f"status muss einer von {sorted(STATUSES)} sein")


def _to_change_out(change: models.RegulatoryChange) -> schemas.RegulatoryChangeOut:
    return schemas.RegulatoryChangeOut(
        id=change.id,
        title=change.title,
        description=change.description,
        category=change.category,
        process_group_id=change.process_group_id,
        process_group_name=change.process_group.name if change.process_group else None,
        pi_id=change.pi_id,
        pi_number=change.pi.pi_number if change.pi else None,
        risk=change.risk,
        effort=change.effort,
        effort_person_days=change.effort_person_days,
        recommendation=change.recommendation,
        message_type=change.message_type,
        effective_message_type=change.effective_message_type,
        source_url=change.source_url,
        status=change.status,
        origin=change.origin,
        regulatory_version_id=change.regulatory_version_id,
        created_at=change.created_at,
    )


# --- RegulatoryVersion: Anlegen kommt hier dazu, Auflisten bleibt in routers_reference.py ---

@router.patch("/regulatory-versions/{version_id}", response_model=schemas.RegulatoryVersionOut)
def update_regulatory_version(version_id: int, payload: schemas.RegulatoryVersionUpdate, db: Session = Depends(get_db)):
    """Nachpflegen der Versions-Metadaten -- im MVP vor allem die kuratierte
    Zusammenfassung, die in der Kunden-Vorschau angezeigt wird."""
    version = db.query(models.RegulatoryVersion).filter(models.RegulatoryVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="RegulatoryVersion nicht gefunden")

    data = payload.model_dump(exclude_unset=True)
    status = data.get("status")
    if status is not None and status not in VERSION_STATUSES:
        raise HTTPException(status_code=400, detail=f"status muss einer von {sorted(VERSION_STATUSES)} sein")

    for field, value in data.items():
        setattr(version, field, value)

    db.commit()
    db.refresh(version)
    return version


@router.post("/regulatory-versions", response_model=schemas.RegulatoryVersionOut)
def create_regulatory_version(payload: schemas.RegulatoryVersionCreate, db: Session = Depends(get_db)):
    if payload.predecessor_version_id is not None:
        predecessor = db.query(models.RegulatoryVersion).filter(
            models.RegulatoryVersion.id == payload.predecessor_version_id
        ).first()
        if not predecessor:
            raise HTTPException(status_code=404, detail="Vorgaenger-Version nicht gefunden")

    # is_active bewusst nicht aus dem Payload uebernommen: eine neue Version anzulegen
    # (z.B. fuer eine bevorstehende Formatumstellung) darf die aktuell aktive Version
    # nicht versehentlich ablösen -- Aktivierung ist ein eigener, spaeterer Schritt.
    version = models.RegulatoryVersion(
        name=payload.name,
        sector=payload.sector,
        status=payload.status,
        source_reference=payload.source_reference,
        valid_from=payload.valid_from,
        predecessor_version_id=payload.predecessor_version_id,
        is_active=False,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


# Bewusst KEIN DELETE-Endpunkt fuer RegulatoryVersion: ein Fehlklick hatte eine
# kuratierte Version samt aller zugehoerigen Aenderungen unwiederbringlich
# geloescht. Versionen werden deshalb gar nicht mehr entfernt -- der Seed legt
# fehlende Demo-Versionen beim Start ohnehin wieder an (siehe seed_runner.py).


@router.get("/regulatory-versions/{version_id}/diff", response_model=schemas.RegulatoryDiffSummary)
def get_regulatory_diff(version_id: int, against: int | None = None, db: Session = Depends(get_db)):
    """Klassischer Requirement-Diff (Pipeline-Schritt 3, Abschnitt 11.2) zwischen
    `version_id` und einer Vergleichsversion. `against` ist optional -- ohne
    Angabe wird die per `predecessor_version_id` hinterlegte Vorgaenger-Version
    verwendet (siehe Schritt 2a)."""
    new_version = db.query(models.RegulatoryVersion).filter(models.RegulatoryVersion.id == version_id).first()
    if not new_version:
        raise HTTPException(status_code=404, detail="RegulatoryVersion nicht gefunden")

    old_version_id = against if against is not None else new_version.predecessor_version_id
    if old_version_id is None:
        raise HTTPException(status_code=400, detail="Keine Vorgaenger-Version bekannt -- 'against' Parameter angeben")

    old_version = db.query(models.RegulatoryVersion).filter(models.RegulatoryVersion.id == old_version_id).first()
    if not old_version:
        raise HTTPException(status_code=404, detail="Vergleichs-Version nicht gefunden")

    entries = diff.diff_requirements(db, old_version_id, version_id)

    return schemas.RegulatoryDiffSummary(
        old_version_id=old_version_id,
        new_version_id=version_id,
        added_count=sum(1 for e in entries if e.change_type == "neu"),
        changed_count=sum(1 for e in entries if e.change_type == "geaendert"),
        removed_count=sum(1 for e in entries if e.change_type == "entfallen"),
        entries=[
            schemas.RequirementDiffOut(
                change_type=e.change_type,
                requirement_code=e.requirement_code,
                title=e.title,
                pi_number=e.pi_number,
                changed_fields=e.changed_fields,
                old_title=e.old_title,
            )
            for e in entries
        ],
    )


@router.post("/regulatory-versions/{version_id}/analyze-diff", response_model=list[schemas.RegulatoryChangeOut])
def analyze_regulatory_diff(version_id: int, against: int | None = None, db: Session = Depends(get_db)):
    """Pipeline-Schritt 4 (Abschnitt 11.2): holt den klassischen Diff (Schritt 3,
    siehe get_regulatory_diff), schickt NUR die neuen/geaenderten Zeilen an die
    Anthropic-API (ai_analysis.py) und legt das Ergebnis als KI-Vorschlaege
    (status=zu_pruefen, origin=ki_vorschlag) an -- der Kurator prueft sie in der
    Kanban-Spalte "Zu pruefen" (Kuratoren-UI, Schritt 2b) wie jede andere
    RegulatoryChange."""
    new_version = db.query(models.RegulatoryVersion).filter(models.RegulatoryVersion.id == version_id).first()
    if not new_version:
        raise HTTPException(status_code=404, detail="RegulatoryVersion nicht gefunden")

    old_version_id = against if against is not None else new_version.predecessor_version_id
    if old_version_id is None:
        raise HTTPException(status_code=400, detail="Keine Vorgaenger-Version bekannt -- 'against' Parameter angeben")

    diff_entries = diff.diff_requirements(db, old_version_id, version_id)
    relevant_entries = [e for e in diff_entries if e.change_type in ("neu", "geaendert")]

    try:
        assessments = ai_analysis.analyze_diff_entries(relevant_entries)
    except ai_analysis.AiAnalysisError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # requirement_code -> Requirement nachschlagen, damit die KI-Vorschlaege dieselbe
    # PI-/Prozessgruppen-Verknuepfung bekommen wie manuell angelegte Aenderungen.
    reqs_by_code = {
        r.code: r for r in db.query(models.Requirement).filter(
            models.Requirement.regulatory_version_id == version_id
        ).all()
    }

    created = []
    for item in assessments:
        req = reqs_by_code.get(item.get("requirement_code"))
        category = item.get("kategorie")
        risk = item.get("risiko")
        effort = item.get("aufwand")
        change = models.RegulatoryChange(
            title=item.get("titel") or item.get("requirement_code") or "Unbenannte Aenderung",
            description=item.get("beschreibung"),
            category=category if category in CATEGORIES else "neues_pflichtfeld",
            process_group_id=req.pi.process_group_id if req and req.pi else None,
            pi_id=req.pi_id if req else None,
            risk=risk if risk in RISK_EFFORT_LEVELS else "mittel",
            effort=effort if effort in RISK_EFFORT_LEVELS else "mittel",
            regulatory_version_id=version_id,
            status="zu_pruefen",    # KI-Vorschlaege starten unbestaetigt in der ersten Kanban-Spalte
            origin="ki_vorschlag",
        )
        db.add(change)
        created.append(change)

    db.commit()
    for c in created:
        db.refresh(c)
    return [_to_change_out(c) for c in created]


@router.get("/assessments/{assessment_id}/regulatory-impact", response_model=schemas.RegulatoryImpactOut)
def get_regulatory_impact(assessment_id: int, db: Session = Depends(get_db)):
    """Kunden-Ansicht 'Formatumstellungs-Impact' (Abschnitt 11.5). Nimmt automatisch
    die naechste nicht-aktive Version, deren predecessor_version_id auf die
    RegulatoryVersion des Assessments zeigt (siehe Rueckfrage Schritt 2e) -- kein
    zusaetzlicher Auswahlschritt fuer den Kunden. Nur VEROEFFENTLICHTE
    RegulatoryChange-Eintraege sind sichtbar, Entwuerfe bleiben kuratorenintern
    (11.4)."""
    assessment = (
        db.query(models.Assessment)
        .options(joinedload(models.Assessment.requirement_statuses).joinedload(models.AssessmentRequirement.requirement))
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment nicht gefunden")

    # Kontext zur Version des Assessments selbst -- damit die Kunden-Ansicht bei
    # fehlender Folgeversion unterscheiden kann, ob schlicht nichts Neues bekannt ist
    # oder ob bereits gegen den neuesten bekannten Stand gemessen wird.
    current_version = assessment.regulatory_version
    all_versions = db.query(models.RegulatoryVersion).all()

    def effective_start(v: models.RegulatoryVersion) -> datetime:
        return v.valid_from or datetime.min  # ohne Stichtag = "gilt seit jeher"

    latest_version = max(all_versions, key=lambda v: (effective_start(v), v.id)) if all_versions else None
    # Nur aussagekraeftig, wenn es ueberhaupt mehrere Staende gibt -- bei genau einer
    # Version waere "ihr messt gegen den neuesten Stand" eine inhaltsleere Aussage.
    is_latest = bool(
        current_version and latest_version
        and latest_version.id == current_version.id
        and len(all_versions) > 1
    )
    version_context = dict(
        current_version_name=current_version.name if current_version else None,
        current_version_valid_from=current_version.valid_from if current_version else None,
        is_latest_known_version=is_latest,
        known_version_count=len(all_versions),
    )

    upcoming = (
        db.query(models.RegulatoryVersion)
        .filter(
            models.RegulatoryVersion.predecessor_version_id == assessment.regulatory_version_id,
            models.RegulatoryVersion.is_active == False,  # noqa: E712
        )
        .order_by(models.RegulatoryVersion.id.desc())
        .first()
    )
    if not upcoming:
        return schemas.RegulatoryImpactOut(has_upcoming_version=False, **version_context)

    segments = set(assessment.customer_segments.split(","))

    old_reqs_by_code = {
        r.code: r for r in db.query(models.Requirement).filter(
            models.Requirement.regulatory_version_id == assessment.regulatory_version_id
        ).all()
    }
    new_reqs_by_code = {
        r.code: r for r in db.query(models.Requirement).filter(
            models.Requirement.regulatory_version_id == upcoming.id
        ).all()
    }
    ar_by_code = {ar.requirement.code: ar for ar in assessment.requirement_statuses}

    diff_entries = diff.diff_requirements(db, assessment.regulatory_version_id, upcoming.id)

    # X: bleiben gueltig -- Code existiert in beiden Katalogen (unveraendert ODER
    # geaendert, siehe 11.5: "unabhaengig vom bisherigen Stand") UND war beim
    # Kunden bereits implementiert.
    remain_valid = [
        schemas.RegulatoryImpactRequirementRef(
            requirement_code=code,
            title=new_reqs_by_code[code].title,
            pi_number=new_reqs_by_code[code].pi.pi_number if new_reqs_by_code[code].pi else None,
        )
        for code in old_reqs_by_code
        if code in new_reqs_by_code
        and ar_by_code.get(code)
        and ar_by_code[code].implementation_status == "implementiert"
    ]

    # Y: neu benoetigt -- nur neue Codes, die fuer die Kundensegmente ueberhaupt relevant sind.
    newly_required = [
        schemas.RegulatoryImpactRequirementRef(requirement_code=e.requirement_code, title=e.title, pi_number=e.pi_number)
        for e in diff_entries
        if e.change_type == "neu" and services.requirement_matches_segments(new_reqs_by_code[e.requirement_code], segments)
    ]

    # Z: entfallen -- war implementiert, existiert im neuen Katalog nicht mehr.
    dropped = [
        schemas.RegulatoryImpactRequirementRef(requirement_code=e.requirement_code, title=e.title, pi_number=e.pi_number)
        for e in diff_entries
        if e.change_type == "entfallen" and ar_by_code.get(e.requirement_code)
        and ar_by_code[e.requirement_code].implementation_status == "implementiert"
    ]

    # Score-Prognose: gleiche Gewichtsformel wie services.calculate_score, einmal
    # fuer den heutigen Stand (identisch zum gespeicherten ScoreResult) und einmal
    # projiziert auf den neuen Katalog (implementiert bleibt implementiert, neue
    # Codes gelten als noch nicht implementiert).
    relevant_old = [ar for ar in assessment.requirement_statuses if services.requirement_matches_segments(ar.requirement, segments)]
    total_old_weight = sum(ar.requirement.weight for ar in relevant_old) or 1.0
    covered_old_weight = sum(ar.requirement.weight for ar in relevant_old if ar.implementation_status == "implementiert")
    current_coverage = round(100 * covered_old_weight / total_old_weight, 1)

    relevant_new = [r for r in new_reqs_by_code.values() if services.requirement_matches_segments(r, segments)]
    total_new_weight = sum(r.weight for r in relevant_new) or 1.0
    covered_new_weight = sum(
        r.weight for r in relevant_new
        if ar_by_code.get(r.code) and ar_by_code[r.code].implementation_status == "implementiert"
    )
    projected_coverage = round(100 * covered_new_weight / total_new_weight, 1)

    # Nur veroeffentlichte Aenderungen sind kundensichtbar -- Entwuerfe und
    # ungeprüfte Atlas-Vorschlaege bleiben kuratorenintern (11.4).
    published_changes = db.query(models.RegulatoryChange).filter(
        models.RegulatoryChange.regulatory_version_id == upcoming.id,
        models.RegulatoryChange.status == "veroeffentlicht",
    ).options(
        joinedload(models.RegulatoryChange.process_group),
        joinedload(models.RegulatoryChange.pi),
    ).all()

    # Gesamtrisiko = hoechstes vorkommendes Einzelrisiko (eine "hoch"-Aenderung
    # reicht, um die gesamte Umstellung als hohes Risiko einzustufen).
    overall_risk = next(
        (level for level in ("hoch", "mittel", "niedrig") if any(c.risk == level for c in published_changes)),
        None,
    )

    # Nur summieren, wenn ueberhaupt jemand Personentage gepflegt hat -- sonst
    # wuerde eine "0 PT"-Angabe eine Schaetzung vortaeuschen, die es nicht gibt.
    person_day_values = [c.effort_person_days for c in published_changes if c.effort_person_days is not None]
    total_person_days = sum(person_day_values) if person_day_values else None

    # "Zuletzt aktualisiert": juengster Zeitpunkt aus der Version selbst und ihren
    # kundensichtbaren Aenderungen -- der Kunde sieht dadurch, wie frisch der Stand ist.
    timestamps = [t for t in (
        [upcoming.updated_at] + [c.updated_at for c in published_changes]
    ) if t is not None]
    last_updated = max(timestamps) if timestamps else None

    affected_message_types = sorted({
        mt for mt in (c.effective_message_type for c in published_changes) if mt
    })

    return schemas.RegulatoryImpactOut(
        has_upcoming_version=True,
        **version_context,
        upcoming_version_id=upcoming.id,
        upcoming_version_name=upcoming.name,
        upcoming_version_valid_from=upcoming.valid_from,
        upcoming_version_status=upcoming.status,
        upcoming_version_summary=upcoming.summary,
        upcoming_version_last_updated=last_updated,
        current_coverage=current_coverage,
        projected_coverage=projected_coverage,
        remain_valid_count=len(remain_valid),
        remain_valid=remain_valid,
        newly_required=newly_required,
        dropped=dropped,
        published_change_count=len(published_changes),
        risk_hoch_count=sum(1 for c in published_changes if c.risk == "hoch"),
        risk_mittel_count=sum(1 for c in published_changes if c.risk == "mittel"),
        risk_niedrig_count=sum(1 for c in published_changes if c.risk == "niedrig"),
        overall_risk=overall_risk,
        total_person_days=total_person_days,
        affected_process_groups=sorted({c.process_group.name for c in published_changes if c.process_group}),
        affected_message_types=affected_message_types,
        new_test_case_count=sum(1 for c in published_changes if c.category == "neuer_testfall"),
        changes=[
            schemas.RegulatoryImpactChange(
                id=c.id,
                title=c.title,
                description=c.description,
                category=c.category,
                risk=c.risk,
                effort=c.effort,
                effort_person_days=c.effort_person_days,
                recommendation=c.recommendation,
                message_type=c.effective_message_type,
                source_url=c.source_url,
                process_group_name=c.process_group.name if c.process_group else None,
                pi_number=c.pi.pi_number if c.pi else None,
                origin=c.origin,
                is_reviewed=True,  # veroeffentlicht == Kuration durchlaufen
            )
            for c in published_changes
        ],
    )


# --- RegulatoryChange: Kuratoren-CRUD ---

@router.get("/regulatory-changes", response_model=list[schemas.RegulatoryChangeOut])
def list_regulatory_changes(regulatory_version_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.RegulatoryChange).options(
        joinedload(models.RegulatoryChange.process_group),
        joinedload(models.RegulatoryChange.pi),
    )
    if regulatory_version_id is not None:
        query = query.filter(models.RegulatoryChange.regulatory_version_id == regulatory_version_id)
    changes = query.order_by(models.RegulatoryChange.created_at.desc()).all()
    return [_to_change_out(c) for c in changes]


@router.post("/regulatory-changes", response_model=schemas.RegulatoryChangeOut)
def create_regulatory_change(payload: schemas.RegulatoryChangeCreate, db: Session = Depends(get_db)):
    _validate_change_fields(payload.category, payload.risk, payload.effort, None)

    version = db.query(models.RegulatoryVersion).filter(
        models.RegulatoryVersion.id == payload.regulatory_version_id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="RegulatoryVersion nicht gefunden")

    change = models.RegulatoryChange(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        process_group_id=payload.process_group_id,
        pi_id=payload.pi_id,
        risk=payload.risk,
        effort=payload.effort,
        effort_person_days=payload.effort_person_days,
        recommendation=payload.recommendation,
        message_type=payload.message_type,
        source_url=payload.source_url,
        regulatory_version_id=payload.regulatory_version_id,
        status="entwurf",     # manuell angelegte Aenderungen starten immer als Entwurf
        origin="manuell",     # Schritt 2d ergaenzt "ki_vorschlag" fuer LLM-generierte Eintraege
    )
    db.add(change)
    db.commit()
    db.refresh(change)
    return _to_change_out(change)


@router.patch("/regulatory-changes/{change_id}", response_model=schemas.RegulatoryChangeOut)
def update_regulatory_change(change_id: int, payload: schemas.RegulatoryChangeUpdate, db: Session = Depends(get_db)):
    change = db.query(models.RegulatoryChange).filter(models.RegulatoryChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="RegulatoryChange nicht gefunden")

    data = payload.model_dump(exclude_unset=True)
    _validate_change_fields(data.get("category"), data.get("risk"), data.get("effort"), data.get("status"))

    for field, value in data.items():
        setattr(change, field, value)

    db.commit()
    db.refresh(change)
    return _to_change_out(change)


@router.delete("/regulatory-changes/{change_id}")
def delete_regulatory_change(change_id: int, db: Session = Depends(get_db)):
    change = db.query(models.RegulatoryChange).filter(models.RegulatoryChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="RegulatoryChange nicht gefunden")
    db.delete(change)
    db.commit()
    return {"deleted": True}
