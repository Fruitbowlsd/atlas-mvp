"""Klassischer (kein LLM) Diff zweier RegulatoryVersion-Requirement-Kataloge.

Pipeline-Schritt 3 aus Planungsdokument Abschnitt 11.2: liefert nur die
tatsaechlich geaenderten Zeilen, damit Schritt 4 (Anthropic-API, siehe Schritt
2d) nicht den kompletten Katalog analysieren muss -- >95% weniger Tokens als
eine Volltext-Analyse.
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from . import models

# Felder, die bei gleichem Requirement-Code auf inhaltliche Aenderung geprueft
# werden. pi_id ist bewusst dabei -- der PI-/ProcessGroup-Katalog ist NICHT
# versioniert (dieselben Tabellen fuer alle RegulatoryVersion-Eintraege), der
# Vergleich ueber pi_id ist also trotz unterschiedlicher Version gueltig.
_COMPARED_FIELDS = [
    "title", "description", "pi_id", "transaction_reason", "response_code",
    "criticality", "weight", "applies_to_slp", "applies_to_rlm", "is_conditional",
]


@dataclass
class RequirementDiffEntry:
    change_type: str  # neu | geaendert | entfallen
    requirement_code: str
    title: str
    pi_number: str | None
    changed_fields: list[str] = field(default_factory=list)
    old_title: str | None = None


def diff_requirements(db: Session, old_version_id: int, new_version_id: int) -> list[RequirementDiffEntry]:
    """Vergleicht die Requirement-Kataloge zweier RegulatoryVersion-Eintraege.
    Matching-Schluessel ist `Requirement.code` (unique) -- gleicher Code in
    beiden Versionen = dieselbe fachliche Anforderung, ggf. inhaltlich geaendert."""
    old_reqs = {
        r.code: r for r in db.query(models.Requirement).filter(
            models.Requirement.regulatory_version_id == old_version_id
        ).all()
    }
    new_reqs = {
        r.code: r for r in db.query(models.Requirement).filter(
            models.Requirement.regulatory_version_id == new_version_id
        ).all()
    }

    entries: list[RequirementDiffEntry] = []

    for code, new_req in new_reqs.items():
        old_req = old_reqs.get(code)
        if old_req is None:
            entries.append(RequirementDiffEntry(
                change_type="neu",
                requirement_code=code,
                title=new_req.title,
                pi_number=new_req.pi.pi_number if new_req.pi else None,
            ))
            continue

        changed_fields = [f for f in _COMPARED_FIELDS if getattr(old_req, f) != getattr(new_req, f)]
        if changed_fields:
            entries.append(RequirementDiffEntry(
                change_type="geaendert",
                requirement_code=code,
                title=new_req.title,
                pi_number=new_req.pi.pi_number if new_req.pi else None,
                changed_fields=changed_fields,
                old_title=old_req.title,
            ))
        # keine Aenderung -> taucht im Diff gar nicht erst auf

    for code, old_req in old_reqs.items():
        if code not in new_reqs:
            entries.append(RequirementDiffEntry(
                change_type="entfallen",
                requirement_code=code,
                title=old_req.title,
                pi_number=old_req.pi.pi_number if old_req.pi else None,
            ))

    return entries
