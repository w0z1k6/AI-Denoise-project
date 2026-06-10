type Led = "idle" | "active" | "processing";

type Props = {
  led?: Led;
  ancOn?: boolean;
  latencyMs?: number;
  className?: string;
};

export default function LiveMonitorUnit({ led = "idle", ancOn = false, latencyMs = 0, className = "" }: Props) {
  return (
    <div className={`live-monitor-unit ${ancOn ? "is-anc-on" : ""} ${className}`.trim()} role="img" aria-hidden="true">
      <div className="live-monitor-shell">
        <div className="live-monitor-band" />
        <div className="live-monitor-cavity" />
        <span className={`live-monitor-led live-monitor-led-${led}`} />
        <span className="live-monitor-label">{ancOn ? "ANC" : "REF"}</span>
      </div>
      {latencyMs > 0 ? (
        <span className="live-monitor-latency-badge mono">{latencyMs} ms</span>
      ) : (
        <span className="live-monitor-latency-badge mono live-monitor-latency-idle">—</span>
      )}
    </div>
  );
}
