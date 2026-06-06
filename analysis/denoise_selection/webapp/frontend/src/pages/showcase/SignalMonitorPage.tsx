import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import GlassButton from "../../components/GlassButton";
import RackPanel from "../../components/RackPanel";
import LcdTicker from "../../components/showcase/LcdTicker";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import VuMeterBar from "../../components/showcase/VuMeterBar";
import { useI18n } from "../../i18n/I18nContext";
import { getMetrics, getTask } from "../../lib/api";
import type { MetricsPayload } from "../../types/api";

type Props = {
  taskId: string;
};

function normSnr(v: number | undefined): number {
  if (v == null || Number.isNaN(v)) return 0.35;
  return Math.max(0.05, Math.min(1, (v + 5) / 25));
}

export default function SignalMonitorPage({ taskId }: Props) {
  const { t } = useI18n();
  const [metrics, setMetrics] = useState<MetricsPayload | null>(null);
  const [processing, setProcessing] = useState(false);
  const [flash, setFlash] = useState(false);
  const [present, setPresent] = useState(false);
  const [tickerKey, setTickerKey] = useState(0);
  const prevRef = useRef<string>("");

  useEffect(() => {
    if (!taskId) {
      setMetrics(null);
      setProcessing(false);
      return;
    }
    let cancelled = false;
    const load = async () => {
      try {
        const task = await getTask(taskId);
        if (cancelled) return;
        if (task.status !== "completed") {
          setProcessing(true);
          setMetrics(null);
          return;
        }
        setProcessing(false);
        const m = await getMetrics(taskId);
        if (!cancelled) setMetrics(m);
      } catch {
        if (!cancelled) {
          setProcessing(false);
          setMetrics(null);
        }
      }
    };
    load();
    const timer = setInterval(load, 2000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [taskId]);

  const snapshot = JSON.stringify(metrics ?? {});

  useEffect(() => {
    if (prevRef.current && prevRef.current !== snapshot) {
      setFlash(true);
      setTickerKey((k) => k + 1);
      const tmr = window.setTimeout(() => setFlash(false), 160);
      return () => clearTimeout(tmr);
    }
    prevRef.current = snapshot;
  }, [snapshot]);

  const cells = useMemo(() => {
    const dash = "—";
    const m = metrics;
    return [
      { label: t("inputSnr"), value: m?.snr_db?.input_est?.toFixed(3) ?? dash, vu: normSnr(m?.snr_db?.input_est) },
      { label: t("outputSnr"), value: m?.snr_db?.output_est?.toFixed(3) ?? dash, vu: normSnr(m?.snr_db?.output_est) },
      { label: t("deltaSnr"), value: m?.snr_db?.delta?.toFixed(3) ?? dash, vu: normSnr(m?.snr_db?.delta) },
      { label: t("residualRms"), value: m?.rms?.residual?.toFixed(6) ?? dash, vu: Math.min(1, (m?.rms?.residual ?? 0) * 200) },
      { label: t("kurtosis"), value: m?.residual_stats?.kurtosis?.toFixed(3) ?? dash, vu: Math.min(1, (m?.residual_stats?.kurtosis ?? 0) / 6) },
      { label: t("methodLabel"), value: m?.method ?? dash, vu: 0.5 },
      { label: t("routeLabel"), value: m?.route?.join(" → ") ?? dash, vu: 0.65 },
      { label: "SR / LEN", value: m ? `${m.sample_rate} Hz · ${m.length_sec?.toFixed(1)}s` : dash, vu: 0.4 },
    ];
  }, [metrics, t]);

  const tickerLines = metrics
    ? [
        `SR ${metrics.sample_rate}`,
        `${metrics.length_sec?.toFixed(2)}s`,
        metrics.method,
        metrics.route?.join(" → ") ?? "",
        metrics.reason ?? "",
      ]
    : [];

  if (!taskId) {
    return (
      <div className="showcase-page showcase-page-inner stagger-fast">
        <ShowcaseSubNav hidden={present} />
        <ShowcasePageHeader
          variant="inner"
          moduleId="MOD-S03"
          channel="TELEMETRY"
          title={t("showcaseMonitorTitle")}
          subtitle={t("showcaseMonitorSubtitle")}
        />
        <div className="showcase-empty showcase-empty-rack">
          <div className="history-empty-icon" aria-hidden="true" />
          <p>{t("showcaseNoTask")}</p>
          <Link to="/upload">
            <GlassButton variant="primary">{t("homeStart")}</GlassButton>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={`showcase-page showcase-page-inner stagger-fast ${present ? "showcase-monitor--present" : ""}`}>
      <ShowcaseSubNav hidden={present} />
      <ShowcasePageHeader
        variant="inner"
        moduleId="MOD-S03"
        channel="TELEMETRY"
        title={t("showcaseMonitorTitle")}
        subtitle={t("showcaseMonitorSubtitle")}
        badge={
          <GlassButton variant="ghost" onClick={() => setPresent((p) => !p)}>
            {present ? t("showcaseExitPresent") : t("showcasePresentMode")}
          </GlassButton>
        }
      />
      {processing ? (
        <p className="muted" role="status" aria-live="polite">
          {t("statusProcessing")}…
        </p>
      ) : null}
      <RackPanel moduleId="MOD-S03" channel="TELEMETRY" led={processing ? "processing" : "active"} className="rack-no-corner-led">
        <div className="monitor-grid">
          {cells.map((c) => (
            <div key={c.label} className={`monitor-cell ${flash ? "is-flash" : ""}`}>
              <span className="monitor-label">{c.label}</span>
              <div className="monitor-value">{c.value}</div>
              <VuMeterBar value={processing ? 0.45 : c.vu} pulse={processing} />
            </div>
          ))}
        </div>
        {tickerLines.length > 0 ? <LcdTicker key={tickerKey} lines={tickerLines} /> : null}
      </RackPanel>
    </div>
  );
}
