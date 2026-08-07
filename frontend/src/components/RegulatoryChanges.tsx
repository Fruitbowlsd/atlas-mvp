import { useEffect, useState } from "react";
import { api } from "../api/client";
import type {
  ChangeCategory,
  ChangeStatus,
  ProcessGroup,
  RegulatoryChange,
  RegulatoryVersion,
  RiskLevel,
} from "../types";
import { RegulatoryImpactView } from "./RegulatoryImpactView";

const CATEGORY_LABELS: Record<ChangeCategory, string> = {
  neuer_prozess: "Neuer Prozess",
  neues_pflichtfeld: "Neues Pflichtfeld",
  neuer_code: "Neuer Code",
  neue_qualitaetsregel: "Neue Qualitätsregel",
  neuer_testfall: "Neuer Testfall",
};

const RISK_OPTIONS: RiskLevel[] = ["hoch", "mittel", "niedrig"];

const COLUMNS: { status: ChangeStatus; title: string }[] = [
  { status: "zu_pruefen", title: "Zu prüfen" },
  { status: "entwurf", title: "Entwurf" },
  { status: "veroeffentlicht", title: "Veröffentlicht" },
];

interface ChangeFormState {
  title: string;
  description: string;
  category: ChangeCategory;
  process_group_id: number | "";
  pi_id: number | "";
  risk: RiskLevel;
  effort: RiskLevel;
  source_url: string;
  status: ChangeStatus;
}

const EMPTY_FORM: ChangeFormState = {
  title: "",
  description: "",
  category: "neues_pflichtfeld",
  process_group_id: "",
  pi_id: "",
  risk: "mittel",
  effort: "mittel",
  source_url: "",
  status: "entwurf",
};

interface Props {
  assessmentId: number | null;
}

export function RegulatoryChanges({ assessmentId }: Props) {
  const [tab, setTab] = useState<"kanban" | "vorschau">("kanban");

  const [versions, setVersions] = useState<RegulatoryVersion[]>([]);
  const [processGroups, setProcessGroups] = useState<ProcessGroup[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(null);
  const [changes, setChanges] = useState<RegulatoryChange[]>([]);

  const [showNewVersionForm, setShowNewVersionForm] = useState(false);
  const [newVersionName, setNewVersionName] = useState("");
  const [newVersionValidFrom, setNewVersionValidFrom] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null); // null = neue Karte
  const [form, setForm] = useState<ChangeFormState>(EMPTY_FORM);

  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadVersions = async (preferId?: number) => {
    const vs = await api.listRegulatoryVersions();
    setVersions(vs);
    if (preferId !== undefined) {
      setSelectedVersionId(preferId);
    } else if (selectedVersionId === null && vs.length > 0) {
      // Standardmäßig die erste NICHT-aktive Version -- Kuration findet fuer die
      // kommende, noch nicht ausgerollte Version statt.
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
      await loadVersions(created.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteVersion = async () => {
    if (selectedVersionId === null) return;
    const version = versions.find((v) => v.id === selectedVersionId);
    if (!version) return;
    if (!window.confirm(`Version "${version.name}" wirklich löschen? Alle zugehörigen Änderungen werden mitgelöscht.`)) return;
    setLoading(true);
    setError(null);
    try {
      await api.deleteRegulatoryVersion(selectedVersionId);
      setSelectedVersionId(null);
      await loadVersions();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
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

  const openNewCard = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setError(null);
    setModalOpen(true);
  };

  const openCard = (c: RegulatoryChange) => {
    setEditingId(c.id);
    setForm({
      title: c.title,
      description: c.description ?? "",
      category: c.category,
      process_group_id: c.process_group_id ?? "",
      pi_id: c.pi_id ?? "",
      risk: c.risk,
      effort: c.effort,
      source_url: c.source_url ?? "",
      status: c.status,
    });
    setError(null);
    setModalOpen(true);
  };

  const closeModal = () => setModalOpen(false);

  const handleSaveCard = async () => {
    if (!form.title.trim() || selectedVersionId === null) return;
    setLoading(true);
    setError(null);
    try {
      if (editingId === null) {
        const created = await api.createRegulatoryChange({
          title: form.title.trim(),
          description: form.description.trim() || null,
          category: form.category,
          process_group_id: form.process_group_id === "" ? null : Number(form.process_group_id),
          pi_id: form.pi_id === "" ? null : Number(form.pi_id),
          risk: form.risk,
          effort: form.effort,
          source_url: form.source_url.trim() || null,
          regulatory_version_id: selectedVersionId,
        });
        // Neu angelegte Karten starten serverseitig immer als "entwurf" -- falls im
        // Modal eine andere Spalte gewaehlt wurde, per Folge-Update setzen.
        const final = form.status !== "entwurf"
          ? await api.updateRegulatoryChange(created.id, { status: form.status })
          : created;
        setChanges((prev) => [final, ...prev]);
      } else {
        const updated = await api.updateRegulatoryChange(editingId, {
          title: form.title.trim(),
          description: form.description.trim() || null,
          category: form.category,
          process_group_id: form.process_group_id === "" ? null : Number(form.process_group_id),
          pi_id: form.pi_id === "" ? null : Number(form.pi_id),
          risk: form.risk,
          effort: form.effort,
          source_url: form.source_url.trim() || null,
          status: form.status,
        });
        setChanges((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
      }
      setModalOpen(false);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCard = async () => {
    if (editingId === null) return;
    if (!window.confirm("Diese Änderung wirklich löschen?")) return;
    setLoading(true);
    setError(null);
    try {
      await api.deleteRegulatoryChange(editingId);
      setChanges((prev) => prev.filter((c) => c.id !== editingId));
      setModalOpen(false);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const availablePis = processGroups.find((g) => g.id === form.process_group_id)?.pis ?? [];
  const selectedVersion = versions.find((v) => v.id === selectedVersionId) ?? null;

  const statusLabel = (status: string) => {
    if (status === "final") return "Final";
    if (status === "verbindlich") return "Verbindlich";
    return "Konsultation";
  };

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Formatänderungen</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 560, marginBottom: 20 }}>
        Interner Bereich, nicht Teil der Kunden-Sicht. Regulatorische Änderungen einer
        bevorstehenden Formatumstellung kuratieren — KI-Vorschläge prüfen, manuell
        ergänzen und veröffentlichen.
      </p>

      <div className="tab-switcher">
        <button className={`tab-button ${tab === "kanban" ? "active" : ""}`} onClick={() => setTab("kanban")}>
          Kanban-Board
        </button>
        <button className={`tab-button ${tab === "vorschau" ? "active" : ""}`} onClick={() => setTab("vorschau")}>
          Kunden-Vorschau
        </button>
      </div>

      {tab === "vorschau" ? (
        assessmentId === null ? (
          <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
            Bitte zuerst im Kundenprofil ein Assessment anlegen, um die Kunden-Vorschau
            zu sehen (zeigt, was für diesen Kunden sichtbar wäre).
          </div>
        ) : (
          <RegulatoryImpactView assessmentId={assessmentId} />
        )
      ) : (
        <>
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
            {selectedVersion && !selectedVersion.is_active && (
              <button type="button" className="text-button" onClick={handleDeleteVersion}>
                Version löschen
              </button>
            )}
          </div>

          {selectedVersion && (
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18, flexWrap: "wrap" }}>
              <div style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
                {statusLabel(selectedVersion.status)}
                {selectedVersion.valid_from && ` · gültig ab ${new Date(selectedVersion.valid_from).toLocaleDateString("de-DE")}`}
              </div>
              {selectedVersion.predecessor_version_id !== null && (
                <button type="button" className="text-button" onClick={handleAnalyzeDiff} disabled={analyzing}>
                  {analyzing ? "Analysiere Diff …" : "🤖 KI-Vorschläge aus Diff generieren"}
                </button>
              )}
              <button type="button" className="recalc-button" onClick={openNewCard} style={{ marginLeft: "auto" }}>
                + Neue Änderung
              </button>
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

          {error && <div className="form-error">{error}</div>}

          {selectedVersionId !== null && (
            <div className="kanban-board">
              {COLUMNS.map((col) => {
                const cards = changes.filter((c) => c.status === col.status);
                return (
                  <div className="kanban-column" key={col.status}>
                    <div className="kanban-column-header">
                      <span className="kanban-column-title">{col.title}</span>
                      <span className="kanban-column-count">{cards.length}</span>
                    </div>
                    <div className="kanban-cards">
                      {cards.length === 0 && <div className="kanban-empty">Keine Einträge</div>}
                      {cards.map((c) => (
                        <button key={c.id} className="kanban-card" onClick={() => openCard(c)}>
                          <div className="kanban-card-title">{c.title}</div>
                          <div className="kanban-card-badges">
                            <span className={`risk-badge risk-${c.risk}`}>{c.risk}</span>
                            <span className="risk-badge risk-niedrig">{CATEGORY_LABELS[c.category]}</span>
                            {c.origin === "ki_vorschlag" && <span className="risk-badge risk-mittel">🤖 KI</span>}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="section-title" style={{ margin: 0 }}>
                {editingId === null ? "Neue Änderung" : "Änderung bearbeiten"}
              </div>
              <button className="modal-close" onClick={closeModal} aria-label="Schließen">×</button>
            </div>

            <div className="form-field">
              <label className="form-label">Titel</label>
              <input
                className="text-input"
                placeholder="z. B. Neues Pflichtfeld Bilanzierungsbrennwert in UTILMD"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </div>
            <div className="form-field">
              <label className="form-label">Beschreibung</label>
              <textarea
                className="text-input"
                rows={3}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
              <div className="form-field">
                <label className="form-label">Kategorie</label>
                <select className="text-input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value as ChangeCategory })}>
                  {Object.entries(CATEGORY_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </div>
              <div className="form-field">
                <label className="form-label">Risiko</label>
                <select className="text-input" value={form.risk} onChange={(e) => setForm({ ...form, risk: e.target.value as RiskLevel })}>
                  {RISK_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div className="form-field">
                <label className="form-label">Aufwand</label>
                <select className="text-input" value={form.effort} onChange={(e) => setForm({ ...form, effort: e.target.value as RiskLevel })}>
                  {RISK_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
              <div className="form-field">
                <label className="form-label">Prozessgruppe (optional)</label>
                <select
                  className="text-input"
                  value={form.process_group_id}
                  onChange={(e) => setForm({
                    ...form,
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
                  value={form.pi_id}
                  onChange={(e) => setForm({ ...form, pi_id: e.target.value === "" ? "" : Number(e.target.value) })}
                  disabled={availablePis.length === 0}
                >
                  <option value="">— keine —</option>
                  {availablePis.map((pi) => <option key={pi.id} value={pi.id}>{pi.pi_number} — {pi.name}</option>)}
                </select>
              </div>
            </div>
            <div className="form-field">
              <label className="form-label">Quelle (URL, optional)</label>
              <input
                className="text-input"
                placeholder="https://www.bundesnetzagentur.de/…"
                value={form.source_url}
                onChange={(e) => setForm({ ...form, source_url: e.target.value })}
              />
            </div>
            <div className="form-field">
              <label className="form-label">Status (Spalte)</label>
              <select className="text-input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as ChangeStatus })}>
                {COLUMNS.map((c) => <option key={c.status} value={c.status}>{c.title}</option>)}
              </select>
            </div>

            {error && <div className="form-error">{error}</div>}

            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button className="recalc-button" onClick={handleSaveCard} disabled={loading}>
                {loading ? "Speichere …" : "Speichern"}
              </button>
              {editingId !== null && (
                <button className="text-button" onClick={handleDeleteCard}>Löschen</button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
