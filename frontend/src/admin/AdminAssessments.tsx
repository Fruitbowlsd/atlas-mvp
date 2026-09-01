import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AdminAssessmentRow, AssessmentDetail, AssessmentType, Tenant } from "../types";

const SECTOR_LABEL: Record<string, string> = { gas: "Gas", strom: "Strom" };

/* Eigene Labels statt toUpperCase(): daraus wuerde sonst "IMSYS". */
const SEGMENT_LABEL: Record<string, string> = { slp: "SLP", rlm: "RLM", imsys: "iMSys", tlp: "TLP" };

const csvLabels = (csv: string | null, labels: Record<string, string>) =>
  (csv ?? "").split(",").filter(Boolean).map((v) => labels[v] ?? v.toUpperCase()).join(" & ") || "—";

const TYPE_LABEL: Record<AssessmentType, string> = {
  readiness: "Readiness",
  compliance: "Compliance",
  historisch: "Historisch",
};

const STATUS_LABEL: Record<string, string> = {
  in_bearbeitung: "In Bearbeitung",
  abgeschlossen: "Abgeschlossen",
};

/** Tenant-übergreifende Übersicht, bewusst read-only (Issue #13 C). */
export function AdminAssessments() {
  const [rows, setRows] = useState<AdminAssessmentRow[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [tenantFilter, setTenantFilter] = useState<number | "">("");
  const [detail, setDetail] = useState<AssessmentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.adminListTenants().then(setTenants).catch(() => setTenants([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    api.adminListAssessments(tenantFilter === "" ? undefined : Number(tenantFilter))
      .then(setRows)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, [tenantFilter]);

  const open = async (id: number) => {
    setError(null);
    try {
      setDetail(await api.adminGetAssessment(id));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const pct = (v: number | null) => (v === null ? "—" : `${v.toFixed(1)}%`);

  return (
    <div>
      <div className="admin-header">
        <div className="section-title" style={{ margin: 0 }}>Assessments</div>
        <select
          className="text-input"
          style={{ width: "auto", minWidth: 220 }}
          value={tenantFilter}
          onChange={(e) => setTenantFilter(e.target.value === "" ? "" : Number(e.target.value))}
        >
          <option value="">Alle Organisationen</option>
          {tenants.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>

      <p style={{ color: "var(--text-muted)", fontSize: 12.5, marginBottom: 14 }}>
        Nur lesend. Der Typ wird live aus dem Stichtag der jeweiligen Version abgeleitet.
      </p>

      {error && <div className="form-error">{error}</div>}
      {loading ? (
        <div className="loading">Lade Assessments …</div>
      ) : (
        <table className="import-table">
          <thead>
            <tr>
              <th>Organisation</th><th>Kunde</th><th>Version</th>
              <th>Typ</th><th>Abdeckung</th><th>Qualität</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="admin-row-clickable" onClick={() => open(r.id)}>
                <td>{r.tenant_name ?? "—"}</td>
                <td><strong>{r.customer_name ?? "—"}</strong></td>
                <td>{r.regulatory_version_name ?? "—"}</td>
                <td><span className={`type-badge type-${r.assessment_type}`}>{TYPE_LABEL[r.assessment_type]}</span></td>
                <td>{pct(r.regulatory_coverage)}</td>
                <td>{pct(r.quality_grade)}</td>
                <td>{STATUS_LABEL[r.status] ?? r.status}</td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={7} style={{ color: "var(--text-muted)" }}>Keine Assessments gefunden.</td></tr>
            )}
          </tbody>
        </table>
      )}

      {detail && (
        <div className="modal-overlay" onClick={() => setDetail(null)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="section-title" style={{ margin: 0 }}>{detail.assessment.customer_name}</div>
              <button className="modal-close" onClick={() => setDetail(null)}>×</button>
            </div>

            <div className="profile-summary-card" style={{ maxWidth: "none" }}>
              <div className="profile-summary-row">
                <span>Regulatorischer Stand</span><strong>{detail.assessment.regulatory_version_name ?? "—"}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Typ</span>
                <strong>{detail.assessment.assessment_type ? TYPE_LABEL[detail.assessment.assessment_type] : "—"}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Sparte</span>
                <strong>{csvLabels(detail.assessment.sector, SECTOR_LABEL)}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Kundensegment</span>
                <strong>{csvLabels(detail.assessment.customer_segments, SEGMENT_LABEL)}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Abdeckungsgrad</span><strong>{pct(detail.score?.regulatory_coverage ?? null)}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Qualitätsgrad</span><strong>{pct(detail.score?.quality_grade ?? null)}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Anforderungen</span><strong>{detail.requirement_statuses.length}</strong>
              </div>
              <div className="profile-summary-row">
                <span>Findings</span><strong>{detail.findings.length}</strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
