import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { SystemHealth } from "../types";

export function AdminSystem() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [reseeding, setReseeding] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    api.adminSystemHealth()
      .then(setHealth)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const reseed = async () => {
    const ok = window.confirm(
      "Alle Seed-Daten neu einlesen? Bestehende Demo-Daten bleiben erhalten falls schon vorhanden (idempotent)."
    );
    if (!ok) return;

    setReseeding(true);
    setMessage(null);
    setError(null);
    try {
      await api.adminReseed();
      setMessage("Seed-Daten wurden eingelesen. Fehlende Einträge wurden ergänzt, vorhandene blieben unverändert.");
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setReseeding(false);
    }
  };

  if (loading) return <div className="loading">Prüfe System …</div>;

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>System</div>

      {error && <div className="form-error">{error}</div>}
      {message && <div className="notice-info">{message}</div>}

      <div className="admin-status-row">
        <span className={`type-badge ${health?.api_ok ? "type-compliance" : "type-historisch"}`}>
          API {health?.api_ok ? "erreichbar" : "gestört"}
        </span>
        <span className={`type-badge ${health?.database_ok ? "type-compliance" : "type-historisch"}`}>
          Datenbank {health?.database_ok ? "verbunden" : "nicht erreichbar"}
        </span>
      </div>
      {health?.database_error && <div className="form-error">{health.database_error}</div>}

      <div className="kpi-grid" style={{ marginTop: 18 }}>
        <div className="kpi-card">
          <div className="kpi-value">{health?.tenant_count ?? 0}</div>
          <div className="kpi-label">Organisationen</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{health?.user_count ?? 0}</div>
          <div className="kpi-label">Nutzer</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{health?.assessment_count ?? 0}</div>
          <div className="kpi-label">Assessments</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{health?.regulatory_version_count ?? 0}</div>
          <div className="kpi-label">Regulatorische Stände</div>
        </div>
      </div>

      <div className="section-title">Seed-Daten</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 560, marginBottom: 12 }}>
        Legt fehlende Demo-Daten an. Der Vorgang ist idempotent — vorhandene Daten
        bleiben unverändert, es wird nichts gelöscht.
      </p>
      <button className="recalc-button" onClick={reseed} disabled={reseeding}>
        {reseeding ? "Lese ein …" : "Seed-Daten neu einlesen"}
      </button>
    </div>
  );
}
