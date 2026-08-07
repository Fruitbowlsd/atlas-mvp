import random

from sqlalchemy.orm import Session

from . import models, seed_data as sd

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


def run_seed(db: Session):
    if db.query(models.RegulatoryVersion).first():
        return  # bereits geseedet

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

    customer = models.Customer(name=sd.DEMO_CUSTOMER_NAME, market_role="lieferant", sector="gas")
    db.add(customer)
    db.flush()

    assessment = models.Assessment(
        customer_id=customer.id,
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

    # Regulatory Intelligence: reales Vorher-Nachher-Paar als feste Demo-Grundlage
    # (Abschnitt 11.8 -- kein Live-Monitoring, keine automatische Extraktion).
    reg_version_2 = models.RegulatoryVersion(
        **sd.REGULATORY_VERSION_2,
        predecessor_version_id=reg_version.id,
    )
    db.add(reg_version_2)
    db.flush()

    # Katalog der neuen Version = bestehender Katalog unveraendert uebernommen plus
    # die von Mitteilung 56 ergaenzten Requirements. Damit liefert der Diff ein
    # realistisches Bild ("das meiste bleibt gueltig, einiges kommt dazu") statt
    # eines leeren Katalogs, den die Diff-Logik als "alles entfallen" lesen wuerde.
    for req, _pi_number in requirements:
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
         recommendation, group_code, pi_number) in sd.REGULATORY_CHANGES_V2:
        db.add(models.RegulatoryChange(
            title=title,
            description=description,
            category=category,
            risk=risk,
            effort=effort,
            effort_person_days=person_days,
            recommendation=recommendation,
            process_group_id=group_by_code[group_code].id if group_code else None,
            pi_id=pi_by_number[pi_number].id if pi_number else None,
            source_url=sd.REGULATORY_VERSION_2["source_reference"],
            status="veroeffentlicht",  # direkt als Demo-Karten in der "Veroeffentlicht"-Spalte sichtbar
            origin="manuell",
            regulatory_version_id=reg_version_2.id,
        ))

    db.commit()
