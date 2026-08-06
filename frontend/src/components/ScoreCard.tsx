interface Props {
  label: string;
  value: number;
}

export function ScoreCard({ label, value }: Props) {
  return (
    <div className="score-card">
      <div className="score-card-label">{label}</div>
      <div className="score-card-value">{value.toFixed(1)}%</div>
      <div className="score-card-bar">
        <div className="score-card-bar-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
