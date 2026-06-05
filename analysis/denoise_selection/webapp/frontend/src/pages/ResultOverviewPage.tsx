import { useEffect, useState } from "react";
import ABXTestPanel from "../components/ABXTestPanel";
import AudioComparePlayer from "../components/AudioComparePlayer";
import BookmarkList from "../components/BookmarkList";
import PipelineSummary from "../components/PipelineSummary";
import RackPanel from "../components/RackPanel";
import StatusBadge from "../components/StatusBadge";
import WaveformPanel from "../components/WaveformPanel";
import { useI18n } from "../i18n/I18nContext";
import { addBookmark, audioUrl, getAbxStats, getHistory, getMetrics, postAbx } from "../lib/api";
import { isDeepfilterMismatch } from "../lib/pipelineUtils";
import type { MetricsPayload, TaskItem } from "../types/api";

type Props = {
  taskId: string;
};

export default function ResultOverviewPage({ taskId }: Props) {
  const { t } = useI18n();
  const [metrics, setMetrics] = useState<MetricsPayload | null>(null);
  const [metricsLoading, setMetricsLoading] = useState(true);
  const [abx, setAbx] = useState({ accuracy: 0, total: 0, correct: 0 });
  const [task, setTask] = useState<TaskItem | null>(null);

  useEffect(() => {
    if (!taskId) return;
    setMetricsLoading(true);
    getMetrics(taskId)
      .then(setMetrics)
      .catch(() => setMetrics(null))
      .finally(() => setMetricsLoading(false));
    getAbxStats(taskId).then(setAbx).catch(() => undefined);
    getHistory().then((items) => setTask(items.find((x) => x.task_id === taskId) ?? null)).catch(() => undefined);
  }, [taskId]);

  if (!taskId) return <p className="muted">{t("overviewNeedTask")}</p>;

  const method = metrics?.method ?? (task?.settings?.method as string) ?? "-";
  const route = metrics?.route ?? task?.route ?? [];
  const reason = metrics?.reason ?? task?.reason ?? "";
  const status = task?.status ?? "completed";
  const mismatch = isDeepfilterMismatch(method, route, reason);
  const routeText = route.length ? route.join(" → ") : "—";

  return (
    <div className="column gap stagger overview-page">
      <RackPanel
        moduleId="MOD-01"
        channel="TASK"
        led={mismatch ? "error" : status === "completed" ? "active" : "processing"}
        alert={mismatch}
        className="task-rack-panel"
      >
        <div className="task-rack-bar">
          <div>
            <span className="section-subtitle">{t("overviewStatusTitle")}</span>
            <h3 className="section-title task-rack-filename">{task?.filename ?? taskId}</h3>
            <p className="task-rack-meta">
              {method} · {routeText}
            </p>
          </div>
          <StatusBadge status={status} />
        </div>
      </RackPanel>

      {!metricsLoading && metrics ? (
        <PipelineSummary method={method} route={route} reason={reason} />
      ) : (
        <p className="muted">{t("metricsLoading")}</p>
      )}

      <AudioComparePlayer
        originalUrl={audioUrl(taskId, "original")}
        denoisedUrl={audioUrl(taskId, "denoised")}
        residualUrl={audioUrl(taskId, "residual")}
      />
      <div className="grid2">
        <WaveformPanel title={t("waveformOriginal")} url={audioUrl(taskId, "original")} />
        <WaveformPanel title={t("waveformDenoised")} url={audioUrl(taskId, "denoised")} />
      </div>
      <ABXTestPanel
        stats={abx}
        onRecord={async (xIs, guess) => {
          const s = await postAbx(taskId, xIs, guess);
          setAbx(s);
        }}
      />
      <BookmarkList
        bookmarks={task?.bookmarks ?? []}
        onAdd={async (timeSec, note) => {
          await addBookmark(taskId, timeSec, note);
          const items = await getHistory();
          setTask(items.find((x) => x.task_id === taskId) ?? null);
        }}
      />
      <RackPanel moduleId="MOD-05" channel="METER" led="active" title={t("metricTitle")} subtitle={t("metricSubtitle")}>
        <div className="metric-readout-grid">
          <div className="metric-readout">
            <span className="metric-readout-label">{t("inputSnr")}</span>
            <span className="metric-readout-value metric-readout-value-lg">
              {metrics?.snr_db?.input_est?.toFixed(3) ?? "—"}
            </span>
          </div>
          <div className="metric-readout">
            <span className="metric-readout-label">{t("outputSnr")}</span>
            <span className="metric-readout-value metric-readout-value-lg">
              {metrics?.snr_db?.output_est?.toFixed(3) ?? "—"}
            </span>
          </div>
          <div className="metric-readout">
            <span className="metric-readout-label">{t("deltaSnr")}</span>
            <span className="metric-readout-value metric-readout-value-lg">
              {metrics?.snr_db?.delta?.toFixed(3) ?? "—"}
            </span>
          </div>
          <div className="metric-readout">
            <span className="metric-readout-label">{t("residualRms")}</span>
            <span className="metric-readout-value">{metrics?.rms?.residual?.toFixed(6) ?? "—"}</span>
          </div>
          <div className="metric-readout">
            <span className="metric-readout-label">{t("kurtosis")}</span>
            <span className="metric-readout-value">{metrics?.residual_stats?.kurtosis?.toFixed(3) ?? "—"}</span>
          </div>
          <div className="metric-readout">
            <span className="metric-readout-label">{t("methodLabel")}</span>
            <span className="metric-readout-value">{method}</span>
          </div>
          <div className="metric-readout span-2">
            <span className="metric-readout-label">{t("routeLabel")}</span>
            <span className="metric-readout-value">{routeText}</span>
          </div>
          <div className={`metric-readout span-4 ${mismatch ? "pipeline-alert" : ""}`}>
            <span className="metric-readout-label">{t("reasonLabel")}</span>
            <span className="metric-readout-value">{reason || "—"}</span>
          </div>
        </div>
      </RackPanel>
    </div>
  );
}
