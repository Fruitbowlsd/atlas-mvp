import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AssessmentCreate, MarketRole, RegulatoryVersion } from "../types";
import { RegulatoryVersionPicker } from "./RegulatoryVersionPicker";

interface Props {
  onSubmit: (payload: AssessmentCreate) => void;
  submitting: boolean;
  error: string | null;
}

const ROLE_OPTIONS: { value: MarketRole; label: string }[] = [
  { value: "lieferant", label: "Lieferant" },
  { value: "grund_ersatzversorger", label: "Grund- und Ersatzversorger" },
  { value: "beides", label: "Lieferant sowie Grund- und Ersatzversorger" },
];

export function ProfileForm({ onSubmit, submitting, error }: Props) {
  const [customerName, setCustomerName] = useState("");
  const [marketRole, setMarketRole] = useState<MarketRole>("lieferant");
  const [versions, setVersions] = useState<RegulatoryVersion[]>([]);
  const [versionId, setVersionId] = useState<number | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    api.listRegulatoryVersions().then((vs) => {
      setVersions(vs);
      // Vorbelegt ist der heute geltende Stand -- der haeufigste Fall. Wer sich auf
      // eine kommende Umstellung vorbereitet, waehlt bewusst eine andere Version.
      const current = vs.find((v) => v.is_active) ?? vs[0];
      if (current) setVersionId(current.id);
    });
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName.trim()) {
      setValidationError("Bitte einen Unternehmensnamen angeben.");
      return;
    }
    if (versionId === null) {
      setValidationError("Bitte einen regulatorischen Stand auswählen.");
      return;
    }
    setValidationError(null);
    onSubmit({
      customer_name: customerName.trim(),
      market_role: marketRole,
      customer_segments: "slp", // im MVP fest
      business_scenario: "lieferantenwechsel",
      regulatory_version_id: versionId,
    });
  };

  return (
    <div className="profile-form-wrap">
      <div className="brand" style={{ marginBottom: 6 }}>
        <div className="brand-mark">A</div>
        <div>
          <div className="brand-name">Atlas</div>
          <div className="brand-sub">Energy Quality Assessment</div>
        </div>
      </div>
      <p style={{ color: "var(--text-muted)", fontSize: 13.5, marginBottom: 28 }}>
        Neues Assessment anlegen — die Angaben bestimmen, welche regulatorischen
        Anforderungen für dieses Unternehmen relevant sind.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label className="form-label">Unternehmen</label>
          <input
            type="text"
            className="text-input"
            placeholder="z. B. Stadtwerke Musterstadt GmbH"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
          />
        </div>

        <div className="form-field">
          <label className="form-label">Marktrolle</label>
          <div className="radio-group">
            {ROLE_OPTIONS.map((opt) => (
              <label key={opt.value} className="radio-option">
                <input
                  type="radio"
                  name="market_role"
                  checked={marketRole === opt.value}
                  onChange={() => setMarketRole(opt.value)}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>

        <div className="form-field">
          <label className="form-label">Gegen welchen Stand soll Atlas Ihre Qualität messen?</label>
          <RegulatoryVersionPicker versions={versions} selectedId={versionId} onSelect={setVersionId} />
        </div>

        <div className="form-field">
          <label className="form-label">Sparte</label>
          <div className="fixed-value">
            Gas
            <span className="fixed-hint">im MVP fest vorgegeben</span>
          </div>
        </div>

        <div className="form-field">
          <label className="form-label">Kundensegment</label>
          <div className="fixed-value">
            SLP (Standardlastprofil)
            <span className="fixed-hint">im MVP fest vorgegeben</span>
          </div>
        </div>

        <div className="form-field">
          <label className="form-label">Geschäftsprozess</label>
          <div className="fixed-value">
            Lieferantenwechsel
            <span className="fixed-hint">im MVP fest vorgegeben</span>
          </div>
        </div>

        {(validationError || error) && (
          <div className="form-error">{validationError || error}</div>
        )}

        <button type="submit" className="recalc-button" disabled={submitting} style={{ marginTop: 8 }}>
          {submitting ? "Wird angelegt …" : "Relevante Marktkommunikation ermitteln"}
        </button>
      </form>
    </div>
  );
}
