import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import GlassButton from "../../components/GlassButton";
import RackPanel from "../../components/RackPanel";
import LcdTicker from "../../components/showcase/LcdTicker";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import { useI18n } from "../../i18n/I18nContext";
import { getMetrics, getTask } from "../../lib/api";
import { DEMO_METRICS } from "../../lib/showcasePresets";
import type { MetricsPayload } from "../../types/api";

type Props = {
  taskId: string;
};

function radarPct(v: number | undefined, max: number): number {
  if (v == null || Number.isNaN(v)) return 12;
  return Math.max(8, Math.min(92, (v / max) * 100));
}

export default function MetricsTheaterPage({ taskId }: Props) {
  const { t } = useI18n();
  const [metrics, setMetrics] = useState<MetricsPayload | null>(null);
  const [sim, setSim] = useState(false);
  const [loading, setLoading] = useState(!!taskId);

  useEffect(() => {
    if (!taskId) {
      setMetrics(DEMO_METRICS as MetricsPayload);
      setSim(true);
      setLoading(false);
      return;
    }
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const task = await getTask(taskId);
        if (cancelled) return;
        if (task.status !== "completed") {
          setMetrics(DEMO_METRICS as MetricsPayload);
          setSim(true);
          return;
        }
        const m = await getMetrics(taskId);
        if (!cancelled) {
          setMetrics(m);
          setSim(false);
        }
      } catch {
        if (!cancelled) {
          setMetrics(DEMO_METRICS as MetricsPayload);
          setSim(true);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [taskId]);

  const m = metrics;
  const radar = useMemo(
    () => ({
      snr: radarPct(m?.snr_db?.delta, 12),
      clarity: radarPct(m?.snr_db?.output_est, 20),
      residual: radarPct(1 - (m?.rms?.residual ?? 0) * 120, 1),
      stability: 68,
      complexity: 42,
    }),
    [m],
  );

  const tickerLines = m
    ? [
        `IN ${m.snr_db?.input_est?.toFixed(2) ?? "—"} dB`,
        `OUT ${m.snr_db?.output_est?.toFixed(2) ?? "—"} dB`,
        `Δ ${m.snr_db?.delta?.toFixed(2) ?? "—"} dB`,
        m.method ?? "",
        m.route?.join(" → ") ?? "",
      ]
    : [];

  return (
    <div className="showcase-page showcase-page-inner stagger-fast">
      <ShowcaseSubNav />
      <ShowcasePageHeader
        variant="inner"
        moduleId="MOD-S06"
        channel="METRICS"
        title={t("metricsTheaterTitle")}
        subtitle={t("metricsTheaterSubtitle")}
        badge={sim ? <span className="showcase-sim-badge">{t("showcaseSimBadge")}</span> : <span className="showcase-live-badge">{t("showcaseLiveBadge")}</span>}
      />
      <RackPanel moduleId="MOD-S06" channel="METRICS" led={loading ? "processing" : "active"} className={loading ? "metrics-theater-loading" : ""}>
        <div className="metrics-theater-grid">
          <div className="metrics-theater-hero">
            <div className="metrics-big">
              <span className="metrics-big-label">{t("inputSnr")}</span>
              <strong>{m?.snr_db?.input_est?.toFixed(2) ?? "—"}</strong>
            </div>
            <div className="metrics-big metrics-big-signal">
              <span className="metrics-big-label">{t("deltaSnr")}</span>
              <strong>{m?.snr_db?.delta?.toFixed(2) ?? "—"}</strong>
            </div>
            <div className="metrics-big">
              <span className="metrics-big-label">{t("outputSnr")}</span>
              <strong>{m?.snr_db?.output_est?.toFixed(2) ?? "—"}</strong>
            </div>
            <div className="metrics-mini-row">
              <div>
                <span>{t("residualRms")}</span>
                <strong>{m?.rms?.residual?.toFixed(6) ?? "—"}</strong>
              </div>
              <div>
                <span>{t("kurtosis")}</span>
                <strong>{m?.residual_stats?.kurtosis?.toFixed(3) ?? "—"}</strong>
              </div>
            </div>
          </div>
          <div>
            <div
              className="metrics-radar"
              style={
                {
                  "--r-snr": `${radar.snr}%`,
                  "--r-clarity": `${radar.clarity}%`,
                  "--r-residual": `${radar.residual}%`,
                  "--r-stability": `${radar.stability}%`,
                  "--r-complexity": `${radar.complexity}%`,
                } as CSSProperties
              }
              aria-hidden="true"
            />
            <ul className="metrics-radar-legend">
              <li>{t("metricsRadarSnr")}</li>
              <li>{t("metricsRadarClarity")}</li>
              <li>{t("metricsRadarResidual")}</li>
            </ul>
          </div>
          <div className="metrics-theater-side">
            <div className="metrics-monitor-unit" aria-hidden="true">
              <span className="metrics-monitor-cup" />
              <span className="metrics-monitor-bridge">ANC</span>
              <span className="metrics-monitor-cup" />
            </div>
            <p className="muted">{t("metricsTheaterListenHint")}</p>
            {taskId && !sim ? (
              <Link to="/showcase/cinema">
                <GlassButton variant="primary">{t("wayfindCinema")}</GlassButton>
              </Link>
            ) : (
              <Link to="/upload">
                <GlassButton variant="secondary">{t("homeStart")}</GlassButton>
              </Link>
            )}
          </div>
        </div>
        {tickerLines.length > 0 ? <LcdTicker lines={tickerLines} /> : null}
      </RackPanel>
    </div>
  );
}
