import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from . import models

# Erkennt PI-Nummern (5-stellig, z.B. 44001) und typische Response-/Transaktionscodes
# (ein bis zwei Buchstaben + Ziffern, z.B. E03, ZC5, Z43) im Freitext.
PI_PATTERN = re.compile(r"\b4400\d\b|\b4401\d\b|\b4402\d\b|\b4403\d\b")
CODE_PATTERN = re.compile(r"\b[A-Z]{1,2}\d{1,2}\b")

STOPWORDS = {
    "der", "die", "das", "und", "oder", "mit", "für", "ein", "eine", "im", "in",
    "auf", "bei", "test", "testfall", "case", "tc", "check", "prüfung", "von", "zu",
}


@dataclass
class MatchCandidate:
    requirement_id: int
    requirement_code: str
    requirement_title: str
    confidence: float  # 0.0 - 1.0


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-ZäöüÄÖÜß]{3,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def match_row(raw_text: str, requirements: list[models.Requirement]) -> MatchCandidate | None:
    """Schlaegt die wahrscheinlichste Requirement-Zuordnung fuer eine Freitextzeile vor."""
    pi_hits = set(PI_PATTERN.findall(raw_text))
    code_hits = set(CODE_PATTERN.findall(raw_text.upper()))
    text_tokens = _tokenize(raw_text)

    best: MatchCandidate | None = None
    best_score = 0.0

    for req in requirements:
        score = 0.0
        req_pi_number = req.pi.pi_number if req.pi else None

        if req_pi_number and req_pi_number in pi_hits:
            score += 0.5
        if req.response_code and req.response_code in code_hits:
            score += 0.35
        if req.transaction_reason and req.transaction_reason in code_hits:
            score += 0.35

        title_tokens = _tokenize(req.title)
        overlap = text_tokens & title_tokens
        if title_tokens:
            score += 0.3 * (len(overlap) / len(title_tokens))

        if score > best_score:
            best_score = score
            best = MatchCandidate(
                requirement_id=req.id,
                requirement_code=req.code,
                requirement_title=req.title,
                confidence=min(round(score, 2), 1.0),
            )

    if best and best.confidence >= 0.2:
        return best
    return None


def status_from_text(raw_status: str) -> tuple[str, str, str]:
    """Leitet (implementation_status, test_status, result_status) aus einem Freitext-Statuswert ab."""
    s = raw_status.strip().lower()
    positive = {"done", "passed", "pass", "erfolgreich", "bestanden", "ok", "closed", "abgeschlossen", "ja"}
    negative_but_tested = {"failed", "fail", "fehlgeschlagen", "nicht bestanden"}

    if s in positive:
        return "implementiert", "getestet", "erfolgreich"
    if s in negative_but_tested:
        return "implementiert", "getestet", "fehlgeschlagen"
    if s:
        # unbekannter, aber nicht-leerer Status -> immerhin als implementiert werten,
        # aber ohne Testnachweis, damit nichts unbegruendet als "erfolgreich getestet" gilt
        return "implementiert", "nicht_getestet", "offen"
    return "nicht_implementiert", "nicht_getestet", "offen"


def get_requirements(db: Session, regulatory_version_id: int) -> list[models.Requirement]:
    return (
        db.query(models.Requirement)
        .filter(models.Requirement.regulatory_version_id == regulatory_version_id)
        .all()
    )
