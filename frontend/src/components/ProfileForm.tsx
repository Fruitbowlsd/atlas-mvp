import { useState } from "react";
import type { MarketRole, Sector, Segment } from "../types";

/** Reine Kundendaten -- die regulatorische Version gehoert bewusst NICHT hierher:
 *  Unternehmen/Marktrolle sind Eigenschaften des Kunden, die Version dagegen eine
 *  Eigenschaft des einzelnen Assessments. Sie wird im Folgeschritt abgefragt. */
export interface ProfileDraft {
  customer_name: string;
  market_role: MarketRole;
  /** Mehrfachauswahl -- Stadtwerke betreiben oft beide Sparten (Issue #16). */
  sectors: Sector[];
  /** Segmente je Sparte. Getrennt, weil sie sich unterscheiden: iMSys gibt es
   *  im Gas-Markt noch nicht als eigenes Segment. */
  segmentsGas: Segment[];
  segmentsStrom: Segment[];
}

interface Props {
  onSubmit: (draft: ProfileDraft) => void;
  submitting: boolean;
  error: string | null;
  /** Organisation des angemeldeten Nutzers. Belegt das Unternehmensfeld vor. */
  tenantName: string | null;
}

const ROLE_OPTIONS: { value: MarketRole; label: string; disabled?: boolean; note?: string }[] = [
  { value: "lieferant", label: "Lieferant" },
  { value: "beides", label: "Lieferant sowie Grund- und Ersatzversorger" },
  { value: "netzbetreiber", label: "Netzbetreiber" },
  { value: "messstellenbetreiber", label: "Messstellenbetreiber" },
  {
    value: "bilanzkreisverantwortlicher",
    label: "Bilanzkreisverantwortlicher",
    disabled: true,
    note: "Wird in einer späteren Version von Atlas unterstützt.",
  },
];

// "Grund- und Ersatzversorger" steht bewusst nicht mehr allein zur Wahl: das ist
// eine Unterrolle von Lieferant, keine eigene Marktrolle. Im Backend bleibt der
// Wert gueltig, damit bestehende Kunden mit dieser Angabe weiter korrekt
// angezeigt werden.

/** "Gas und Strom" ist eine eigene, exklusive Auswahl und keine Kombination aus
 *  zwei Haken. Vorher waren beim Klick darauf alle drei Kaestchen markiert, was
 *  aussah, als waere dreimal dasselbe gewaehlt. Gespeichert wird weiterhin die
 *  Spartenmenge -- "gas_und_strom" existiert nur in der Oberflaeche und loest
 *  sich beim Absenden in beide Sparten auf. Ein eigener gespeicherter Wert waere
 *  eine zweite Schreibweise fuer denselben Zustand. */
type SectorChoice = "gas" | "strom" | "gas_und_strom";

const SECTOR_CHOICES: { value: SectorChoice; label: string }[] = [
  { value: "gas", label: "Gas" },
  { value: "strom", label: "Strom" },
  { value: "gas_und_strom", label: "Gas und Strom" },
];

const SECTORS_OF: Record<SectorChoice, Sector[]> = {
  gas: ["gas"],
  strom: ["strom"],
  gas_und_strom: ["gas", "strom"],
};

/** Die Beschriftungen stehen an einer Stelle. Vorher waren SLP, RLM und TLP in
 *  beiden Sparten getrennt notiert -- die falsche TLP-Bezeichnung musste
 *  entsprechend auch zweimal korrigiert werden. */
const SEGMENT_LABELS: Record<Segment, string> = {
  slp: "SLP – Standardlastprofil (Kleinverbraucher)",
  rlm: "RLM – Registrierende Leistungsmessung (Großverbraucher)",
  imsys: "iMSys – Intelligentes Messsystem / Smart Meter (Rollout seit 2023 verpflichtend)",
  tlp: "TLP – Tagesparameterabhängiges Lastprofil (Sonderfall)",
};

/** iMSys fehlt bei Gas, weil es dort noch kein eigenes Segment ist. */
const SEGMENTS_BY_SECTOR: Record<Sector, Segment[]> = {
  gas: ["slp", "rlm", "tlp"],
  strom: ["slp", "rlm", "imsys", "tlp"],
};

const SECTOR_HEADING: Record<Sector, string> = {
  gas: "Kundensegmente Gas",
  strom: "Kundensegmente Strom",
};

export function ProfileForm({ onSubmit, submitting, error, tenantName }: Props) {
  // Bewusst nur als Startwert, nicht als laufende Kopplung an tenantName: sobald der
  // Nutzer den Namen angepasst hat -- etwa fuer eine Tochtergesellschaft -- darf ein
  // spaeteres Neuladen der Sitzung seine Eingabe nicht wieder ueberschreiben.
  // Der Wizard wird erst nach der Anmeldung gerendert, der Name steht hier also bereits.
  const [customerName, setCustomerName] = useState(tenantName ?? "");
  const [marketRole, setMarketRole] = useState<MarketRole>("lieferant");
  const [sectorChoice, setSectorChoice] = useState<SectorChoice | null>("gas");
  const [segmentsGas, setSegmentsGas] = useState<Segment[]>(["slp"]);
  const [segmentsStrom, setSegmentsStrom] = useState<Segment[]>(["slp"]);
  const [validationError, setValidationError] = useState<string | null>(null);

  const sectors = sectorChoice ? SECTORS_OF[sectorChoice] : [];

  /* Exklusiv: ein Klick auf eine andere Sparte waehlt diese und hebt die
     bisherige auf, ein Klick auf die bereits gewaehlte hebt sie auf. Bewusst
     Kaestchen und keine Radios -- Radios liessen sich nicht mehr abwaehlen, und
     "noch nichts gewaehlt" ist ein Zustand, den die Validierung abfaengt. */
  const chooseSector = (value: SectorChoice) =>
    setSectorChoice((prev) => (prev === value ? null : value));

  const toggleSegment = (sector: Sector, value: Segment) => {
    const [list, set] =
      sector === "gas" ? [segmentsGas, setSegmentsGas] : [segmentsStrom, setSegmentsStrom];
    set(list.includes(value) ? list.filter((s) => s !== value) : [...list, value]);
  };

  const segmentsFor = (sector: Sector) => (sector === "gas" ? segmentsGas : segmentsStrom);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName.trim()) {
      setValidationError("Bitte einen Unternehmensnamen angeben.");
      return;
    }
    if (!sectorChoice) {
      setValidationError("Bitte eine Sparte auswählen.");
      return;
    }
    const ohneSegment = sectors.find((sec) => segmentsFor(sec).length === 0);
    if (ohneSegment) {
      setValidationError(
        `Bitte mindestens ein Kundensegment für ${ohneSegment === "gas" ? "Gas" : "Strom"} auswählen.`
      );
      return;
    }
    setValidationError(null);
    onSubmit({
      customer_name: customerName.trim(),
      market_role: marketRole,
      sectors,
      segmentsGas,
      segmentsStrom,
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
              <label
                key={opt.value}
                className={`radio-option${opt.disabled ? " radio-option-disabled" : ""}`}
                title={opt.note}
              >
                <input
                  type="radio"
                  name="market_role"
                  checked={!opt.disabled && marketRole === opt.value}
                  disabled={opt.disabled}
                  onChange={() => setMarketRole(opt.value)}
                />
                {opt.label}
                {opt.note && <span className="option-note">später verfügbar</span>}
              </label>
            ))}
          </div>
        </div>

        <div className="form-field">
          <label className="form-label">Welche Sparte betreiben Sie?</label>
          <div className="checkbox-group">
            {SECTOR_CHOICES.map((opt) => (
              <label key={opt.value} className="checkbox-option">
                <input
                  type="checkbox"
                  checked={sectorChoice === opt.value}
                  onChange={() => chooseSector(opt.value)}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>

        <div className="form-field">
          {/* Ein Block je gewaehlter Sparte -- die Segmente unterscheiden sich,
              und eine gemeinsame Liste liesse offen, welches Haekchen fuer welche
              Sparte gilt. */}
          {sectors.map((sec) => (
            <div key={sec} className="segment-block">
              <label className="form-label">
                {sectors.length > 1
                  ? SECTOR_HEADING[sec]
                  : `Welche Kundensegmente (${sec === "gas" ? "Gas" : "Strom"}) beliefern/betreiben Sie?`}
              </label>
              <div className="checkbox-group">
                {SEGMENTS_BY_SECTOR[sec].map((seg) => (
                  <label key={seg} className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={segmentsFor(sec).includes(seg)}
                      onChange={() => toggleSegment(sec, seg)}
                    />
                    {SEGMENT_LABELS[seg]}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="form-field">
          <label className="form-label">Geschäftsprozess</label>
          <div className="fixed-value">Lieferantenwechsel</div>
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
