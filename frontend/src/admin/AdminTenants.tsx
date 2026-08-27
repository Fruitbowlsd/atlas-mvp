import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Tenant } from "../types";

const SSO_OPTIONS = [
  { value: "", label: "Kein SSO (Passwort-Login)" },
  { value: "entra", label: "Microsoft Entra ID" },
];

const EMPTY = { name: "", slug: "", email_domain: "", sso_provider: "", sso_tenant_id: "" };

export function AdminTenants() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState<Tenant | null>(null);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    api.adminListTenants()
      .then(setTenants)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  /** Aus dem Namen einen brauchbaren Slug ableiten -- Umlaute ausgeschrieben, damit
   *  daraus keine leeren Zeichen werden. */
  const slugify = (value: string) =>
    value.toLowerCase()
      .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY);
    setError(null);
    setShowForm(true);
  };

  const openEdit = (t: Tenant) => {
    setEditing(t);
    setForm({
      name: t.name,
      slug: t.slug,
      email_domain: t.email_domain ?? "",
      sso_provider: t.sso_provider ?? "",
      sso_tenant_id: t.sso_tenant_id ?? "",
    });
    setError(null);
    setShowForm(true);
  };

  const save = async () => {
    if (!form.name.trim()) { setError("Bitte einen Namen angeben."); return; }
    setSaving(true);
    setError(null);
    const payload = {
      name: form.name.trim(),
      slug: (form.slug.trim() || slugify(form.name)),
      email_domain: form.email_domain.trim() || null,
      sso_provider: form.sso_provider || null,
      sso_tenant_id: form.sso_tenant_id.trim() || null,
    };
    try {
      if (editing) await api.adminUpdateTenant(editing.id, payload);
      else await api.adminCreateTenant(payload);
      setShowForm(false);
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (t: Tenant) => {
    try {
      await api.adminUpdateTenant(t.id, { is_active: !t.is_active });
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  if (loading) return <div className="loading">Lade Organisationen …</div>;

  return (
    <div>
      <div className="admin-header">
        <div className="section-title" style={{ margin: 0 }}>Organisationen</div>
        <button className="recalc-button" onClick={openCreate}>+ Organisation anlegen</button>
      </div>

      {error && <div className="form-error">{error}</div>}

      <table className="import-table">
        <thead>
          <tr>
            <th>Name</th><th>Slug</th><th>Domain</th><th>SSO</th>
            <th>Nutzer</th><th>Kunden</th><th>Status</th><th></th>
          </tr>
        </thead>
        <tbody>
          {tenants.map((t) => (
            <tr key={t.id} className={t.is_active ? "" : "import-row-unmatched"}>
              <td><strong>{t.name}</strong></td>
              <td><span className="pi-number">{t.slug}</span></td>
              <td>{t.email_domain ?? "—"}</td>
              <td>{t.sso_provider === "entra" ? "Entra ID" : "—"}</td>
              <td>{t.user_count}</td>
              <td>{t.customer_count}</td>
              <td>
                <span className={`type-badge ${t.is_active ? "type-compliance" : "type-historisch"}`}>
                  {t.is_active ? "Aktiv" : "Deaktiviert"}
                </span>
              </td>
              <td style={{ whiteSpace: "nowrap" }}>
                <button className="text-button" onClick={() => openEdit(t)}>Bearbeiten</button>{" "}
                <button className="text-button" onClick={() => toggleActive(t)}>
                  {t.is_active ? "Deaktivieren" : "Aktivieren"}
                </button>
              </td>
            </tr>
          ))}
          {tenants.length === 0 && (
            <tr><td colSpan={8} style={{ color: "var(--text-muted)" }}>Noch keine Organisationen.</td></tr>
          )}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="section-title" style={{ margin: 0 }}>
                {editing ? "Organisation bearbeiten" : "Neue Organisation"}
              </div>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>

            <div className="form-field">
              <label className="form-label">Name</label>
              <input className="text-input" value={form.name}
                placeholder="z. B. Stadtwerke Musterstadt GmbH"
                onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="form-field">
              <label className="form-label">Slug</label>
              <input className="text-input" value={form.slug}
                placeholder={form.name ? slugify(form.name) : "stadtwerke-musterstadt"}
                onChange={(e) => setForm({ ...form, slug: e.target.value })} />
              <div className="field-hint">Leer lassen, um ihn aus dem Namen abzuleiten.</div>
            </div>
            <div className="form-field">
              <label className="form-label">E-Mail-Domain</label>
              <input className="text-input" value={form.email_domain}
                placeholder="stadtwerke-musterstadt.de"
                onChange={(e) => setForm({ ...form, email_domain: e.target.value })} />
              <div className="field-hint">
                Steuert, welcher Organisation ein Login zugeordnet wird — und ob im
                zweiten Login-Schritt SSO oder ein Passwort-Feld erscheint.
              </div>
            </div>
            <div className="form-field">
              <label className="form-label">SSO-Anbieter</label>
              <select className="text-input" value={form.sso_provider}
                onChange={(e) => setForm({ ...form, sso_provider: e.target.value })}>
                {SSO_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            {form.sso_provider === "entra" && (
              <div className="form-field">
                <label className="form-label">Entra-Verzeichnis-ID</label>
                <input className="text-input" value={form.sso_tenant_id}
                  placeholder="00000000-0000-0000-0000-000000000000"
                  onChange={(e) => setForm({ ...form, sso_tenant_id: e.target.value })} />
                <div className="field-hint">
                  Wird beim Login gegen das Token geprüft — ohne sie käme auch ein
                  Konto aus einem fremden Verzeichnis herein.
                </div>
              </div>
            )}

            {error && <div className="form-error">{error}</div>}
            <button className="recalc-button" onClick={save} disabled={saving}>
              {saving ? "Speichere …" : "Speichern"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
