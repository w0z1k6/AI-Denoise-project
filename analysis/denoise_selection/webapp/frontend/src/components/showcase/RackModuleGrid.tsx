import type { RackLed } from "../RackPanel";

export type RackModuleItem = {
  id: string;
  value: string;
  label: string;
  hint?: string;
  led?: RackLed;
  selected?: boolean;
  onSelect?: () => void;
};

type Props = {
  modules: RackModuleItem[];
};

export default function RackModuleGrid({ modules }: Props) {
  return (
    <div className="rack-module-grid">
      {modules.map((m) => (
        <button
          key={m.id}
          type="button"
          className={`rack-module-card ${m.selected ? "is-selected" : ""}`}
          onClick={m.onSelect}
        >
          <div className="rack-module-card-head">
            <code>{m.value}</code>
            <span className={`rack-led rack-led-${m.led ?? (m.selected ? "active" : "idle")}`} aria-hidden="true" />
          </div>
          <strong>{m.label}</strong>
          {m.hint ? <span className="rack-module-hint">{m.hint}</span> : null}
        </button>
      ))}
    </div>
  );
}
