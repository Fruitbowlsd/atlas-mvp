import { useState } from "react";
import type { AssessmentRequirement, ProcessGroup } from "../types";
import { PiCard } from "./PiCard";

interface Props {
  group: ProcessGroup;
  requirementStatuses: AssessmentRequirement[];
  onChange: (id: number, patch: Record<string, string>) => void;
  defaultOpen?: boolean;
}

export function ProcessGroupAccordion({ group, requirementStatuses, onChange, defaultOpen }: Props) {
  const [open, setOpen] = useState(!!defaultOpen);

  const groupStatuses = requirementStatuses.filter((ar) =>
    group.pis.some((pi) => pi.id === ar.requirement.pi_id)
  );
  if (groupStatuses.length === 0) return null;

  const covered = groupStatuses.filter((ar) => ar.implementation_status === "implementiert").length;

  return (
    <div className="accordion">
      <button className="accordion-header" onClick={() => setOpen((o) => !o)}>
        <span className="accordion-title">{group.name}</span>
        <span className="accordion-meta">
          <span>{covered} / {groupStatuses.length} abgedeckt</span>
          <span>{open ? "–" : "+"}</span>
        </span>
      </button>
      {open && (
        <div className="accordion-body">
          {group.pis.map((pi) => (
            <PiCard
              key={pi.id}
              pi={pi}
              requirementStatuses={groupStatuses.filter((ar) => ar.requirement.pi_id === pi.id)}
              onChange={onChange}
            />
          ))}
        </div>
      )}
    </div>
  );
}
