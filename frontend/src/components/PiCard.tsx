import type { AssessmentRequirement, ProcessIdentifier } from "../types";
import { RequirementRow } from "./RequirementRow";

interface Props {
  pi: ProcessIdentifier;
  requirementStatuses: AssessmentRequirement[];
  onChange: (id: number, patch: Record<string, string>) => void;
}

export function PiCard({ pi, requirementStatuses, onChange }: Props) {
  if (requirementStatuses.length === 0) return null;

  const covered = requirementStatuses.filter(
    (ar) => ar.implementation_status === "implementiert"
  ).length;

  return (
    <div className="pi-card">
      <div className="pi-card-header">
        <span className="pi-number">PI {pi.pi_number}</span>
        <span className="pi-name">{pi.name}</span>
        <span className={`crit-badge crit-${pi.criticality}`}>{pi.criticality}</span>
      </div>
      <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6 }}>
        {covered} von {requirementStatuses.length} Fällen abgedeckt
      </div>
      {requirementStatuses.map((ar) => (
        <RequirementRow key={ar.id} ar={ar} onChange={onChange} />
      ))}
    </div>
  );
}
