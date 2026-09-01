import { useState } from "react";
import type { AssessmentHistoryItem, AssessmentOut, AssessmentType, RegulatoryVersion } from "../types";
import { RegulatoryVersionPicker } from "./RegulatoryVersionPicker";

const ROLE_LABEL: Record<string, string> = {
  lieferant: "Lieferant",
  grund_ersatzversorger: "Grund- und Ersatzversorger",
  beides: "Lieferant sowie Grund- und Ersatzversorger",
  netzbetreiber: "Netzbetreiber",
  messstellenbetreiber: "Messstellenbetreiber",
  bilanzkreisverantwortlicher: "Bilanzkreisverantwortlicher",
};

const SECTOR_LABEL: Record<string, string> = { gas: "Gas", strom: "Strom" };

/* Eigene Labels statt toUpperCase(): daraus wuerde sonst "IMSYS". */
const SEGMENT_LABEL: Record<string, string> = {
  slp: "SLP",
  rlm: "RLM",
  imsys: "iMSys",
  tlp: "TLP",
};

const sectors = (csv: string | null) => (csv ?? "").split(",").filter(Boolean);

const sectorLabel = (csv: string | null) =>
  sectors(csv).map((s) => SECTOR_LABEL[s] ?? s).join(" & ") || "—";

const segmentLabel = (csv: string | null) =>
  (csv ?? "").split(",").filter(Boolean).map((s) => SEGMENT_LABEL[s] ?? s.toUpperCase()).join(" & ") || "—";

const TYPE_LABEL: Record<AssessmentType, string> = {
  readiness: "Readiness",
  compliance: "Compliance",
  historisch: "Historisch",
};

interface Props {
  assessment: AssessmentOut;
  onEdit: () => void;
  history: AssessmentHistoryItem[];
  activeAssessmentId: number | null;
  onSelectAssessment: (id: number) => void;
  versions: RegulatoryVersion[];
  onCreateAssessment: (regulatoryVersionId: number) => void;
  creating: boolean;
}

export function ProfileSummary({
  assessment,
  onEdit,
  history,
  activeAssessmentId,
  onSelectAssessment,
  versions,
  onCreateAssessment,
  creating,
}: Props) {
  const [showPicker, setShowPicker] = useState(false);
  const [newVersionId, setNewVersionId] = useState<number | null>(null);

  const handleStart = () => {
    if (newVersionId === null) return;
    onCreateAssessment(newVersionId);
    setShowPicker(false);
    setNewVersionId(null);
  };

  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Kundenprofil</div>
      <div className="profile-summary-card">
        <div className="profile-summary-row"><span>Unternehmen</span><strong>{assessment.customer_name}</strong></div>
        <div className="profile-summary-row"><span>Marktrolle</span><strong>{assessment.market_role ? ROLE_LABEL[assessment.market_role] : "—"}</strong></div>
        <div className="profile-summary-row"><span>Sparte</span><strong>{sectorLabel(assessment.sector)}</strong></div>
        {/* Je Sparte aufgeschluesselt, sobald beide betrieben werden -- die
            blosse Vereinigung liesse offen, welches Segment wozu gehoert. */}
        {sectors(assessment.sector).map((sec) => (
          <div key={sec} className="profile-summary-row">
            <span>{sectors(assessment.sector).length > 1 ? `Kundensegmente ${SECTOR_LABEL[sec] ?? sec}` : "Kundensegment"}</span>
            <strong>{segmentLabel(sec === "gas" ? assessment.segments_gas : assessment.segments_strom)}</strong>
          </div>
        ))}
        <div className="profile-summary-row"><span>Geschäftsprozess</span><strong>Lieferantenwechsel</strong></div>
      </div>
      <button className="text-button" onClick={onEdit} style={{ marginTop: 14 }}>
        Neues Profil / anderes Unternehmen
      </button>

      <div className="section-title">Assessment-Historie</div>
      <p style={{ color: "var(--text-muted)", fontSize: 12.5, marginBottom: 12, maxWidth: 560 }}>
        Ein Kunde kann gegen mehrere regulatorische Stände bewertet werden. Der Typ
        ergibt sich aus dem Stichtag der Version und ändert sich mit der Zeit von
        selbst.
      </p>

      <div className="history-list">
        {history.map((h) => (
          <button
            key={h.id}
            className={`history-row ${h.id === activeAssessmentId ? "history-row-active" : ""}`}
            onClick={() => onSelectAssessment(h.id)}
          >
            <div className="history-main">
              <div className="history-version">{h.regulatory_version_name ?? "— unbekannte Version —"}</div>
              <div className="history-meta">
                angelegt am {new Date(h.created_at).toLocaleDateString("de-DE")}
              </div>
            </div>
            <span className={`type-badge type-${h.assessment_type}`}>{TYPE_LABEL[h.assessment_type]}</span>
            <div className="history-score">
              {h.regulatory_coverage !== null ? `${h.regulatory_coverage.toFixed(1)}%` : "—"}
              <span className="history-score-label">Abdeckung</span>
            </div>
          </button>
        ))}
        {history.length === 0 && (
          <div style={{ color: "var(--text-muted)", fontSize: 13 }}>Noch keine Assessments.</div>
        )}
      </div>

      {showPicker ? (
        <div className="import-panel" style={{ marginTop: 16, maxWidth: 560 }}>
          <div className="form-field">
            <label className="form-label">Gegen welchen Stand soll gemessen werden?</label>
            <RegulatoryVersionPicker
              versions={versions}
              selectedId={newVersionId}
              onSelect={setNewVersionId}
              name="new_assessment_version"
            />
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <button className="recalc-button" onClick={handleStart} disabled={creating || newVersionId === null}>
              {creating ? "Wird angelegt …" : "Assessment starten"}
            </button>
            <button className="text-button" onClick={() => setShowPicker(false)}>Abbrechen</button>
          </div>
        </div>
      ) : (
        <button className="text-button" style={{ marginTop: 14 }} onClick={() => setShowPicker(true)}>
          + Neues Assessment für diesen Kunden starten
        </button>
      )}
    </div>
  );
}
