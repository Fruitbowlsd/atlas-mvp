import type { Finding } from "../types";

export function FindingsList({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return <p style={{ color: "var(--text-muted)", fontSize: 13.5 }}>Keine offenen Findings.</p>;
  }
  return (
    <div className="findings-list">
      {findings.map((f) => (
        <div key={f.id} className={`finding-card ${f.severity}`}>
          <div className="finding-title">{f.title}</div>
          {f.description && <div className="finding-desc">{f.description}</div>}
          {f.recommendation && <div className="finding-rec">→ {f.recommendation}</div>}
        </div>
      ))}
    </div>
  );
}
