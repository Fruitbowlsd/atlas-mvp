import { useEffect, useState } from "react";
import type { RegulatoryVersion } from "../types";
import { RegulatoryVersionPicker } from "./RegulatoryVersionPicker";

interface Props {
  customerName: string;
  versions: RegulatoryVersion[];
  onStart: (regulatoryVersionId: number) => void;
  onBack: () => void;
  submitting: boolean;
  error: string | null;
}

/** Eigener Schritt nach dem Kundenprofil: die regulatorische Version ist eine
 *  Eigenschaft des Assessments, nicht des Kunden -- deshalb bewusst getrennt vom
 *  Profil-Wizard. Fuer bestehende Kunden wird derselbe Schritt aus der
 *  Assessment-Historie heraus erreicht, ohne die Profildaten erneut abzufragen. */
export function AssessmentStartStep({ customerName, versions, onStart, onBack, submitting, error }: Props) {
  const [versionId, setVersionId] = useState<number | null>(null);

  useEffect(() => {
    if (versionId !== null || versions.length === 0) return;
    // Vorbelegt ist der heute geltende Stand -- der haeufigste Fall.
    const current = versions.find((v) => v.is_active) ?? versions[0];
    setVersionId(current.id);
  }, [versions, versionId]);

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
        Assessment starten für <strong>{customerName}</strong>. Der gewählte Stand
        bestimmt, gegen welchen Anforderungskatalog gemessen wird.
      </p>

      <div className="form-field">
        <label className="form-label">Gegen welchen Stand soll Atlas Ihre Qualität messen?</label>
        <RegulatoryVersionPicker versions={versions} selectedId={versionId} onSelect={setVersionId} />
      </div>

      {error && <div className="form-error">{error}</div>}

      <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
        <button
          className="recalc-button"
          disabled={submitting || versionId === null}
          onClick={() => versionId !== null && onStart(versionId)}
        >
          {submitting ? "Wird angelegt …" : "Assessment starten"}
        </button>
        <button className="text-button" onClick={onBack} disabled={submitting}>
          Zurück
        </button>
      </div>
    </div>
  );
}
