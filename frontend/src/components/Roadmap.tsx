interface StageDef {
  badge: "LIVE" | "GEPLANT";
  title: string;
  description: string;
}

const STAGES: StageDef[] = [
  {
    badge: "LIVE",
    title: "Stufe 1 — Selbstauskunft",
    description: "Status manuell im Dashboard pflegen, per CSV-Import oder über SAP Cloud ALM. Sofort einsatzbereit, keine tiefe Integration nötig.",
  },
  {
    badge: "GEPLANT",
    title: "Stufe 2 — Nachrichten-Simulation",
    description: "Echte UTILMD-Nachricht hochladen, Atlas prüft Format & Pflichtfelder automatisch — erste objektive Prüfung statt Behauptung.",
  },
  {
    badge: "GEPLANT",
    title: "Stufe 3 — Prozessketten-Prüfung",
    description: "Mehrere Nachrichten in Folge, Referenzkonsistenz über die Kette und bewusste Fehlerfälle werden automatisch geprüft.",
  },
];

export function Roadmap() {
  return (
    <div>
      <div className="section-title" style={{ marginTop: 0 }}>Reifegradmodell</div>
      <p style={{ color: "var(--text-muted)", fontSize: 13, maxWidth: 520, marginBottom: 22 }}>
        Atlas wächst mit eurem Reifegrad mit — von Selbstauskunft bis zur automatisierten
        Prüfung, ganz ohne Zugriff auf eure Backend-Systeme.
      </p>
      <div className="roadmap-grid">
        {STAGES.map((s) => (
          <div key={s.title} className={`roadmap-card ${s.badge === "LIVE" ? "roadmap-card-live" : ""}`}>
            <span className={`roadmap-badge ${s.badge === "LIVE" ? "roadmap-badge-live" : ""}`}>
              {s.badge === "LIVE" ? "● LIVE" : "GEPLANT"}
            </span>
            <div className="roadmap-card-title">{s.title}</div>
            <div className="roadmap-card-desc">{s.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
