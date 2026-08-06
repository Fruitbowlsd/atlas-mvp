import { useEffect, useState, useCallback } from "react";
import { api } from "./api/client";
import type { AssessmentCreate, AssessmentDetail, HeatmapRow } from "./types";
import { ScoreCard } from "./components/ScoreCard";
import { Heatmap } from "./components/Heatmap";
import { FindingsList } from "./components/FindingsList";
import { ProcessGroupAccordion } from "./components/ProcessGroupAccordion";
import { ProfileForm } from "./components/ProfileForm";
import { ProfileSummary } from "./components/ProfileSummary";
import { Sidebar, type Step } from "./components/Sidebar";
import { Login } from "./components/Login";
import { MarketCommunicationTriangle } from "./components/MarketCommunicationTriangle";
import { Import } from "./components/Import";
import { Roadmap } from "./components/Roadmap";

export default function App() {
  const [authChecked, setAuthChecked] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    api
      .checkAuth()
      .then((r) => setAuthenticated(r.authenticated))
      .catch(() => setAuthenticated(false))
      .finally(() => setAuthChecked(true));
  }, []);

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

  const handleCreateAssessment = async (payload: AssessmentCreate) => {
    setCreating(true);
    setCreateError(null);
    try {
      const created = await api.createAssessment(payload);
      setAssessmentId(created.id);
      setStep("uebersicht");
    } catch (e) {
      setCreateError((e as Error).message);
    } finally {
      setCreating(false);
    }
  };

  const resetToWizard = () => {
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
        return <ProfileSummary assessment={detail.assessment} onEdit={resetToWizard} />;
      }
      return <ProfileForm onSubmit={handleCreateAssessment} submitting={creating} error={createError} />;
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

    if (step === "ergebnisse") {
      return (
        <div>
          <div className="section-title" style={{ marginTop: 0 }}>Findings</div>
          <FindingsList findings={findings} />
        </div>
      );
    }

    // uebersicht
    return (
      <div>
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
  if (!authenticated) return <Login onSuccess={() => setAuthenticated(true)} />;

  return (
    <div className="app-shell">
      <Sidebar active={step} onSelect={setStep} hasAssessment={detail !== null} />
      <div className="app-content">{renderContent()}</div>
    </div>
  );
}
