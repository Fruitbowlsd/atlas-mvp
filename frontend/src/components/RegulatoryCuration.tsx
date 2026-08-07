import { useEffect, useState } from "react";
import { api } from "../api/client";
import type {
  ChangeCategory,
  ProcessGroup,
  RegulatoryChange,
  RegulatoryVersion,
  RiskLevel,
} from "../types";

const CATEGORY_LABELS: Record<ChangeCategory, string> = {
  neuer_prozess: "Neuer Prozess",
  neues_pflichtfeld: "Neues Pflichtfeld",
  neuer_code: "Neuer Code",
  neue_qualitaetsregel: "Neue Qualitätsregel",
  neuer_testfall: "Neuer Testfall",
};

const RISK_OPTIONS: RiskLevel[] = ["hoch", "mittel", "niedrig"];

const EMPTY_CHANGE_FORM = {
  title: "",
  description: "",
  category: "neues_pflichtfeld" as ChangeCategory,
  process_group_id: "" as number | "",
  pi_id: "" as number | "",
  risk: "mittel" as RiskLevel,
  effort: "mittel" as RiskLevel,
  source_url: "",
};

export function RegulatoryCuration() {
  const [versions, setVersions] = useState<RegulatoryVersion[]>([]);
  const [processGroups, setProcessGroups] = useState<ProcessGroup[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(null);
  const [changes, setChanges] = useState<RegulatoryChange[]>([]);

  const [showNewVersionForm, setShowNewVersionForm] = useState(false);
  const [newVersionName, setNewVersionName] = useState("");
  const [newVersionValidFrom, setNewVersionValidFrom] = useState("");

  const [changeForm, setChangeForm] = useState(EMPTY_CHANGE_FORM);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadVersions = async () => {
    const vs = await api.listRegulatoryVersions();
    setVersions(vs);
    // Standardmäßig die erste NICHT-aktive Version vorauswählen -- Kuration findet
    // fuer die kommende, noch nicht ausgerollte Version statt.
    if (selectedVersionId === null && vs.length > 0) {
      const upcoming = vs.find((v) => !v.is_active);
      setSelectedVersionId((upcoming ?? vs[vs.length - 1]).id);
    }
  };

  useEffect(() => {
    loadVersions();
    api.listProcessGroups().then(setProcessGroups);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedVersionId === null) return;
    api.listRegulatoryChanges(selectedVersionId).then(setChanges).catch((e) => setError((e as Error).message));
  }, [selectedVersionId]);

  const handleCreateVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newVersionName.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const created = await api.createRegulatoryVersion({
        name: newVersionName.trim(),
        valid_from: newVersionValidFrom ? new Date(newVersionValidFrom).toISOString() : null,
        predecessor_version_id: versions.find((v) => v.is_active)?.id ?? null,
      });
      setNewVersionName("");
      setNewVersionValidFrom("");
      setShowNewVersionForm(false);
      await loadVersions();
      setSelectedVersionId(created.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!changeForm.title.trim() || selectedVersionId === null) return;
    setLoading(true);
    setError(null);
    try {
      const created = await api.createRegulatoryChange({
        title: changeForm.title.trim(),
        description: changeForm.description.trim() || null,
        category: changeForm.category,
        process_group_id: changeForm.process_group_id === "" ? null : Number(changeForm.process_group_id),
        pi_id: changeForm.pi_id === "" ? null : Number(changeForm.pi_id),
        risk: changeForm.risk,
        effort: changeForm.effort,
        source_url: changeForm.source_url.trim() || null,
        regulatory_version_id: selectedVersionId,
      });
      setChanges((prev) => [created, ...prev]);
      setChangeForm(EMPTY_CHANGE_FORM);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const toggleStatus = async (change: RegulatoryChange) => {
    const nextStatus = change.status === "entwurf" ? "veroeffentlicht" : "entwurf";
    try {
      const updated = await api.updateRegulatoryChange(change.id, { status: nextStatus });
      setChanges((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleAnalyzeDiff = async () => {
    if (selectedVersionId === null) return;
    setAnalyzing(true);
    setError(null);
    try {
      const created = await api.analyzeDiff(selectedVersionId);
      setChanges((prev) => [...created, ...prev]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setAnalyzing(false);
    }
  };

  const deleteChange = async (id: number) => {
    try {
      await api.deleteRegulatoryChange(id);
      setChanges((prev) => prev.filter((c) => c.id !== id));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const availablePis = processGroups.find((g) => g.id === changeForm.process_group_id)?.pis ?? [];
  const selectedVersion = versions.find((v) => v.id === selectedVersionId) ?? null;

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Regulatory Intelligence — Kuration (intern)</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 560, marginBottom: 20 }}>
        Rein interne Ansicht, nicht Teil der Kunden-Sicht. Erfasse regulatorische Änderungen einer
        bevorstehenden Formatumstellung manuell — Status „Entwurf" bis du sie veröffentlichst.
      </p>

      <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 8, flexWrap: "wrap" }}>
        <label className="form-label" style={{ marginBottom: 0 }}>Version:</label>
        <select
          className="text-input"
          style={{ width: "auto", minWidth: 280 }}
          value={selectedVersionId ?? ""}
          onChange={(e) => setSelectedVersionId(Number(e.target.value))}
        >
          {versions.map((v) => (
            <option key={v.id} value={v.id}>
              {v.name} {v.is_active ? "(aktiv)" : "(Entwurf)"}
            </option>
          ))}
        </select>
        <button type="button" className="text-button" onClick={() => setShowNewVersionForm((s) => !s)}>
          + neue Version
        </button>
      </div>

      {selectedVersion && (
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18, flexWrap: "wrap" }}>
          <div style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
            {selectedVersion.status === "final" ? "Final" : "Konsultation"}
            {selectedVersion.valid_from && ` · gültig ab ${new Date(selectedVersion.valid_from).toLocaleDateString("de-DE")}`}
          </div>
          {selectedVersion.predecessor_version_id !== null && (
            <button type="button" className="text-button" onClick={handleAnalyzeDiff} disabled={analyzing}>
              {analyzing ? "Analysiere Diff …" : "🤖 KI-Vorschläge aus Diff generieren"}
            </button>
          )}
        </div>
      )}

      {showNewVersionForm && (
        <form onSubmit={handleCreateVersion} className="import-panel" style={{ marginBottom: 24, maxWidth: 480 }}>
          <div className="form-field">
            <label className="form-label">Name der neuen Version</label>
            <input
              className="text-input"
              placeholder="z. B. GeLi Gas 2.1 / UTILMD Gas G1.2 (Entwurf Okt. 2027)"
              value={newVersionName}
              onChange={(e) => setNewVersionName(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label className="form-label">Gültig ab (optional)</label>
            <input
              type="date"
              className="text-input"
              value={newVersionValidFrom}
              onChange={(e) => setNewVersionValidFrom(e.target.value)}
            />
          </div>
          <button type="submit" className="recalc-button" disabled={loading}>
            {loading ? "Wird angelegt …" : "Version anlegen"}
          </button>
        </form>
      )}

      {selectedVersionId !== null && (
        <form onSubmit={handleCreateChange} className="import-panel" style={{ marginBottom: 24 }}>
          <div className="form-field">
            <label className="form-label">Titel</label>
            <input
              className="text-input"
              placeholder="z. B. Neues Pflichtfeld Bilanzierungsbrennwert in UTILMD"
              value={changeForm.title}
              onChange={(e) => setChangeForm({ ...changeForm, title: e.target.value })}
            />
          </div>
          <div className="form-field">
            <label className="form-label">Beschreibung</label>
            <textarea
              className="text-input"
              rows={3}
              value={changeForm.description}
              onChange={(e) => setChangeForm({ ...changeForm, description: e.target.value })}
            />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
            <div className="form-field">
              <label className="form-label">Kategorie</label>
              <select
                className="text-input"
                value={changeForm.category}
                onChange={(e) => setChangeForm({ ...changeForm, category: e.target.value as ChangeCategory })}
              >
                {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label className="form-label">Risiko</label>
              <select
                className="text-input"
                value={changeForm.risk}
                onChange={(e) => setChangeForm({ ...changeForm, risk: e.target.value as RiskLevel })}
              >
                {RISK_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label className="form-label">Aufwand</label>
              <select
                className="text-input"
                value={changeForm.effort}
                onChange={(e) => setChangeForm({ ...changeForm, effort: e.target.value as RiskLevel })}
              >
                {RISK_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <div className="form-field">
              <label className="form-label">Prozessgruppe (optional)</label>
              <select
                className="text-input"
                value={changeForm.process_group_id}
                onChange={(e) => setChangeForm({
                  ...changeForm,
                  process_group_id: e.target.value === "" ? "" : Number(e.target.value),
                  pi_id: "",
                })}
              >
                <option value="">— keine —</option>
                {processGroups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label className="form-label">PI (optional)</label>
              <select
                className="text-input"
                value={changeForm.pi_id}
                onChange={(e) => setChangeForm({ ...changeForm, pi_id: e.target.value === "" ? "" : Number(e.target.value) })}
                disabled={availablePis.length === 0}
              >
                <option value="">— keine —</option>
                {availablePis.map((pi) => (
                  <option key={pi.id} value={pi.id}>{pi.pi_number} — {pi.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-field">
            <label className="form-label">Quelle (URL, optional)</label>
            <input
              className="text-input"
              placeholder="https://www.bundesnetzagentur.de/…"
              value={changeForm.source_url}
              onChange={(e) => setChangeForm({ ...changeForm, source_url: e.target.value })}
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="recalc-button" disabled={loading}>
            {loading ? "Wird angelegt …" : "Änderung als Entwurf anlegen"}
          </button>
        </form>
      )}

      <div className="findings-list">
        {changes.length === 0 && (
          <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
            Noch keine Änderungen für diese Version erfasst.
          </div>
        )}
        {changes.map((c) => (
          <div key={c.id} className={`finding-card ${c.risk}`}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10 }}>
              <div style={{ flex: 1 }}>
                <div className="finding-title">{c.title}</div>
                <div style={{ display: "flex", gap: 6, margin: "4px 0 8px", flexWrap: "wrap" }}>
                  <span className={`crit-badge crit-${c.risk}`}>Risiko: {c.risk}</span>
                  <span className="crit-badge crit-niedrig">Aufwand: {c.effort}</span>
                  <span className="crit-badge crit-niedrig">{CATEGORY_LABELS[c.category]}</span>
                  <span className={`roadmap-badge ${c.status === "veroeffentlicht" ? "roadmap-badge-live" : ""}`}>
                    {c.status === "veroeffentlicht" ? "● VERÖFFENTLICHT" : "ENTWURF"}
                  </span>
                  {c.origin === "ki_vorschlag" && (
                    <span className="crit-badge crit-mittel">KI-Vorschlag</span>
                  )}
                </div>
                {c.description && <div className="finding-desc">{c.description}</div>}
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                  {c.process_group_name && <span>{c.process_group_name} </span>}
                  {c.pi_number && <span className="pi-number" style={{ marginRight: 6 }}>{c.pi_number}</span>}
                  {c.source_url && (
                    <a href={c.source_url} target="_blank" rel="noreferrer" style={{ color: "var(--accent-dark)" }}>
                      Quelle
                    </a>
                  )}
                </div>
              </div>
              <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                <button className="text-button" onClick={() => toggleStatus(c)}>
                  {c.status === "entwurf" ? "Veröffentlichen" : "Zurück zu Entwurf"}
                </button>
                <button className="text-button" onClick={() => deleteChange(c.id)}>Löschen</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
