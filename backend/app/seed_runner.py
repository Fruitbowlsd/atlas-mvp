import os
import random

from sqlalchemy.orm import Session

from . import auth, models, seed_data as sd

# Deterministische Demo-Statusvergabe: die Basisraten je Prozessgruppe spiegeln
# die im Auftrag beschriebene Luecken-Story wider (Abschnitt 29):
# Kern-PIs (Anmeldung) gut, Abmeldeanfrage/Informationsmeldungen/Bestandsabgleich
# teilweise, Stornierung schwach, SLP staerker als RLM, Nachweise bei
# Ablehnungscodes (PI 44003) oft luckenhaft.

GROUP_IMPLEMENTATION_RATE = {
    "registration": 0.82,
    "deregistration_request": 0.55,
    "information_messages": 0.65,
    "cancellation": 0.30,
    "business_data": 0.90,
    "portfolio_reconciliation": 0.60,
}

_RNG = random.Random(42)  # fest gesetzter Seed fuer reproduzierbare Demo-Daten


def _demo_status(pi_number: str, group_code: str, applies_slp: bool, applies_rlm: bool):
    rate = GROUP_IMPLEMENTATION_RATE[group_code]

    rlm_only = applies_rlm and not applies_slp
    slp_only = applies_slp and not applies_rlm
    if rlm_only:
        rate *= 0.55  # RLM-Abdeckung im Demo-Kunden systematisch schwaecher
    elif slp_only:
        rate = max(rate, 0.88)  # SLP weitgehend vollstaendig

    implemented = _RNG.random() < rate
    if not implemented:
        return (sd.NICHT_IMPLEMENTIERT, sd.NICHT_GETESTET, sd.OFFEN, sd.FEHLT)

    test_rate = 0.70
    tested = _RNG.random() < test_rate
    if not tested:
        return (sd.IMPLEMENTIERT, sd.NICHT_GETESTET, sd.OFFEN, sd.FEHLT)

    result_success_rate = 0.90
    result = sd.ERFOLGREICH if _RNG.random() < result_success_rate else "fehlgeschlagen"

    # Nachweise fehlen ueberproportional bei Ablehnungscodes (PI 44003)
    evidence_rate = 0.35 if pi_number == "44003" else 0.65
    evidence = sd.VORHANDEN if _RNG.random() < evidence_rate else sd.FEHLT

    return (sd.IMPLEMENTIERT, sd.GETESTET, result, evidence)


def _version_by_name(db: Session, name: str) -> models.RegulatoryVersion | None:
    return db.query(models.RegulatoryVersion).filter(models.RegulatoryVersion.name == name).first()


def run_seed(db: Session):
    """Legt fehlende Demo-Daten an -- bewusst je Datensatz geprueft statt alles
    oder nichts. Frueher stoppte ein einziger Guard ("existiert irgendeine
    RegulatoryVersion? -> fertig") den kompletten Seed, sobald die Basisversion
    da war: eine geloeschte Folgeversion kam dadurch auch nach einem Neustart
    nie zurueck. Jetzt wird jeder Block einzeln nachgezogen, ohne vorhandene
    Daten zu duplizieren."""
    _seed_tenant(db)

    if not _version_by_name(db, sd.REGULATORY_VERSION["name"]):
        # Die Basisversion wird am Namen erkannt. Wurde sie umbenannt (z.B. weil der
        # Stand auf eine neuere Formatumstellung aktualisiert wurde), faende der
        # Namensabgleich sie nicht mehr und legte einen ZWEITEN Basiskatalog samt
        # Demo-Kunde an. Deshalb zuerst die vorhandene aktive Version nachziehen.
        existing_base = (
            db.query(models.RegulatoryVersion)
            .filter(models.RegulatoryVersion.is_active == True)  # noqa: E712
            .first()
        )
        if existing_base:
            for field, value in sd.REGULATORY_VERSION.items():
                setattr(existing_base, field, value)
            db.commit()
        else:
            _seed_base(db)

    if not _version_by_name(db, sd.REGULATORY_VERSION_2["name"]):
        _seed_upcoming_version(db)


def _seed_tenant(db: Session) -> models.Tenant:
    """Default-Tenant anlegen und bestehende Kundendaten ihm zuordnen (Abschnitt 13.2).
    Idempotent wie alle anderen Seed-Bloecke -- und ordnet zusaetzlich Datensaetze
    ohne tenant_id nach, die vor der Multi-Tenancy-Einfuehrung entstanden sind."""
    tenant = db.query(models.Tenant).filter(models.Tenant.slug == sd.DEMO_TENANT["slug"]).first()
    if not tenant:
        tenant = models.Tenant(**sd.DEMO_TENANT)
        db.add(tenant)
        db.flush()

    db.query(models.Customer).filter(models.Customer.tenant_id.is_(None)).update(
        {"tenant_id": tenant.id}
    )
    db.query(models.Assessment).filter(models.Assessment.tenant_id.is_(None)).update(
        {"tenant_id": tenant.id}
    )
    db.commit()
    _seed_demo_user(db, tenant)
    return tenant


def _seed_demo_user(db: Session, tenant: models.Tenant) -> None:
    """Zugang zur Demo (Abschnitt 13.4). Idempotent wie die uebrigen Bloecke.
    Ersetzt das frueher gemeinsame Passwort -- es gibt jetzt ein echtes Konto."""
    existing = db.query(models.User).filter(models.User.email == sd.DEMO_USER_EMAIL).first()
    if existing:
        # Bestandsnutzer aus der Zeit vor dem Admin-Flag nachziehen -- sonst waere der
        # Demo-Zugang nach dem Update aus dem Admin-Bereich ausgesperrt.
        if not existing.is_atlas_admin:
            existing.is_atlas_admin = True
            db.commit()
        return

    password = os.getenv("ATLAS_DEMO_PASSWORD", "atlas-demo")
    db.add(models.User(
        email=sd.DEMO_USER_EMAIL,
        password_hash=auth.hash_password(password),
        tenant_id=tenant.id,
        is_active=True,
        is_atlas_admin=True,   # Demo-Zugang ist zugleich der Atlas-Admin
    ))
    db.commit()


def _seed_base(db: Session):
    """Basiskatalog (GeLi Gas 2.0 / UTILMD Gas G1.1) plus Demo-Kunde und dessen
    Assessment."""
    reg_version = models.RegulatoryVersion(**sd.REGULATORY_VERSION)
    db.add(reg_version)
    db.flush()

    group_by_code = {}
    for g in sd.PROCESS_GROUPS:
        group = models.ProcessGroup(**g)
        db.add(group)
        db.flush()
        group_by_code[g["code"]] = group

    pi_by_number = {}
    pi_group_code = {}
    for pi_number, name, sender, receiver, group_code, criticality in sd.PROCESS_IDENTIFIERS:
        pi = models.ProcessIdentifier(
            pi_number=pi_number,
            name=name,
            sender_role=sender,
            receiver_role=receiver,
            message_type="UTILMD",
            process_group_id=group_by_code[group_code].id,
            criticality=criticality,
            weight=sd.WEIGHT_BY_CRITICALITY[criticality],
        )
        db.add(pi)
        db.flush()
        pi_by_number[pi_number] = pi
        pi_group_code[pi_number] = group_code

    requirements = []
    for code, title, pi_number, tx_reason, resp_code, criticality, slp, rlm in sd.REQUIREMENTS:
        req = models.Requirement(
            code=code,
            title=title,
            pi_id=pi_by_number[pi_number].id,
            transaction_reason=tx_reason,
            response_code=resp_code,
            criticality=criticality,
            weight=sd.WEIGHT_BY_CRITICALITY[criticality],
            applies_to_slp=slp,
            applies_to_rlm=rlm,
            regulatory_version_id=reg_version.id,
        )
        db.add(req)
        db.flush()
        requirements.append((req, pi_number))

    tenant = db.query(models.Tenant).filter(models.Tenant.slug == sd.DEMO_TENANT["slug"]).first()
    customer = models.Customer(
        name=sd.DEMO_CUSTOMER_NAME,
        market_role="lieferant",
        sector="gas",
        tenant_id=tenant.id if tenant else None,
    )
    db.add(customer)
    db.flush()

    assessment = models.Assessment(
        customer_id=customer.id,
        tenant_id=customer.tenant_id,
        regulatory_version_id=reg_version.id,
        business_scenario="lieferantenwechsel",
        customer_segments="slp,rlm",
        status="in_bearbeitung",
    )
    db.add(assessment)
    db.flush()

    for req, pi_number in requirements:
        group_code = pi_group_code[pi_number]
        impl, test, result, evidence = _demo_status(
            pi_number, group_code, req.applies_to_slp, req.applies_to_rlm
        )
        ar = models.AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req.id,
            relevance_status="relevant",
            implementation_status=impl,
            test_status=test,
            result_status=result,
            evidence_status=evidence,
        )
        db.add(ar)

    db.commit()


def _seed_upcoming_version(db: Session):
    """Bevorstehende Formatumstellung (Mitteilung Nr. 56) als feste Demo-Grundlage
    -- Abschnitt 11.8: kein Live-Monitoring, keine automatische Extraktion.
    Liest den Basiskatalog aus der DB statt ihn uebergeben zu bekommen, damit der
    Block auch nachtraeglich allein laufen kann (z.B. wenn die Version zwischendurch
    entfernt wurde und beim naechsten Start wiederkommen soll)."""
    base_version = _version_by_name(db, sd.REGULATORY_VERSION["name"])
    if base_version is None:
        return  # ohne Basiskatalog gibt es nichts fortzuschreiben

    group_by_code = {g.code: g for g in db.query(models.ProcessGroup).all()}
    pi_by_number = {p.pi_number: p for p in db.query(models.ProcessIdentifier).all()}
    base_requirements = db.query(models.Requirement).filter(
        models.Requirement.regulatory_version_id == base_version.id
    ).all()

    reg_version_2 = models.RegulatoryVersion(
        **sd.REGULATORY_VERSION_2,
        predecessor_version_id=base_version.id,
    )
    db.add(reg_version_2)
    db.flush()

    # Katalog der neuen Version = bestehender Katalog unveraendert uebernommen plus
    # die von Mitteilung 56 ergaenzten Requirements. Damit liefert der Diff ein
    # realistisches Bild ("das meiste bleibt gueltig, einiges kommt dazu") statt
    # eines leeren Katalogs, den die Diff-Logik als "alles entfallen" lesen wuerde.
    for req in base_requirements:
        db.add(models.Requirement(
            code=req.code,
            title=req.title,
            description=req.description,
            pi_id=req.pi_id,
            transaction_reason=req.transaction_reason,
            response_code=req.response_code,
            criticality=req.criticality,
            weight=req.weight,
            applies_to_slp=req.applies_to_slp,
            applies_to_rlm=req.applies_to_rlm,
            is_conditional=req.is_conditional,
            regulatory_version_id=reg_version_2.id,
        ))

    for code, title, pi_number, tx_reason, resp_code, criticality, slp, rlm in sd.REQUIREMENTS_V2_NEW:
        db.add(models.Requirement(
            code=code,
            title=title,
            pi_id=pi_by_number[pi_number].id,
            transaction_reason=tx_reason,
            response_code=resp_code,
            criticality=criticality,
            weight=sd.WEIGHT_BY_CRITICALITY[criticality],
            applies_to_slp=slp,
            applies_to_rlm=rlm,
            regulatory_version_id=reg_version_2.id,
        ))

    for (title, description, category, risk, effort, person_days,
         recommendation, message_type, group_code, pi_number) in sd.REGULATORY_CHANGES_V2:
        db.add(models.RegulatoryChange(
            title=title,
            description=description,
            category=category,
            risk=risk,
            effort=effort,
            effort_person_days=person_days,
            recommendation=recommendation,
            message_type=message_type,
            process_group_id=group_by_code[group_code].id if group_code else None,
            pi_id=pi_by_number[pi_number].id if pi_number else None,
            source_url=sd.REGULATORY_VERSION_2["source_reference"],
            status="veroeffentlicht",  # direkt als Demo-Karten in der "Veroeffentlicht"-Spalte sichtbar
            origin="manuell",
            regulatory_version_id=reg_version_2.id,
        ))

    db.commit()
