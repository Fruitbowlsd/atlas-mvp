from datetime import datetime

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


def derive_assessment_type(
    version: models.RegulatoryVersion,
    all_versions: list[models.RegulatoryVersion],
    today: datetime | None = None,
) -> str:
    """Leitet den Assessment-Typ aus dem Stichtag der zugehoerigen RegulatoryVersion ab
    (Abschnitt 12.5) -- bewusst LIVE berechnet und nicht gespeichert, weil sich der Typ
    allein durch Zeitablauf aendert: aus einem "readiness" wird ohne jede Datenaenderung
    irgendwann "compliance" und spaeter "historisch".

    readiness   -- Stichtag liegt in der Zukunft (Vorbereitung auf eine Umstellung)
    compliance  -- die aktuell geltende Version (juengster Stichtag <= heute)
    historisch  -- von einer neueren, bereits geltenden Version abgeloest

    Ein leeres valid_from bedeutet "gilt seit jeher" (die Basis-Version hat keinen
    Stichtag) -- sonst fiele sie durch alle drei Faelle und haette gar keinen Typ.
    """
    today = today or datetime.utcnow()

    def effective_start(v: models.RegulatoryVersion) -> datetime:
        return v.valid_from or datetime.min

    if version.valid_from is not None and version.valid_from > today:
        return "readiness"

    already_valid = [v for v in all_versions if v.valid_from is None or v.valid_from <= today]
    if not already_valid:
        return "historisch"

    # id als Tiebreaker, damit mehrere Versionen ohne Stichtag deterministisch ordnen
    newest = max(already_valid, key=lambda v: (effective_start(v), v.id))
    return "compliance" if newest.id == version.id else "historisch"


# Segment-Kuerzel -> Flag auf dem Requirement. An einer Stelle, damit ein
# spaeter dazukommendes Segment nicht in mehreren if-Ketten nachgezogen werden
# muss (Abschnitt 14.2).
_SEGMENT_FLAGS = {
    "slp": "applies_to_slp",
    "rlm": "applies_to_rlm",
    "imsys": "applies_to_imsys",
    "tlp": "applies_to_tlp",
}

_SECTOR_FLAGS = {
    "gas": "applies_to_gas",
    "strom": "applies_to_strom",
}

# Zulaessiges Profil-Vokabular an einer Stelle (Abschnitt 14.2), damit
# Validierung, Filterung und Seed nicht auseinanderlaufen.
VALID_SEGMENTS = set(_SEGMENT_FLAGS)
VALID_SECTORS = set(_SECTOR_FLAGS)
# Ausgeschrieben und nicht als Kuerzel, passend zum bestehenden Bestand --
# "grund_ersatzversorger" und "beides" gibt es bereits und bleiben gueltig.
VALID_MARKET_ROLES = {
    "lieferant",
    "grund_ersatzversorger",
    "beides",
    "netzbetreiber",
    "messstellenbetreiber",
    "bilanzkreisverantwortlicher",
}


def requirement_matches_profile(
    req: models.Requirement, segments: set[str], sector: str | None = None
) -> bool:
    """Prueft, ob ein Requirement zum EVU-Profil passt (Abschnitt 14.2).

    ODER innerhalb der Segmente, UND zwischen den Dimensionen: wer SLP und RLM
    beliefert, sieht die Anforderungen beider Segmente -- aber nur die seiner
    Sparte. Genau so war die Regel schon fuer SLP/RLM gemeint, hier nur um die
    Sparte erweitert.

    sector=None laesst die Sparte bewusst offen. Das brauchen die Aufrufer, die
    noch kein Assessment in der Hand haben, sondern nur rohe Requirements.
    """
    if sector is not None:
        flag = _SECTOR_FLAGS.get(sector)
        # Unbekannte Sparte: nichts durchlassen. Lieber ein sichtbar leeres
        # Ergebnis als stillschweigend der falsche Katalog.
        if flag is None or not getattr(req, flag, False):
            return False

    return any(getattr(req, _SEGMENT_FLAGS[s], False) for s in segments if s in _SEGMENT_FLAGS)


def _is_relevant(
    ar: models.AssessmentRequirement, segments: set[str], sector: str | None = None
) -> bool:
    return requirement_matches_profile(ar.requirement, segments, sector)


def profile_of(assessment: models.Assessment) -> tuple[set[str], str | None]:
    """Segmente und Sparte eines Assessments -- an einer Stelle gelesen, damit die
    Relevanzfilterung in Score, Findings und Heatmap nicht auseinanderlaufen kann."""
    segments = {s.strip() for s in (assessment.customer_segments or "").split(",") if s.strip()}
    return segments, assessment.sector


def calculate_score(db: Session, assessment: models.Assessment) -> models.ScoreResult:
    segments, sector = profile_of(assessment)
    statuses = assessment.requirement_statuses

    relevant = [ar for ar in statuses if _is_relevant(ar, segments, sector)]

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

    segments, sector = profile_of(assessment)
    findings = []

    for ar in assessment.requirement_statuses:
        if not _is_relevant(ar, segments, sector):
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
    segments, sector = profile_of(assessment)
    groups = db.query(models.ProcessGroup).order_by(models.ProcessGroup.sequence).all()
    status_by_req_id = {ar.requirement_id: ar for ar in assessment.requirement_statuses}

    heatmap = []
    for group in groups:
        pi_ids = [pi.id for pi in group.pis]
        reqs = db.query(models.Requirement).filter(models.Requirement.pi_id.in_(pi_ids)).all()

        # Frueher stand die Regel hier als eigene if-Kette und musste bei jeder
        # neuen Dimension doppelt gepflegt werden -- jetzt dieselbe Funktion wie
        # ueberall sonst.
        relevant_reqs = [r for r in reqs if requirement_matches_profile(r, segments, sector)]

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
