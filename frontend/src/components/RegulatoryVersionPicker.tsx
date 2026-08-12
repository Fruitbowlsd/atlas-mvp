import type { RegulatoryVersion } from "../types";

interface Props {
  versions: RegulatoryVersion[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  name?: string;
}

/** Zusatzhinweis je Version -- macht sichtbar, ob man gegen den heute geltenden
 *  Stand misst oder sich auf eine kommende Umstellung vorbereitet. Bewusst aus
 *  demselben valid_from abgeleitet wie der Assessment-Typ im Backend. */
function versionHint(v: RegulatoryVersion): string {
  if (!v.valid_from) return "aktueller Stand";
  const validFrom = new Date(v.valid_from);
  if (validFrom > new Date()) {
    return `künftig · gültig ab ${validFrom.toLocaleDateString("de-DE")}`;
  }
  return `gültig seit ${validFrom.toLocaleDateString("de-DE")}`;
}

export function RegulatoryVersionPicker({ versions, selectedId, onSelect, name = "regulatory_version" }: Props) {
  if (versions.length === 0) {
    return <div className="fixed-value">Keine regulatorischen Stände verfügbar</div>;
  }

  return (
    <div className="radio-group">
      {versions.map((v) => (
        <label key={v.id} className="radio-option">
          <input
            type="radio"
            name={name}
            checked={selectedId === v.id}
            onChange={() => onSelect(v.id)}
          />
          <span>
            {v.name}
            <span className="version-hint">{versionHint(v)}</span>
          </span>
        </label>
      ))}
    </div>
  );
}
