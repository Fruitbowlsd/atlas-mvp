from sqlalchemy.orm import Session
from . import models

# Konfigurierbare Gewichte der Qualitaets-Unterdimensionen (Auftrag Abschnitt 22).
QUALITY_WEIGHTS = {
    "implementation_quality": 0.35,
    "test_quality": 0.35,
    "evidence_quality": 0.20,
    "actuality": 0.10,
}


def get_active_regulatory_version(db: Session) -> models.RegulatoryVersion | None:
    """Liefert die aktuell aktive RegulatoryVersion -- der Default-Referenzkatalog
    fuer neue Assessments (Abschnitt 11.7: Mehrfach-Versionen-Konzept). Vorher gab
    es dafuer nur `RegulatoryVersion.query.first()`, weil es genau eine Version gab."""
    return db.query(models.RegulatoryVersion).filter(models.RegulatoryVersion.is_active == True).first()  # noqa: E712


def requirement_matches_segments(req: models.Requirement, segments: set[str]) -> bool:
    """Prueft, ob ein Requirement fuer die uebergebenen Kundensegmente (slp/rlm)
    relevant ist. Von _is_relevant() UND der Regulatory-Impact-Berechnung
    (Schritt 2e, siehe routers_regulatory.py) gemeinsam genutzt -- dort gibt es
    fuer die kommende Version noch keine AssessmentRequirement-Zeilen, nur die
    rohen Requirements."""
    if "slp" in segments and req.applies_to_slp:
        return True
    if "rlm" in segments and req.applies_to_rlm:
        return True
    return False


def _is_relevant(ar: models.AssessmentRequirement, segments: set[str]) -> bool:
    return requirement_matches_segments(ar.requirement, segments)


def calculate_score(db: Session, assessment: models.Assessment) -> models.ScoreResult:
    segments = set(assessment.customer_segments.split(","))
    statuses = assessment.requirement_statuses

    relevant = [ar for ar in statuses if _is_relevant(ar, segments)]

    # --- Regulatorischer Abdeckungsgrad ---
    total_weight = sum(ar.requirement.weight for ar in relevant) or 1.0
    covered_weight = sum(
        ar.requirement.weight for ar in relevant if ar.implementation_status == "implementiert"
    )
    coverage = round(100 * covered_weight / total_weight, 1)

    # --- Qualitaetsgrad: nur ueber die tatsaechlich implementierten (=unterstuetzten) Faelle ---
    basis = [ar for ar in relevant if ar.implementation_status == "implementiert"]
    basis_weight = sum(ar.requirement.weight for ar in basis) or 1.0

    impl_quality_weight = sum(
        ar.requirement.weight for ar in basis if ar.result_status == "erfolgreich"
    )
    test_quality_weight = sum(
        ar.requirement.weight for ar in basis if ar.test_status == "getestet"
    )
    evidence_quality_weight = sum(
        ar.requirement.weight for ar in basis if ar.evidence_status == "vorhanden"
    )

    implementation_quality = round(100 * impl_quality_weight / basis_weight, 1)
    test_quality = round(100 * test_quality_weight / basis_weight, 1)
    evidence_quality = round(100 * evidence_quality_weight / basis_weight, 1)
    # Aktualitaet: im MVP vereinfacht als fixer Wert je regulatorischem Stand.
    actuality = 92.0

    quality_grade = round(
        QUALITY_WEIGHTS["implementation_quality"] * implementation_quality
        + QUALITY_WEIGHTS["test_quality"] * test_quality
        + QUALITY_WEIGHTS["evidence_quality"] * evidence_quality
        + QUALITY_WEIGHTS["actuality"] * actuality,
        1,
    )

    existing = assessment.score_result
    if existing:
        result = existing
    else:
        result = models.ScoreResult(assessment_id=assessment.id)
        db.add(result)

    result.regulatory_coverage = coverage
    result.quality_grade = quality_grade
    result.implementation_quality = implementation_quality
    result.test_quality = test_quality
    result.evidence_quality = evidence_quality
    result.actuality = actuality

    db.flush()
    return result


def generate_findings(db: Session, assessment: models.Assessment) -> list[models.Finding]:
    # Alte Findings ersetzen, damit Neuberechnung konsistent bleibt.
    db.query(models.Finding).filter(models.Finding.assessment_id == assessment.id).delete()

    segments = set(assessment.customer_segments.split(","))
    findings = []

    for ar in assessment.requirement_statuses:
        if not _is_relevant(ar, segments):
            continue
        req = ar.requirement

        if ar.implementation_status != "implementiert":
            findings.append(models.Finding(
                assessment_id=assessment.id,
                requirement_id=req.id,
                severity=req.criticality,
                title=f"{req.code}: nicht implementiert",
                description=f"'{req.title}' ist fuer dieses Profil relevant, aber noch nicht umgesetzt.",
                recommendation="Umsetzung priorisieren, insbesondere bei kritischer/hoher Einstufung.",
            ))
            continue

        if ar.test_status != "getestet":
            findings.append(models.Finding(
                assessment_id=assessment.id,
                requirement_id=req.id,
                severity=req.criticality,
                title=f"{req.code}: nicht getestet",
                description=f"'{req.title}' ist implementiert, aber es liegt kein dokumentierter Testlauf vor.",
                recommendation="Positiv- bzw. Negativtest durchfuehren und Ergebnis dokumentieren.",
            ))

        if ar.evidence_status != "vorhanden":
            findings.append(models.Finding(
                assessment_id=assessment.id,
                requirement_id=req.id,
                severity=req.criticality,
                title=f"{req.code}: Nachweis fehlt",
                description=f"Fuer '{req.title}' fehlt ein nachvollziehbarer Nachweis (Evidence).",
                recommendation="Nachweis (Log, Testprotokoll, Screenshot) hinterlegen.",
            ))

    db.add_all(findings)
    db.flush()
    return findings


def process_group_heatmap(db: Session, assessment: models.Assessment):
    segments = set(assessment.customer_segments.split(","))
    groups = db.query(models.ProcessGroup).order_by(models.ProcessGroup.sequence).all()
    status_by_req_id = {ar.requirement_id: ar for ar in assessment.requirement_statuses}

    heatmap = []
    for group in groups:
        pi_ids = [pi.id for pi in group.pis]
        reqs = db.query(models.Requirement).filter(models.Requirement.pi_id.in_(pi_ids)).all()

        relevant_reqs = []
        for r in reqs:
            if ("slp" in segments and r.applies_to_slp) or ("rlm" in segments and r.applies_to_rlm):
                relevant_reqs.append(r)

        if not relevant_reqs:
            continue

        total_w = sum(r.weight for r in relevant_reqs) or 1.0
        covered_w = sum(
            r.weight for r in relevant_reqs
            if status_by_req_id.get(r.id) and status_by_req_id[r.id].implementation_status == "implementiert"
        )

        basis = [r for r in relevant_reqs if status_by_req_id.get(r.id) and status_by_req_id[r.id].implementation_status == "implementiert"]
        basis_w = sum(r.weight for r in basis) or 1.0
        quality_w = sum(
            r.weight for r in basis
            if status_by_req_id[r.id].test_status == "getestet" and status_by_req_id[r.id].result_status == "erfolgreich"
        )

        coverage_pct = round(100 * covered_w / total_w, 1)
        quality_pct = round(100 * quality_w / basis_w, 1) if basis else 0.0

        if coverage_pct >= 80:
            status = "gruen"
        elif coverage_pct >= 50:
            status = "gelb"
        else:
            status = "rot"

        heatmap.append({
            "process_group": group.name,
            "coverage": coverage_pct,
            "quality": quality_pct,
            "status": status,
        })

    return heatmap
