import { useEffect, useState } from "react";
import ABXTestPanel from "../components/ABXTestPanel";
import AudioComparePlayer from "../components/AudioComparePlayer";
import BookmarkList from "../components/BookmarkList";
import GlassCard from "../components/GlassCard";
import StatChip from "../components/StatChip";
import WaveformPanel from "../components/WaveformPanel";
import { useI18n } from "../i18n/I18nContext";
import { addBookmark, audioUrl, getAbxStats, getHistory, getMetrics, postAbx } from "../lib/api";
import type { MetricsPayload, TaskItem } from "../types/api";

type Props = {
  taskId: string;
};

export default function ResultOverviewPage({ taskId }: Props) {
  const { t } = useI18n();
  const [metrics, setMetrics] = useState<MetricsPayload | null>(null);
  const [abx, setAbx] = useState({ accuracy: 0, total: 0, correct: 0 });
  const [task, setTask] = useState<TaskItem | null>(null);

  useEffect(() => {
    if (!taskId) return;
    getMetrics(taskId).then(setMetrics).catch(() => undefined);
    getAbxStats(taskId).then(setAbx).catch(() => undefined);
    getHistory().then((items) => setTask(items.find((x) => x.task_id === taskId) ?? null)).catch(() => undefined);
  }, [taskId]);

  if (!taskId) return <p className="muted">{t("overviewNeedTask")}</p>;

  return (
    <div className="column gap stagger">
      <AudioComparePlayer originalUrl={audioUrl(taskId, "original")} denoisedUrl={audioUrl(taskId, "denoised")} residualUrl={audioUrl(taskId, "residual")} />
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
      <GlassCard title={t("metricTitle")} subtitle={t("metricSubtitle")}>
        <div className="grid3">
          <StatChip label={t("methodLabel")} value={metrics?.method ?? "-"} />
          <StatChip label={t("routeLabel")} value={metrics?.route?.join(" → ") ?? "-"} />
          <StatChip label={t("reasonLabel")} value={metrics?.reason ?? task?.reason ?? "-"} />
          <StatChip label={t("inputSnr")} value={metrics?.snr_db?.input_est?.toFixed(3) ?? "-"} />
          <StatChip label={t("outputSnr")} value={metrics?.snr_db?.output_est?.toFixed(3) ?? "-"} />
          <StatChip label={t("deltaSnr")} value={metrics?.snr_db?.delta?.toFixed(3) ?? "-"} />
          <StatChip label={t("residualRms")} value={metrics?.rms?.residual?.toFixed(6) ?? "-"} />
          <StatChip label={t("kurtosis")} value={metrics?.residual_stats?.kurtosis?.toFixed(3) ?? "-"} />
        </div>
      </GlassCard>
    </div>
  );
}
