import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { RegulatoryImpact } from "../types";

interface Props {
  assessmentId: number;
}

export function RegulatoryImpactView({ assessmentId }: Props) {
  const [impact, setImpact] = useState<RegulatoryImpact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.getRegulatoryImpact(assessmentId)
      .then(setImpact)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, [assessmentId]);

  if (loading) return <div className="loading">Lade Formatumstellungs-Impact …</div>;
  if (error) return <div className="error">Fehler: {error}</div>;
  if (!impact) return null;

  if (!impact.has_upcoming_version) {
    return (
      <div>
        <div className="section-title" style={{ marginTop: 0 }}>Formatumstellungs-Impact</div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 520 }}>
          Aktuell ist keine bevorstehende Formatumstellung für euren regulatorischen
          Stand bekannt. Sobald eine neue Version kuratiert wird, seht ihr hier den
          Impact auf euren Abdeckungsgrad.
        </p>
      </div>
    );
  }

  const delta = (impact.projected_coverage ?? 0) - (impact.current_coverage ?? 0);
  const deltaLabel = delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1);
  const deltaColor = delta > 0 ? "var(--success)" : delta < 0 ? "var(--danger)" : "var(--text-muted)";

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Formatumstellungs-Impact</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 560, marginBottom: 4 }}>
        Bevorstehende Formatumstellung: <strong>{impact.upcoming_version_name}</strong>
        {impact.upcoming_version_valid_from &&
          ` · gültig ab ${new Date(impact.upcoming_version_valid_from).toLocaleDateString("de-DE")}`}
      </p>
      <p style={{ color: "var(--text-muted)", fontSize: 12.5, marginBottom: 20 }}>
        Nur bereits veröffentlichte Änderungen fließen hier ein — Entwürfe sind noch
        kuratorenintern.
      </p>

      <div className="score-grid">
        <div className="score-card">
          <div className="score-card-label">Abdeckungsgrad heute</div>
          <div className="score-card-value">{(impact.current_coverage ?? 0).toFixed(1)}%</div>
          <div className="score-card-bar">
            <div className="score-card-bar-fill" style={{ width: `${impact.current_coverage ?? 0}%` }} />
          </div>
        </div>
        <div className="score-card">
          <div className="score-card-label">Abdeckungsgrad nach Umstellung (Prognose)</div>
          <div className="score-card-value" style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            {(impact.projected_coverage ?? 0).toFixed(1)}%
            <span style={{ fontSize: 13, fontWeight: 600, color: deltaColor }}>
              ({deltaLabel} Pkt.)
            </span>
          </div>
          <div className="score-card-bar">
            <div className="score-card-bar-fill" style={{ width: `${impact.projected_coverage ?? 0}%` }} />
          </div>
        </div>
      </div>

      <div className="subscore-grid">
        <div className="subscore">
          <div className="subscore-label">Bleiben gültig</div>
          <div className="subscore-value">{impact.remain_valid_count}</div>
        </div>
        <div className="subscore">
          <div className="subscore-label">Neu benötigt</div>
          <div className="subscore-value">{impact.newly_required.length}</div>
        </div>
        <div className="subscore">
          <div className="subscore-label">Entfallen</div>
          <div className="subscore-value">{impact.dropped.length}</div>
        </div>
        <div className="subscore">
          <div className="subscore-label">Neue Testfälle</div>
          <div className="subscore-value">{impact.new_test_case_count}</div>
        </div>
      </div>

      <div className="section-title">Regulatorische Änderungen ({impact.published_change_count})</div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
        {impact.risk_hoch_count > 0 && <span className="crit-badge crit-hoch">{impact.risk_hoch_count} hohes Risiko</span>}
        {impact.risk_mittel_count > 0 && <span className="crit-badge crit-mittel">{impact.risk_mittel_count} mittleres Risiko</span>}
        {impact.risk_niedrig_count > 0 && <span className="crit-badge crit-niedrig">{impact.risk_niedrig_count} niedriges Risiko</span>}
        {impact.published_change_count === 0 && (
          <span style={{ color: "var(--text-muted)", fontSize: 13 }}>Noch keine veröffentlichten Änderungen.</span>
        )}
      </div>
      {impact.affected_process_groups.length > 0 && (
        <div style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 20 }}>
          Betroffene Prozessgruppen: {impact.affected_process_groups.join(", ")}
        </div>
      )}

      {impact.newly_required.length > 0 && (
        <>
          <div className="section-title">Neu benötigte Requirements</div>
          <table className="import-table" style={{ marginBottom: 20 }}>
            <thead>
              <tr><th>Code</th><th>Titel</th><th>PI</th></tr>
            </thead>
            <tbody>
              {impact.newly_required.map((r) => (
                <tr key={r.requirement_code}>
                  <td><span className="pi-number">{r.requirement_code}</span></td>
                  <td>{r.title}</td>
                  <td>{r.pi_number ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {impact.dropped.length > 0 && (
        <>
          <div className="section-title">Entfallene Requirements (bisher implementiert)</div>
          <table className="import-table">
            <thead>
              <tr><th>Code</th><th>Titel</th><th>PI</th></tr>
            </thead>
            <tbody>
              {impact.dropped.map((r) => (
                <tr key={r.requirement_code}>
                  <td><span className="pi-number">{r.requirement_code}</span></td>
                  <td>{r.title}</td>
                  <td>{r.pi_number ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
