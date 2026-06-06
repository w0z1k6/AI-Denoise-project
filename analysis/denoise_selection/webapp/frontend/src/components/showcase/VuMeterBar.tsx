type Props = {
  value: number;
  label?: string;
  vertical?: boolean;
  pulse?: boolean;
};

export default function VuMeterBar({ value, label, vertical = false, pulse = false }: Props) {
  const pct = Math.max(0, Math.min(100, value * 100));
  return (
    <div className={`vu-meter ${vertical ? "vu-meter-vertical" : ""} ${pulse ? "vu-meter-pulse" : ""}`}>
      {label ? <span className="vu-meter-label">{label}</span> : null}
      <div className="vu-meter-track" aria-hidden="true">
        <div className="vu-meter-fill" style={{ [vertical ? "height" : "width"]: `${pct}%` }} />
      </div>
    </div>
  );
}
