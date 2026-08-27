import { useEffect, useState, useCallback } from "react";
import { api } from "./api/client";
import type {
  AssessmentCreate,
  AssessmentDetail,
  AssessmentHistoryItem,
  CurrentUser,
  HeatmapRow,
  RegulatoryVersion,
} from "./types";
import { ScoreCard } from "./components/ScoreCard";
import { Heatmap } from "./components/Heatmap";
import { FindingsList } from "./components/FindingsList";
import { ProcessGroupAccordion } from "./components/ProcessGroupAccordion";
import { ProfileForm, type ProfileDraft } from "./components/ProfileForm";
import { AssessmentStartStep } from "./components/AssessmentStartStep";
import { AssessmentContextBar } from "./components/AssessmentContextBar";
import { ProfileSummary } from "./components/ProfileSummary";
import { Sidebar, type Step } from "./components/Sidebar";
import { Login } from "./components/Login";
import { MarketCommunicationTriangle } from "./components/MarketCommunicationTriangle";
import { Import } from "./components/Import";
import { Roadmap } from "./components/Roadmap";
import { RegulatoryImpactView } from "./components/RegulatoryImpactView";

// Seiten, die Zahlen eines konkreten Assessments zeigen -- nur dort steht die
// Kontextzeile. Bewusst NICHT im Kundenprofil (dort waehlt man das Assessment ja
// gerade aus) und nicht im internen Formatänderungen-Bereich.
const ASSESSMENT_SCOPED_STEPS: Step[] = [
  "uebersicht",
  "marktkommunikation",
  "assessment",
  "import",
  "ergebnisse",
  "regulatorischerstand",
];

export default function App() {
  const [authChecked, setAuthChecked] = useState(false);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const authenticated = currentUser?.authenticated === true;

  const loadCurrentUser = useCallback(async () => {
    try {
      setCurrentUser(await api.me());
    } catch {
      setCurrentUser({ authenticated: false });
    } finally {
      setAuthChecked(true);
    }
  }, []);

  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  const handleLogout = async () => {
    try {
      const res = await api.logout();
      // Bei SSO-Nutzern zusaetzlich die Sitzung beim Anbieter beenden -- sonst waere
      // der naechste Login-Versuch sofort wieder automatisch angemeldet.
      if (res.sso_logout_url) {
        window.location.href = res.sso_logout_url;
        return;
      }
    } catch {
      // Auch bei einem Fehler lokal abmelden -- der Cookie kann serverseitig
      // bereits abgelaufen sein.
    }
    window.location.reload();
  };

  // Ein Kunde kann mehrere Assessments haben (Abschnitt 12.3). Gehalten wird bewusst
  // nur das GERADE geladene plus die Liste -- kein Cache mehrerer Details, weil
  // Nachladen billig ist und ein Cache veraltete Staende riskieren wuerde.
  // Zwischenstand aus dem Profil-Schritt: der Kunde wird erst zusammen mit der
  // Versionswahl angelegt, damit ein Abbruch im zweiten Schritt keine kundenlosen
  // Datensaetze hinterlaesst.
  const [profileDraft, setProfileDraft] = useState<ProfileDraft | null>(null);
  const [customerId, setCustomerId] = useState<number | null>(null);
  const [assessments, setAssessments] = useState<AssessmentHistoryItem[]>([]);
  const [versions, setVersions] = useState<RegulatoryVersion[]>([]);
  const [assessmentId, setAssessmentId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [step, setStep] = useState<Step>("kundenprofil");

  const [detail, setDetail] = useState<AssessmentDetail | null>(null);
  const [heatmap, setHeatmap] = useState<HeatmapRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (id: number) => {
    setLoading(true);
    try {
      const [d, calc] = await Promise.all([api.getAssessment(id), api.calculate(id)]);
      setDetail(d);
      setHeatmap(calc.heatmap);
      setDetail((prev) => (prev ? { ...prev, score: calc.score, findings: calc.findings } : prev));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (assessmentId !== null) load(assessmentId);
  }, [assessmentId, load]);

  const loadHistory = useCallback(async (custId: number) => {
    try {
      const items = await api.listCustomerAssessments(custId);
      setAssessments(items);
      return items;
    } catch (e) {
      setError((e as Error).message);
      return [];
    }
  }, []);

  // Erst nach dem Login laden -- vorher antwortet die API mit 401 und die Liste
  // bliebe dauerhaft leer, weil der Effect ohne diese Abhaengigkeit nie erneut liefe.
  useEffect(() => {
    if (!authenticated) return;
    api.listRegulatoryVersions()
      .then(setVersions)
      .catch((e) => setError((e as Error).message));
  }, [authenticated]);

  const handleStartFromDraft = async (regulatoryVersionId: number) => {
    if (!profileDraft) return;
    const payload: AssessmentCreate = {
      customer_name: profileDraft.customer_name,
      market_role: profileDraft.market_role,
      customer_segments: "slp", // im MVP fest
      business_scenario: "lieferantenwechsel",
      regulatory_version_id: regulatoryVersionId,
    };
    setCreating(true);
    setCreateError(null);
    try {
      const created = await api.createAssessment(payload);
      setProfileDraft(null);
      setCustomerId(created.customer_id);
      setAssessmentId(created.id);
      await loadHistory(created.customer_id);
      setStep("uebersicht");
    } catch (e) {
      setCreateError((e as Error).message);
    } finally {
      setCreating(false);
    }
  };

  /** Weiteres Assessment fuer den bereits erfassten Kunden -- fragt nur die Version ab. */
  const handleCreateForCustomer = async (regulatoryVersionId: number) => {
    if (customerId === null) return;
    setCreating(true);
    setError(null);
    try {
      const created = await api.createAssessmentForCustomer(customerId, regulatoryVersionId);
      await loadHistory(customerId);
      setAssessmentId(created.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setCreating(false);
    }
  };

  const resetToWizard = () => {
    setProfileDraft(null);
    setCustomerId(null);
    setAssessments([]);
    setAssessmentId(null);
    setDetail(null);
    setHeatmap([]);
    setError(null);
    setStep("kundenprofil");
  };

  const handleRequirementChange = (id: number, patch: Record<string, string>) => {
    if (!detail) return;
    setDetail({
      ...detail,
      requirement_statuses: detail.requirement_statuses.map((ar) =>
        ar.id === id ? { ...ar, ...patch } : ar
      ),
    });
    api.updateRequirementStatus(id, patch).catch((e) => setError((e as Error).message));
  };

  const recalculate = async () => {
    if (assessmentId === null) return;
    setRecalculating(true);
    try {
      const calc = await api.calculate(assessmentId);
      setHeatmap(calc.heatmap);
      setDetail((prev) => (prev ? { ...prev, score: calc.score, findings: calc.findings } : prev));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRecalculating(false);
    }
  };

  const renderContent = () => {
    if (step === "roadmap") {
      return <Roadmap />;
    }

    if (step === "kundenprofil") {
      if (detail) {
        return (
          <ProfileSummary
            assessment={detail.assessment}
            onEdit={resetToWizard}
            history={assessments}
            activeAssessmentId={assessmentId}
            onSelectAssessment={setAssessmentId}
            versions={versions}
            onCreateAssessment={handleCreateForCustomer}
            creating={creating}
          />
        );
      }
      // Zwei Schritte: erst Kundendaten, dann die Version des Assessments.
      if (profileDraft) {
        return (
          <AssessmentStartStep
            customerName={profileDraft.customer_name}
            versions={versions}
            onStart={handleStartFromDraft}
            onBack={() => { setProfileDraft(null); setCreateError(null); }}
            submitting={creating}
            error={createError}
          />
        );
      }
      return <ProfileForm onSubmit={setProfileDraft} submitting={false} error={createError} />;
    }

    if (loading) return <div className="loading">Lade Assessment …</div>;
    if (error) return <div className="error">Fehler: {error}</div>;
    if (!detail) return <div className="loading">Bitte zuerst ein Kundenprofil anlegen.</div>;

    const { score, findings, process_groups, requirement_statuses } = detail;

    if (step === "import") {
      return (
        <Import
          assessmentId={detail.assessment.id}
          onImported={() => { if (assessmentId !== null) load(assessmentId); }}
        />
      );
    }

    if (step === "marktkommunikation") {
      return (
        <div>
          <div className="section-title" style={{ marginTop: 0 }}>Marktkommunikation</div>
          <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 520, marginBottom: 20 }}>
            Marktpartner beim Lieferantenwechsel. Klick auf eine Verbindung zeigt die
            Nachrichten und die Abdeckung im Assessment.
          </p>
          <MarketCommunicationTriangle
            processGroups={process_groups}
            requirementStatuses={requirement_statuses}
            onOpenAssessment={() => setStep("assessment")}
          />
        </div>
      );
    }

    if (step === "assessment") {
      return (
        <div>
          <div
            className="section-title"
            style={{ marginTop: 0, display: "flex", justifyContent: "space-between", alignItems: "center" }}
          >
            <span>Assessment nach Prozessgruppe</span>
            <button className="recalc-button" onClick={recalculate} disabled={recalculating}>
              {recalculating ? "Berechne …" : "Bewertung neu berechnen"}
            </button>
          </div>
          {process_groups.map((group, i) => (
            <ProcessGroupAccordion
              key={group.id}
              group={group}
              requirementStatuses={requirement_statuses}
              onChange={handleRequirementChange}
              defaultOpen={i === 0}
            />
          ))}
        </div>
      );
    }

    // Kundensicht auf die bevorstehende Formatumstellung (Abschnitt 11.5). Das
    // Kanban-Board bleibt bewusst im Admin-Bereich -- hier nur, was den Kunden
    // betrifft: Stichtag, betroffene Anforderungen, Empfehlungen, Score-Delta.
    if (step === "regulatorischerstand") {
      return <RegulatoryImpactView assessmentId={detail.assessment.id} />;
    }

    if (step === "ergebnisse") {
      return (
        <div>
          <div className="section-title" style={{ marginTop: 0 }}>Findings</div>
          <FindingsList findings={findings} />
        </div>
      );
    }

    // uebersicht
    const complianceItem = assessments.find((a) => a.assessment_type === "compliance");
    const activeItem = assessments.find((a) => a.id === assessmentId);
    return (
      <div>
        {/* Standard ist das Compliance-Assessment. Gibt es keines, wird das benannt --
            statt kommentarlos irgendein anderes anzuzeigen (Abschnitt 12.5). */}
        {assessments.length > 0 && !complianceItem && (
          <div className="notice-warning">
            Kein aktuelles Compliance-Assessment vorhanden — euer letztes Assessment
            {activeItem?.regulatory_version_name ? ` (gegen ${activeItem.regulatory_version_name})` : ""}
            {/* Ohne Compliance-Assessment gibt es zwei Faelle: der Stand ist ueberholt,
                ODER es wurde nur gegen einen kuenftigen Stand gemessen. "historisch"
                waere im zweiten Fall schlicht falsch. */}
            {activeItem?.assessment_type === "readiness"
              ? " misst gegen einen Stand, der erst künftig gilt."
              : " ist mittlerweile historisch."}
          </div>
        )}
        {activeItem && activeItem.assessment_type !== "compliance" && complianceItem && (
          <div className="notice-info">
            Angezeigt wird ein {activeItem.assessment_type === "readiness" ? "Readiness" : "historisches"}-Assessment
            {activeItem.regulatory_version_name ? ` (gegen ${activeItem.regulatory_version_name})` : ""}.
            {" "}
            <button className="link-button" onClick={() => setAssessmentId(complianceItem.id)}>
              Zum aktuellen Compliance-Assessment wechseln
            </button>
          </div>
        )}
        {score && (
          <>
            <div className="score-grid">
              <ScoreCard label="Regulatorischer Abdeckungsgrad" value={score.regulatory_coverage} />
              <ScoreCard label="Qualitätsgrad" value={score.quality_grade} />
            </div>
            <div className="subscore-grid">
              <div className="subscore">
                <div className="subscore-label">Implementierungsqualität</div>
                <div className="subscore-value">{score.implementation_quality.toFixed(1)}%</div>
              </div>
              <div className="subscore">
                <div className="subscore-label">Testqualität</div>
                <div className="subscore-value">{score.test_quality.toFixed(1)}%</div>
              </div>
              <div className="subscore">
                <div className="subscore-label">Nachweisqualität</div>
                <div className="subscore-value">{score.evidence_quality.toFixed(1)}%</div>
              </div>
              <div className="subscore">
                <div className="subscore-label">Aktualität</div>
                <div className="subscore-value">{score.actuality.toFixed(1)}%</div>
              </div>
            </div>
          </>
        )}
        <div className="section-title">Heatmap je Prozessgruppe</div>
        <Heatmap rows={heatmap} />
      </div>
    );
  };

  if (!authChecked) return <div className="loading">Lade …</div>;
  if (!authenticated) return <Login onSuccess={loadCurrentUser} />;

  return (
    <div className="app-shell">
      <Sidebar
        active={step}
        onSelect={setStep}
        hasAssessment={detail !== null}
        activeVersion={versions.find((v) => v.is_active) ?? null}
        currentUser={currentUser}
        onLogout={handleLogout}
      />
      <div className="app-content">
        {detail && ASSESSMENT_SCOPED_STEPS.includes(step) && (
          <AssessmentContextBar assessment={detail.assessment} />
        )}
        {renderContent()}
      </div>
    </div>
  );
}
