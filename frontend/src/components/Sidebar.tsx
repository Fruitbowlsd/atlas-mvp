import type { CurrentUser, RegulatoryVersion } from "../types";
import { validityLabel } from "../utils/versionLabel";

export type Step =
  | "uebersicht"
  | "kundenprofil"
  | "marktkommunikation"
  | "assessment"
  | "import"
  | "ergebnisse"
  | "roadmap"
  | "formataenderungen";

interface StepDef {
  key: Step;
  label: string;
  enabled: boolean;
}

interface Props {
  active: Step;
  onSelect: (step: Step) => void;
  hasAssessment: boolean;
  /** Der aktuell geltende regulatorische Stand. Kommt aus der Datenbank statt aus
   *  einem festen Text -- sonst gaebe es zwei Quellen fuer dieselbe Angabe, die
   *  auseinanderlaufen, sobald sich der Stand aendert. */
  activeVersion: RegulatoryVersion | null;
  currentUser: CurrentUser | null;
  onLogout: () => void;
}

const VERSION_STATUS_LABEL: Record<string, string> = {
  konsultation: "Konsultationsfassung",
  final: "Finale Fassung",
  verbindlich: "Verbindlich",
};

export function Sidebar({ active, onSelect, hasAssessment, activeVersion, currentUser, onLogout }: Props) {
  // Kundenbezogene Eintraege -- sichtbar/relevant fuer die Kunden-Sicht des MVP.
  const customerSteps: StepDef[] = [
    { key: "uebersicht", label: "Übersicht", enabled: hasAssessment },
    { key: "kundenprofil", label: "Kundenprofil", enabled: true },
    { key: "marktkommunikation", label: "Marktkommunikation", enabled: hasAssessment },
    { key: "assessment", label: "Assessment", enabled: hasAssessment },
    { key: "import", label: "Import", enabled: hasAssessment },
    { key: "ergebnisse", label: "Ergebnisse", enabled: hasAssessment },
    { key: "roadmap", label: "Roadmap", enabled: true },
  ];

  // Rein interne Bereiche -- optisch abgesetzt, nicht Teil der Kunden-Sicht.
  const internalSteps: StepDef[] = [
    { key: "formataenderungen", label: "Formatänderungen", enabled: true },
  ];

  const renderItem = (s: StepDef) => (
    <button
      key={s.key}
      className={`sidebar-item ${active === s.key ? "active" : ""} ${!s.enabled ? "disabled" : ""}`}
      onClick={() => s.enabled && onSelect(s.key)}
      disabled={!s.enabled}
    >
      {s.label}
    </button>
  );

  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">A</div>
        <div>
          <div className="sidebar-brand-name">Atlas</div>
          <div className="sidebar-brand-sub">Marktprozesse Gas</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {customerSteps.map(renderItem)}
        <div className="sidebar-divider" />
        <div className="sidebar-section-label">Intern</div>
        {internalSteps.map(renderItem)}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-title">Regulatorischer Stand</div>
        <div className="sidebar-footer-text">
          {activeVersion ? (
            <>
              {activeVersion.name}
              <br />
              {VERSION_STATUS_LABEL[activeVersion.status] ?? activeVersion.status}
              {(() => {
                const validity = validityLabel(activeVersion.name, activeVersion.valid_from);
                return validity ? (<><br />{validity}</>) : null;
              })()}
            </>
          ) : (
            "wird geladen …"
          )}
        </div>
      </div>

      {currentUser?.authenticated && (
        <div className="sidebar-user">
          <div className="sidebar-user-email" title={currentUser.email}>{currentUser.email}</div>
          <button className="sidebar-logout" onClick={onLogout}>Abmelden</button>
        </div>
      )}
    </div>
  );
}
