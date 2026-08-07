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
}

export function Sidebar({ active, onSelect, hasAssessment }: Props) {
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
          GeLi Gas 2.0
          <br />
          UTILMD Gas G1.1
          <br />
          Konsultationsfassung
          <br />
          01.08.2025
        </div>
      </div>
    </div>
  );
}
