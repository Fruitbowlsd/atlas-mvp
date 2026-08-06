import type { AssessmentOut } from "../types";

const ROLE_LABEL: Record<string, string> = {
  lieferant: "Lieferant",
  grund_ersatzversorger: "Grund- und Ersatzversorger",
  beides: "Lieferant sowie Grund- und Ersatzversorger",
};

export function ProfileSummary({ assessment, onEdit }: { assessment: AssessmentOut; onEdit: () => void }) {
  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Kundenprofil</div>
      <div className="profile-summary-card">
        <div className="profile-summary-row"><span>Unternehmen</span><strong>{assessment.customer_name}</strong></div>
        <div className="profile-summary-row"><span>Marktrolle</span><strong>{assessment.market_role ? ROLE_LABEL[assessment.market_role] : "—"}</strong></div>
        <div className="profile-summary-row"><span>Sparte</span><strong>Gas</strong></div>
        <div className="profile-summary-row"><span>Kundensegment</span><strong>{assessment.customer_segments.split(",").map((s) => s.toUpperCase()).join(" & ")}</strong></div>
        <div className="profile-summary-row"><span>Geschäftsprozess</span><strong>Lieferantenwechsel</strong></div>
      </div>
      <button className="text-button" onClick={onEdit} style={{ marginTop: 14 }}>
        Neues Profil / anderes Unternehmen
      </button>
    </div>
  );
}
