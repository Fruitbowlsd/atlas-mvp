import type { AssessmentOut, CurrentUser, RegulatoryVersion } from "../types";
import { validityLabel } from "../utils/versionLabel";

export type Step =
  | "uebersicht"
  | "kundenprofil"
  | "marktkommunikation"
  | "assessment"
  | "import"
  | "ergebnisse"
  | "regulatorischerstand"
  | "roadmap";

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
  /** Profil des laufenden Assessments (Abschnitt 14.2). null, solange keines
   *  geladen ist -- dann bleibt der Block aus, statt Platzhalter zu zeigen. */
  profile: AssessmentOut | null;
}

const SECTOR_LABEL: Record<string, string> = { gas: "Gas", strom: "Strom" };

const SIDEBAR_ROLE_LABEL: Record<string, string> = {
  lieferant: "Lieferant",
  grund_ersatzversorger: "Grund- und Ersatzversorger",
  beides: "Lieferant / Grund- und Ersatzversorger",
  netzbetreiber: "Netzbetreiber",
  messstellenbetreiber: "Messstellenbetreiber",
  bilanzkreisverantwortlicher: "Bilanzkreisverantwortlicher",
};

/** "Gas · SLP & RLM · Lieferant" -- kompakt genug fuer die schmale Sidebar. */
function profileLine(a: AssessmentOut): string {
  const parts = [
    a.sector ? SECTOR_LABEL[a.sector] ?? a.sector : null,
    a.customer_segments
      ? a.customer_segments.split(",").filter(Boolean).map((s) => s.toUpperCase()).join(" & ")
      : null,
    a.market_role ? SIDEBAR_ROLE_LABEL[a.market_role] ?? a.market_role : null,
  ].filter(Boolean);
  return parts.join(" · ");
}

const VERSION_STATUS_LABEL: Record<string, string> = {
  konsultation: "Konsultationsfassung",
  final: "Finale Fassung",
  verbindlich: "Verbindlich",
};

export function Sidebar({ active, onSelect, hasAssessment, activeVersion, currentUser, onLogout, profile }: Props) {
  // Kundenbezogene Eintraege -- sichtbar/relevant fuer die Kunden-Sicht des MVP.
  const customerSteps: StepDef[] = [
    { key: "uebersicht", label: "Übersicht", enabled: hasAssessment },
    { key: "kundenprofil", label: "Kundenprofil", enabled: true },
    { key: "marktkommunikation", label: "Marktkommunikation", enabled: hasAssessment },
    { key: "assessment", label: "Assessment", enabled: hasAssessment },
    { key: "import", label: "Import", enabled: hasAssessment },
    { key: "ergebnisse", label: "Ergebnisse", enabled: hasAssessment },
    { key: "regulatorischerstand", label: "Regulatorischer Stand", enabled: hasAssessment },
    { key: "roadmap", label: "Roadmap", enabled: true },
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

        {profile && (
          <>
            <div className="sidebar-footer-title sidebar-footer-title-second">Ihr Profil</div>
            <div className="sidebar-footer-text">{profileLine(profile)}</div>
          </>
        )}
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
