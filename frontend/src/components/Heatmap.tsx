import type { HeatmapRow } from "../types";

export function Heatmap({ rows }: { rows: HeatmapRow[] }) {
  return (
    <table className="heatmap-table">
      <thead>
        <tr>
          <th>Prozessgruppe</th>
          <th>Abdeckung</th>
          <th>Qualität</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.process_group}>
            <td>{r.process_group}</td>
            <td>{r.coverage.toFixed(1)}%</td>
            <td>{r.quality.toFixed(1)}%</td>
            <td>
              <span className={`status-dot ${r.status}`} />
              {r.status === "gruen" ? "Grün" : r.status === "gelb" ? "Gelb" : "Rot"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
