import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AdminUser, Tenant } from "../types";

const EMPTY = { email: "", password: "", tenant_id: "" as number | "", is_atlas_admin: false };

export function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    Promise.all([api.adminListUsers(), api.adminListTenants()])
      .then(([u, t]) => { setUsers(u); setTenants(t); })
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const save = async () => {
    if (!form.email.trim() || !form.password || form.tenant_id === "") {
      setError("E-Mail, Passwort und Organisation sind erforderlich.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await api.adminCreateUser({
        email: form.email.trim(),
        password: form.password,
        tenant_id: Number(form.tenant_id),
        is_atlas_admin: form.is_atlas_admin,
      });
      setShowForm(false);
      setForm(EMPTY);
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (u: AdminUser) => {
    setError(null);
    try {
      await api.adminUpdateUser(u.id, { is_active: !u.is_active });
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const fmt = (d: string | null) => (d ? new Date(d).toLocaleDateString("de-DE") : "—");

  if (loading) return <div className="loading">Lade Nutzer …</div>;

  return (
    <div>
      <div className="admin-header">
        <div className="section-title" style={{ margin: 0 }}>Nutzer</div>
        <button
          className="recalc-button"
          onClick={() => { setForm(EMPTY); setError(null); setShowForm(true); }}
        >
          + Nutzer anlegen
        </button>
      </div>

      {error && <div className="form-error">{error}</div>}

      <table className="import-table">
        <thead>
          <tr>
            <th>E-Mail</th><th>Organisation</th><th>Anmeldung</th>
            <th>Letzter Login</th><th>Status</th><th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className={u.is_active ? "" : "import-row-unmatched"}>
              <td>
                <strong>{u.email}</strong>
                {u.is_atlas_admin && <span className="risk-badge risk-mittel" style={{ marginLeft: 6 }}>Atlas-Admin</span>}
              </td>
              <td>{u.tenant_name ?? "—"}</td>
              <td>{u.is_sso_user ? "SSO" : "Passwort"}</td>
              <td>{fmt(u.last_login_at)}</td>
              <td>
                <span className={`type-badge ${u.is_active ? "type-compliance" : "type-historisch"}`}>
                  {u.is_active ? "Aktiv" : "Deaktiviert"}
                </span>
              </td>
              <td>
                <button className="text-button" onClick={() => toggleActive(u)}>
                  {u.is_active ? "Deaktivieren" : "Aktivieren"}
                </button>
              </td>
            </tr>
          ))}
          {users.length === 0 && (
            <tr><td colSpan={6} style={{ color: "var(--text-muted)" }}>Noch keine Nutzer.</td></tr>
          )}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="section-title" style={{ margin: 0 }}>Neuer Nutzer</div>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>

            <div className="form-field">
              <label className="form-label">E-Mail</label>
              <input className="text-input" type="email" value={form.email}
                placeholder="name@unternehmen.de"
                onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="form-field">
              <label className="form-label">Passwort</label>
              <input className="text-input" type="text" value={form.password}
                placeholder="wird dem Nutzer mitgeteilt"
                onChange={(e) => setForm({ ...form, password: e.target.value })} />
              <div className="field-hint">
                Im Klartext sichtbar, damit es weitergegeben werden kann — es gibt
                noch keinen Einladungs- oder Zurücksetzen-Flow per E-Mail.
              </div>
            </div>
            <div className="form-field">
              <label className="form-label">Organisation</label>
              <select className="text-input" value={form.tenant_id}
                onChange={(e) => setForm({ ...form, tenant_id: e.target.value === "" ? "" : Number(e.target.value) })}>
                <option value="">— bitte wählen —</option>
                {tenants.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label className="checkbox-option" style={{ cursor: "pointer" }}>
                <input type="checkbox" checked={form.is_atlas_admin}
                  onChange={(e) => setForm({ ...form, is_atlas_admin: e.target.checked })} />
                Atlas-Admin (Zugriff auf diesen Verwaltungsbereich)
              </label>
            </div>

            {error && <div className="form-error">{error}</div>}
            <button className="recalc-button" onClick={save} disabled={saving}>
              {saving ? "Lege an …" : "Nutzer anlegen"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
