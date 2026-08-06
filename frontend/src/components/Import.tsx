import { useState } from "react";
import { api } from "../api/client";
import type { ImportSuggestion } from "../types";

type Tab = "csv" | "sap";

interface Props {
  assessmentId: number;
  onImported: () => void;
}

export function Import({ assessmentId, onImported }: Props) {
  const [tab, setTab] = useState<Tab>("csv");
  const [sourceName, setSourceName] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<ImportSuggestion[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sapForm, setSapForm] = useState({
    token_url: "", client_id: "", client_secret: "", base_url: "", api_path: "/api/test-management/v1/test-cases",
  });

  const handleCsvUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.importCsvPreview(assessmentId, file);
      setSourceName(res.source_name);
      setSuggestions(res.suggestions);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSapImport = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.importSapCloudAlmPreview(assessmentId, sapForm);
      setSourceName(res.source_name);
      setSuggestions(res.suggestions);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!suggestions || !sourceName) return;
    setLoading(true);
    setError(null);
    try {
      const items = suggestions
        .filter((s) => s.requirement_id !== null)
        .map((s) => ({
          requirement_id: s.requirement_id as number,
          implementation_status: s.implementation_status,
          test_status: s.test_status,
          result_status: s.result_status,
        }));
      await api.importConfirm(assessmentId, sourceName, items);
      setSuggestions(null);
      setSourceName(null);
      onImported();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Testfälle importieren</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 540, marginBottom: 18 }}>
        Import bleibt Selbstauskunft — Atlas schlägt eine Zuordnung zu unserem Requirement-Katalog
        vor, du prüfst und bestätigst sie, bevor sie in den Score einfließt.
      </p>

      <div style={{ display: "flex", gap: 8, marginBottom: 18 }}>
        <button className={`text-button ${tab === "csv" ? "active-pill" : ""}`}
          style={tab === "csv" ? { background: "var(--accent-light)", borderColor: "var(--accent)" } : undefined}
          onClick={() => { setTab("csv"); setSuggestions(null); setError(null); }}>
          CSV-Datei
        </button>
        <button className={`text-button ${tab === "sap" ? "active-pill" : ""}`}
          style={tab === "sap" ? { background: "var(--accent-light)", borderColor: "var(--accent)" } : undefined}
          onClick={() => { setTab("sap"); setSuggestions(null); setError(null); }}>
          SAP Cloud ALM
        </button>
      </div>

      {!suggestions && tab === "csv" && (
        <div className="import-panel">
          <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 12 }}>
            Spalten: <code>Titel</code> (oder <code>Title</code>/<code>Testfall</code>) und optional{" "}
            <code>Status</code> (z.B. „passed"/„failed"). Semikolon oder Komma als Trenner.
          </p>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => e.target.files?.[0] && handleCsvUpload(e.target.files[0])}
          />
        </div>
      )}

      {!suggestions && tab === "sap" && (
        <div className="import-panel">
          <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 12, maxWidth: 480 }}>
            Verbindung über den OAuth2-Client-Credentials-Flow. Zugangsdaten werden nur für diese
            Anfrage verwendet, nicht gespeichert.
          </p>
          <div className="sap-form">
            <input className="text-input" placeholder="Token-URL" value={sapForm.token_url}
              onChange={(e) => setSapForm({ ...sapForm, token_url: e.target.value })} />
            <input className="text-input" placeholder="Client ID" value={sapForm.client_id}
              onChange={(e) => setSapForm({ ...sapForm, client_id: e.target.value })} />
            <input className="text-input" type="password" placeholder="Client Secret" value={sapForm.client_secret}
              onChange={(e) => setSapForm({ ...sapForm, client_secret: e.target.value })} />
            <input className="text-input" placeholder="Base-URL (z.B. https://xyz.eu20.alm.cloud.sap)" value={sapForm.base_url}
              onChange={(e) => setSapForm({ ...sapForm, base_url: e.target.value })} />
            <input className="text-input" placeholder="API-Pfad" value={sapForm.api_path}
              onChange={(e) => setSapForm({ ...sapForm, api_path: e.target.value })} />
          </div>
          <button className="recalc-button" onClick={handleSapImport} disabled={loading} style={{ marginTop: 12 }}>
            {loading ? "Verbinde …" : "Verbinden & Testfälle laden"}
          </button>
        </div>
      )}

      {loading && !suggestions && <div className="loading">Lade …</div>}
      {error && <div className="error" style={{ padding: "16px 0" }}>Fehler: {error}</div>}

      {suggestions && (
        <div>
          <div style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 10 }}>
            {suggestions.length} Zeilen erkannt, {suggestions.filter((s) => s.requirement_id !== null).length} davon
            automatisch zugeordnet. Nicht zugeordnete Zeilen werden beim Bestätigen ignoriert.
          </div>
          <table className="import-table">
            <thead>
              <tr>
                <th>Import-Zeile</th>
                <th>Status</th>
                <th>Vorschlag</th>
                <th>Konfidenz</th>
              </tr>
            </thead>
            <tbody>
              {suggestions.map((s) => (
                <tr key={s.row_index} className={s.requirement_id === null ? "import-row-unmatched" : ""}>
                  <td>{s.raw_title}</td>
                  <td>{s.raw_status || "—"}</td>
                  <td>
                    {s.requirement_code ? (
                      <span>
                        <span className="pi-number" style={{ marginRight: 6 }}>{s.requirement_code}</span>
                        {s.requirement_title}
                      </span>
                    ) : (
                      <span style={{ color: "var(--text-muted)" }}>kein Treffer</span>
                    )}
                  </td>
                  <td>{s.requirement_id !== null ? `${Math.round(s.confidence * 100)}%` : "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
            <button className="recalc-button" onClick={handleConfirm} disabled={loading}>
              {loading ? "Übernehme …" : "Bestätigen und übernehmen"}
            </button>
            <button className="text-button" onClick={() => { setSuggestions(null); setSourceName(null); }}>
              Abbrechen
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
