import { useState } from "react";
import type { AssessmentRequirement, ProcessGroup } from "../types";

interface Msg {
  id: string;
  label: string;
  piNumber?: string;
}

interface Edge {
  id: string;
  a: "neu" | "nb" | "alt";
  b: "neu" | "nb" | "alt";
  messages: Msg[];
}

const POS: Record<string, { x: number; y: number; label: string }> = {
  neu: { x: 170, y: 90, label: "Neulieferant" },
  nb: { x: 530, y: 90, label: "Netzbetreiber" },
  alt: { x: 350, y: 360, label: "Altlieferant" },
};

const EDGES: Edge[] = [
  {
    id: "neu-alt",
    a: "neu",
    b: "alt",
    messages: [
      { id: "kuendigung", label: "Kündigung" },
      { id: "best-kuendigung", label: "Bestätigung Kündigung" },
    ],
  },
  {
    id: "neu-nb",
    a: "neu",
    b: "nb",
    messages: [
      { id: "anmeldung", label: "Anmeldung", piNumber: "44001" },
      { id: "bestaetigung", label: "Bestätigung Anmeldung", piNumber: "44002" },
    ],
  },
  {
    id: "nb-alt",
    a: "nb",
    b: "alt",
    messages: [{ id: "abmeldeanfrage", label: "Abmeldeanfrage", piNumber: "44010" }],
  },
];

function findPiCoverage(processGroups: ProcessGroup[], requirementStatuses: AssessmentRequirement[], piNumber: string) {
  for (const group of processGroups) {
    const pi = group.pis.find((p) => p.pi_number === piNumber);
    if (!pi) continue;
    const statuses = requirementStatuses.filter((ar) => ar.requirement.pi_id === pi.id);
    const covered = statuses.filter((ar) => ar.implementation_status === "implementiert").length;
    return { pi, groupName: group.name, covered, total: statuses.length };
  }
  return null;
}

interface Props {
  processGroups: ProcessGroup[];
  requirementStatuses: AssessmentRequirement[];
  onOpenAssessment: () => void;
}

export function MarketCommunicationTriangle({ processGroups, requirementStatuses, onOpenAssessment }: Props) {
  const [selectedEdge, setSelectedEdge] = useState<Edge>(EDGES[1]);
  const [selectedMsg, setSelectedMsg] = useState<Msg>(EDGES[1].messages[0]);

  const coverage = selectedMsg.piNumber
    ? findPiCoverage(processGroups, requirementStatuses, selectedMsg.piNumber)
    : null;

  return (
    <div>
      <svg width="100%" viewBox="0 0 700 420" role="img">
        <title>Dreiecksübersicht Marktpartner Lieferantenwechsel</title>
        <desc>Neulieferant, Netzbetreiber und Altlieferant mit klickbaren Verbindungen zwischen ihnen.</desc>

        {EDGES.map((edge) => {
          const pa = POS[edge.a];
          const pb = POS[edge.b];
          const isSelected = selectedEdge.id === edge.id;
          const midX = (pa.x + pb.x) / 2;
          const midY = (pa.y + pb.y) / 2;
          return (
            <g
              key={edge.id}
              style={{ cursor: "pointer" }}
              onClick={() => {
                setSelectedEdge(edge);
                setSelectedMsg(edge.messages[0]);
              }}
            >
              <line
                x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
                stroke={isSelected ? "var(--accent)" : "var(--border)"}
                strokeWidth={isSelected ? 3 : 1.5}
              />
              <circle cx={midX} cy={midY} r={16}
                fill={isSelected ? "var(--accent)" : "var(--surface)"}
                stroke="var(--accent)" strokeWidth={1.5} />
              <text x={midX} y={midY} textAnchor="middle" dominantBaseline="central"
                fontSize={12} fontWeight={600} fill={isSelected ? "white" : "var(--accent-dark)"}>
                {edge.messages.length}
              </text>
            </g>
          );
        })}

        {(Object.keys(POS) as (keyof typeof POS)[]).map((key) => {
          const p = POS[key];
          return (
            <g key={key}>
              <rect x={p.x - 80} y={p.y - 26} width={160} height={52} rx={10}
                fill="var(--accent-light)" stroke="var(--accent)" strokeWidth={0.5} />
              <text x={p.x} y={p.y} textAnchor="middle" dominantBaseline="central"
                fontSize={13.5} fontWeight={600} fill="var(--accent-dark)">{p.label}</text>
            </g>
          );
        })}
      </svg>

      <div style={{ display: "flex", gap: 8, marginTop: 4, marginBottom: 10 }}>
        {selectedEdge.messages.map((m) => (
          <button
            key={m.id}
            onClick={() => setSelectedMsg(m)}
            className={`text-button ${selectedMsg.id === m.id ? "active-pill" : ""}`}
            style={selectedMsg.id === m.id ? { background: "var(--accent-light)", borderColor: "var(--accent)" } : undefined}
          >
            {m.label}{m.piNumber ? ` (PI ${m.piNumber})` : ""}
          </button>
        ))}
      </div>

      <div className="pi-detail-panel">
        <div style={{ fontWeight: 500, fontSize: 13.5, marginBottom: 4 }}>{selectedMsg.label}</div>
        <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 10 }}>
          {POS[selectedEdge.a].label} ↔ {POS[selectedEdge.b].label}
        </div>

        {selectedMsg.piNumber && coverage && (
          <>
            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
              <span className="pi-number">PI {coverage.pi.pi_number}</span>
              <span className={`crit-badge crit-${coverage.pi.criticality}`}>{coverage.pi.criticality}</span>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{coverage.groupName}</span>
            </div>
            <div style={{ fontSize: 12.5, marginBottom: 10 }}>
              {coverage.covered} von {coverage.total} Anforderungen abgedeckt
            </div>
            <button className="text-button" onClick={onOpenAssessment}>Im Assessment ansehen</button>
          </>
        )}

        {!selectedMsg.piNumber && (
          <div style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
            Kein Bestandteil dieses MVP-Assessments (Kündigungsprozess zwischen Lieferanten,
            nur als E2E-Kontext dargestellt).
          </div>
        )}
      </div>
    </div>
  );
}
