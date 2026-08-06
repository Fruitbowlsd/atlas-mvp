import type { AssessmentRequirement } from "../types";

interface Props {
  ar: AssessmentRequirement;
  onChange: (id: number, patch: Record<string, string>) => void;
}

export function RequirementRow({ ar, onChange }: Props) {
  const testValue =
    ar.test_status === "nicht_getestet" ? "nicht_getestet" : ar.result_status;

  return (
    <div className="requirement-row">
      <div>
        <span className="requirement-title">{ar.requirement.title}</span>
        <span className="requirement-code">{ar.requirement.code}</span>
      </div>

      <select
        className="status-select"
        value={ar.implementation_status}
        onChange={(e) => onChange(ar.id, { implementation_status: e.target.value })}
      >
        <option value="nicht_implementiert">nicht implementiert</option>
        <option value="implementiert">implementiert</option>
      </select>

      <select
        className="status-select"
        value={testValue}
        onChange={(e) => {
          const v = e.target.value;
          if (v === "nicht_getestet") {
            onChange(ar.id, { test_status: "nicht_getestet", result_status: "offen" });
          } else {
            onChange(ar.id, { test_status: "getestet", result_status: v });
          }
        }}
      >
        <option value="nicht_getestet">nicht getestet</option>
        <option value="erfolgreich">getestet – erfolgreich</option>
        <option value="fehlgeschlagen">getestet – fehlgeschlagen</option>
      </select>

      <select
        className="status-select"
        value={ar.evidence_status}
        onChange={(e) => onChange(ar.id, { evidence_status: e.target.value })}
      >
        <option value="fehlt">Nachweis fehlt</option>
        <option value="vorhanden">Nachweis vorhanden</option>
      </select>
    </div>
  );
}
