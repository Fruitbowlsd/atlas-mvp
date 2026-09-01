import { useState } from "react";
import type { MarketRole, Sector, Segment } from "../types";

/** Reine Kundendaten -- die regulatorische Version gehoert bewusst NICHT hierher:
 *  Unternehmen/Marktrolle sind Eigenschaften des Kunden, die Version dagegen eine
 *  Eigenschaft des einzelnen Assessments. Sie wird im Folgeschritt abgefragt. */
export interface ProfileDraft {
  customer_name: string;
  market_role: MarketRole;
  sector: Sector;
  /** Mehrfachauswahl, wird als CSV-Menge uebertragen (Abschnitt 14.2). */
  segments: Segment[];
}

interface Props {
  onSubmit: (draft: ProfileDraft) => void;
  submitting: boolean;
  error: string | null;
  /** Organisation des angemeldeten Nutzers. Belegt das Unternehmensfeld vor. */
  tenantName: string | null;
}

const ROLE_OPTIONS: { value: MarketRole; label: string }[] = [
  { value: "lieferant", label: "Lieferant" },
  { value: "grund_ersatzversorger", label: "Grund- und Ersatzversorger" },
  { value: "beides", label: "Lieferant sowie Grund- und Ersatzversorger" },
  { value: "netzbetreiber", label: "Netzbetreiber" },
  { value: "messstellenbetreiber", label: "Messstellenbetreiber" },
  { value: "bilanzkreisverantwortlicher", label: "Bilanzkreisverantwortlicher" },
];

const WAERME_HINWEIS =
  "Für Wärmeversorgung gibt es keine regulierten Marktkommunikationsprozesse " +
  "im Sinne der BNetzA-Mitteilungen. Atlas unterstützt aktuell Gas und Strom.";

const SECTOR_OPTIONS: { value: Sector; label: string }[] = [
  { value: "gas", label: "Gas" },
  { value: "strom", label: "Strom" },
];

const SEGMENT_OPTIONS: { value: Segment; label: string; hint?: string }[] = [
  { value: "slp", label: "SLP – Standardlastprofil (Kleinverbraucher)" },
  { value: "rlm", label: "RLM – Registrierende Leistungsmessung (Großverbraucher)" },
  {
    value: "imsys",
    label: "iMSys – Intelligentes Messsystem / Smart Meter",
    hint: "Smart-Meter-Rollout — relevant für Strom, zunehmend auch für Gas ab 2025.",
  },
  { value: "tlp", label: "TLP – Tagesband-Lastprofil (Sonderfall)" },
];

export function ProfileForm({ onSubmit, submitting, error, tenantName }: Props) {
  // Bewusst nur als Startwert, nicht als laufende Kopplung an tenantName: sobald der
  // Nutzer den Namen angepasst hat -- etwa fuer eine Tochtergesellschaft -- darf ein
  // spaeteres Neuladen der Sitzung seine Eingabe nicht wieder ueberschreiben.
  // Der Wizard wird erst nach der Anmeldung gerendert, der Name steht hier also bereits.
  const [customerName, setCustomerName] = useState(tenantName ?? "");
  const [marketRole, setMarketRole] = useState<MarketRole>("lieferant");
  const [sector, setSector] = useState<Sector>("gas");
  const [segments, setSegments] = useState<Segment[]>(["slp"]);
  const [validationError, setValidationError] = useState<string | null>(null);

  const toggleSegment = (value: Segment) =>
    setSegments((prev) =>
      prev.includes(value) ? prev.filter((s) => s !== value) : [...prev, value]
    );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName.trim()) {
      setValidationError("Bitte einen Unternehmensnamen angeben.");
      return;
    }
    if (segments.length === 0) {
      setValidationError("Bitte mindestens ein Kundensegment auswählen.");
      return;
    }
    setValidationError(null);
    onSubmit({
      customer_name: customerName.trim(),
      market_role: marketRole,
      sector,
      segments,
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
          {/* Nur solange der vorbelegte Wert unveraendert ist: hat der Nutzer einen
              anderen Namen eingetragen, erklaert der Hinweis nichts mehr. */}
          {tenantName && customerName === tenantName && (
            <p className="form-hint">
              Vorbelegt aus deiner Organisation. Du kannst den Namen anpassen.
            </p>
          )}
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
          <label className="form-label">Welche Sparte betreiben Sie?</label>
          <div className="radio-group">
            {SECTOR_OPTIONS.map((opt) => (
              <label key={opt.value} className="radio-option">
                <input
                  type="radio"
                  name="sector"
                  checked={sector === opt.value}
                  onChange={() => setSector(opt.value)}
                />
                {opt.label}
              </label>
            ))}
            {/* Waerme steht bewusst da, aber deaktiviert: die Frage kommt
                verlaesslich, und eine sichtbare Begruendung ist hilfreicher als
                eine fehlende Option. Auswaehlbar waere sie irrefuehrend -- das
                Datenmodell kennt nur Gas und Strom. */}
            <label className="radio-option radio-option-disabled" title={WAERME_HINWEIS}>
              <input type="radio" name="sector" disabled />
              Wärme
              <span className="option-note">nicht reguliert</span>
            </label>
          </div>
          <p className="form-hint">{WAERME_HINWEIS}</p>
        </div>

        <div className="form-field">
          <label className="form-label">Welche Kundensegmente beliefern/betreiben Sie?</label>
          <div className="checkbox-group">
            {SEGMENT_OPTIONS.map((opt) => (
              <label key={opt.value} className="checkbox-option">
                <input
                  type="checkbox"
                  checked={segments.includes(opt.value)}
                  onChange={() => toggleSegment(opt.value)}
                />
                {opt.label}
              </label>
            ))}
          </div>
          <p className="form-hint">
            Mehrfachauswahl möglich. {SEGMENT_OPTIONS.find((o) => o.value === "imsys")?.hint}
          </p>
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
