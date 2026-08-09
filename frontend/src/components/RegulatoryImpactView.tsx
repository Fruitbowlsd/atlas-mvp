import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { RegulatoryImpact, RegulatoryImpactRequirementRef, RiskLevel } from "../types";

interface Props {
  assessmentId: number;
}

const RISK_LABELS: Record<RiskLevel, string> = {
  hoch: "Hoch",
  mittel: "Mittel",
  niedrig: "Niedrig",
};

const CATEGORY_LABELS: Record<string, string> = {
  neuer_prozess: "Neuer Prozess",
  neues_pflichtfeld: "Neues Pflichtfeld",
  neuer_code: "Neuer Code",
  neue_qualitaetsregel: "Neue Qualitätsregel",
  neuer_testfall: "Neuer Testfall",
};

type TileKey = "remain_valid" | "newly_required" | "dropped" | "test_cases";

/** Wandelt den Stichtag in eine Aussage um, die man nicht erst selbst ausrechnen muss. */
function formatCountdown(validFrom: string): { text: string; urgent: boolean } | null {
  const target = new Date(validFrom);
  if (Number.isNaN(target.getTime())) return null;

  const startOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const days = Math.round(
    (startOfDay(target).getTime() - startOfDay(new Date()).getTime()) / 86_400_000
  );

  if (days < 0) {
    const passed = Math.abs(days);
    return {
      text: passed < 14 ? `Stichtag vor ${passed} Tagen erreicht` : `Stichtag vor ${Math.round(passed / 7)} Wochen erreicht`,
      urgent: true,
    };
  }
  if (days === 0) return { text: "Stichtag ist heute", urgent: true };
  if (days < 14) return { text: `noch ${days} Tage bis zum Stichtag`, urgent: true };
  return { text: `noch ${Math.round(days / 7)} Wochen bis zum Stichtag`, urgent: days < 90 };
}

function RequirementTable({ rows }: { rows: RegulatoryImpactRequirementRef[] }) {
  if (rows.length === 0) {
    return <div className="tile-detail-empty">Keine Einträge in dieser Kategorie.</div>;
  }
  return (
    <table className="import-table">
      <thead>
        <tr><th>Code</th><th>Titel</th><th>PI</th></tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.requirement_code}>
            <td><span className="pi-number">{r.requirement_code}</span></td>
            <td>{r.title}</td>
            <td>{r.pi_number ?? "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function RegulatoryImpactView({ assessmentId }: Props) {
  const [impact, setImpact] = useState<RegulatoryImpact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openTile, setOpenTile] = useState<TileKey | null>(null);

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

  const countdown = impact.upcoming_version_valid_from
    ? formatCountdown(impact.upcoming_version_valid_from)
    : null;

  // Verbindlich vs. Konsultation entscheidet, ob man Ressourcen einplant oder nur beobachtet.
  const isBinding = impact.upcoming_version_status === "verbindlich" || impact.upcoming_version_status === "final";

  const testCaseChanges = impact.changes.filter((c) => c.category === "neuer_testfall");

  const TILES: { key: TileKey; label: string; count: number }[] = [
    { key: "remain_valid", label: "Bleiben gültig", count: impact.remain_valid_count },
    { key: "newly_required", label: "Neu benötigt", count: impact.newly_required.length },
    { key: "dropped", label: "Entfallen", count: impact.dropped.length },
    { key: "test_cases", label: "Neue Testfälle", count: impact.new_test_case_count },
  ];

  const renderTileDetail = () => {
    if (openTile === null) return null;
    const tile = TILES.find((t) => t.key === openTile);

    return (
      <div className="tile-detail">
        <div className="tile-detail-header">
          <span>{tile?.label}</span>
          <button className="modal-close" onClick={() => setOpenTile(null)} aria-label="Schließen">×</button>
        </div>
        {openTile === "remain_valid" && <RequirementTable rows={impact.remain_valid} />}
        {openTile === "newly_required" && <RequirementTable rows={impact.newly_required} />}
        {openTile === "dropped" && <RequirementTable rows={impact.dropped} />}
        {openTile === "test_cases" && (
          testCaseChanges.length === 0 ? (
            <div className="tile-detail-empty">Keine neuen Testfälle in dieser Umstellung.</div>
          ) : (
            <table className="import-table">
              <thead>
                <tr><th>Änderung</th><th>Prozessgruppe</th><th>PI</th></tr>
              </thead>
              <tbody>
                {testCaseChanges.map((c) => (
                  <tr key={c.id}>
                    <td>{c.title}</td>
                    <td>{c.process_group_name ?? "—"}</td>
                    <td>{c.pi_number ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}
      </div>
    );
  };

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Formatumstellungs-Impact</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 560, marginBottom: 12 }}>
        Bevorstehende Formatumstellung: <strong>{impact.upcoming_version_name}</strong>
      </p>

      <div className="impact-timing">
        <span className={`timing-badge ${isBinding ? "timing-binding" : "timing-draft"}`}>
          {isBinding ? "Verbindlich" : "Konsultationsstand"}
        </span>
        <span className="timing-note">
          {isBinding
            ? "Die Inhalte stehen fest — Ressourcen können eingeplant werden."
            : "Die Inhalte können sich noch ändern — Stand beobachten, noch nicht fest einplanen."}
        </span>
      </div>

      {impact.upcoming_version_valid_from && (
        <div className="impact-deadline">
          <span className="deadline-date">
            Stichtag {new Date(impact.upcoming_version_valid_from).toLocaleDateString("de-DE")}
          </span>
          {countdown && (
            <span className={`deadline-countdown ${countdown.urgent ? "deadline-urgent" : ""}`}>
              {countdown.text}
            </span>
          )}
        </div>
      )}

      <div className={`overall-risk-banner overall-risk-${impact.overall_risk ?? "niedrig"}`}>
        <div>
          <div className="overall-risk-label">Gesamt-Risiko</div>
          <div className="overall-risk-value">
            {impact.overall_risk ? RISK_LABELS[impact.overall_risk] : "—"}
          </div>
          <div className="overall-risk-hint">
            Höchstes Einzelrisiko unter {impact.published_change_count}{" "}
            {impact.published_change_count === 1 ? "Änderung" : "Änderungen"}
          </div>
        </div>
        <div className="overall-risk-effort">
          <div className="overall-risk-label">Geschätzter Gesamtaufwand</div>
          <div className="overall-risk-value">
            {impact.total_person_days !== null ? `${impact.total_person_days} PT` : "—"}
          </div>
          <div className="overall-risk-hint">
            {impact.total_person_days !== null ? "Summe der gepflegten Schätzungen" : "Noch nicht geschätzt"}
          </div>
        </div>
      </div>

      <p style={{ color: "var(--text-muted)", fontSize: 12.5, margin: "18px 0 14px" }}>
        Nur bereits veröffentlichte, redaktionell geprüfte Änderungen fließen hier ein.
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
        {TILES.map((t) => (
          <button
            key={t.key}
            className={`subscore subscore-clickable ${openTile === t.key ? "subscore-open" : ""}`}
            onClick={() => setOpenTile(openTile === t.key ? null : t.key)}
          >
            <div className="subscore-label">{t.label}</div>
            <div className="subscore-value">{t.count}</div>
            <div className="subscore-hint">{openTile === t.key ? "schließen" : "Details ansehen"}</div>
          </button>
        ))}
      </div>

      {renderTileDetail()}

      <div className="section-title">Regulatorische Änderungen ({impact.published_change_count})</div>
      {impact.affected_process_groups.length > 0 && (
        <div style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 14 }}>
          Betroffene Prozessgruppen: {impact.affected_process_groups.join(", ")}
        </div>
      )}

      {impact.changes.length === 0 ? (
        <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
          Noch keine veröffentlichten Änderungen.
        </div>
      ) : (
        <div className="findings-list">
          {impact.changes.map((c) => (
            <div key={c.id} className={`finding-card ${c.risk}`}>
              <div className="finding-title">{c.title}</div>
              <div style={{ display: "flex", gap: 6, margin: "4px 0 8px", flexWrap: "wrap" }}>
                <span className={`risk-badge risk-${c.risk}`}>Risiko: {RISK_LABELS[c.risk]}</span>
                <span className="risk-badge risk-niedrig">{CATEGORY_LABELS[c.category] ?? c.category}</span>
                {c.effort_person_days !== null && (
                  <span className="risk-badge risk-niedrig">{c.effort_person_days} PT</span>
                )}
                {/* Herkunft + Prueffstatus: der Kunde muss erkennen, worauf er sich verlaesst. */}
                {c.is_reviewed && <span className="risk-badge badge-reviewed">✓ geprüft</span>}
                {c.origin === "ki_vorschlag" && (
                  <span className="risk-badge risk-niedrig">von Atlas vorgeschlagen</span>
                )}
              </div>
              {c.description && <div className="finding-desc">{c.description}</div>}
              {c.recommendation && (
                <div className="finding-rec">→ Empfehlung: {c.recommendation}</div>
              )}
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                {c.process_group_name && <span>{c.process_group_name} </span>}
                {c.pi_number && <span className="pi-number" style={{ marginRight: 6 }}>{c.pi_number}</span>}
                {c.source_url && (
                  <a href={c.source_url} target="_blank" rel="noreferrer" style={{ color: "var(--accent-dark)" }}>
                    Quelle
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
