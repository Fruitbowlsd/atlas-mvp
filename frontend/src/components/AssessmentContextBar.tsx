import type { AssessmentOut, AssessmentType } from "../types";

const TYPE_LABEL: Record<AssessmentType, string> = {
  readiness: "Readiness",
  compliance: "Compliance",
  historisch: "Historisch",
};

const STATUS_LABEL: Record<string, string> = {
  in_bearbeitung: "In Bearbeitung",
  abgeschlossen: "Abgeschlossen",
};

/** Schreibgeschützte Orientierungszeile über allen Seiten, die Zahlen eines
 *  konkreten Assessments zeigen. Bewusst OHNE Umschalter -- gewechselt wird
 *  weiterhin über die Assessment-Historie im Kundenprofil. */
export function AssessmentContextBar({ assessment }: { assessment: AssessmentOut }) {
  return (
    <div className="assessment-context">
      <strong>{assessment.customer_name ?? "—"}</strong>
      <span className="context-sep">·</span>
      <span>{assessment.regulatory_version_name ?? "kein regulatorischer Stand"}</span>
      {assessment.assessment_type && (
        <span className={`type-badge type-${assessment.assessment_type}`}>
          {TYPE_LABEL[assessment.assessment_type]}
        </span>
      )}
      <span className="context-sep">·</span>
      <span>{STATUS_LABEL[assessment.status] ?? assessment.status}</span>
    </div>
  );
}
