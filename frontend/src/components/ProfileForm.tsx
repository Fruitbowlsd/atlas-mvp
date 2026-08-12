import { useState } from "react";
import type { MarketRole } from "../types";

/** Reine Kundendaten -- die regulatorische Version gehoert bewusst NICHT hierher:
 *  Unternehmen/Marktrolle sind Eigenschaften des Kunden, die Version dagegen eine
 *  Eigenschaft des einzelnen Assessments. Sie wird im Folgeschritt abgefragt. */
export interface ProfileDraft {
  customer_name: string;
  market_role: MarketRole;
}

interface Props {
  onSubmit: (draft: ProfileDraft) => void;
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
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName.trim()) {
      setValidationError("Bitte einen Unternehmensnamen angeben.");
      return;
    }
    setValidationError(null);
    onSubmit({ customer_name: customerName.trim(), market_role: marketRole });
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
        Zuerst das Unternehmen erfassen — im nächsten Schritt wählt ihr, gegen
        welchen regulatorischen Stand bewertet werden soll.
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
          {submitting ? "Weiter …" : "Weiter zur Auswahl des Stands"}
        </button>
      </form>
    </div>
  );
}
