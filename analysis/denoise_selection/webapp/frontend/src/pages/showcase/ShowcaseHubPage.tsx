import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import RackPanel from "../../components/RackPanel";
import StatusBadge from "../../components/StatusBadge";
import MiniScope from "../../components/showcase/MiniScope";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import { useI18n } from "../../i18n/I18nContext";
import { getHistory } from "../../lib/api";
import { abbreviateTaskId, isDeepfilterMismatch } from "../../lib/pipelineUtils";
import type { TaskItem } from "../../types/api";

type Props = {
  taskId: string;
};

const bentoLinks = [
  { to: "/showcase/algorithms", code: "MOD-S01", accent: "s01", titleKey: "showcaseAlgoTitle" as const, descKey: "showcaseAlgoDesc" as const, freq: 1 },
  { to: "/showcase/pipeline", code: "MOD-S02", accent: "s02", titleKey: "showcasePipelineTitle" as const, descKey: "showcasePipelineDesc" as const, freq: 1.4 },
  { to: "/showcase/monitor", code: "MOD-S03", accent: "s03", titleKey: "showcaseMonitorTitle" as const, descKey: "showcaseMonitorDesc" as const, freq: 1.1 },
  { to: "/showcase/cinema", code: "MOD-S04", accent: "s04", titleKey: "showcaseCinemaTitle" as const, descKey: "showcaseCinemaDesc" as const, freq: 1.25 },
] as const;

export default function ShowcaseHubPage({ taskId }: Props) {
  const { t } = useI18n();
  const [task, setTask] = useState<TaskItem | null>(null);

  useEffect(() => {
    if (!taskId) {
      setTask(null);
      return;
    }
    getHistory()
      .then((items) => setTask(items.find((x) => x.task_id === taskId) ?? null))
      .catch(() => setTask(null));
  }, [taskId]);

  const method = (task?.settings?.method as string) ?? "—";
  const route = task?.route?.join(" → ") ?? "—";
  const mismatch = task
    ? isDeepfilterMismatch(method, task.route ?? [], task.reason ?? "")
    : false;

  return (
    <div className="showcase-page stagger-fast">
      <ShowcaseSubNav />
      <ShowcasePageHeader
        variant="hub"
        eyebrow={t("showcaseHubEyebrow")}
        title={t("showcaseHubTitle")}
        lede={t("showcaseHubSubtitle")}
        actions={
          <>
            <Link to="/upload" className="console-cta-primary">
              {t("homeStart")}
            </Link>
            {taskId ? (
              <>
                <Link to="/showcase/monitor" className="console-cta-ghost">
                  {t("showcaseExploreMonitor")}
                </Link>
                <Link to="/showcase/pipeline" className="console-cta-ghost">
                  {t("showcaseExplorePipeline")}
                </Link>
              </>
            ) : null}
            <Link to="/overview" className="console-cta-ghost">
              {t("showcaseBackWorkbench")}
            </Link>
          </>
        }
      />
      <div className="showcase-hub-grid">
        <RackPanel
          moduleId="MOD-S00"
          channel="NAV"
          led={taskId ? "active" : "idle"}
          title={t("showcaseTaskLcdTitle")}
          className="showcase-hub-nav-panel"
        >
          {taskId && task ? (
            <div className={`showcase-task-lcd-grid ${mismatch ? "showcase-task-lcd-mismatch" : ""}`}>
              <div className="showcase-task-lcd-row">
                <span className="showcase-task-lcd-label">ID</span>
                <code title={task.task_id}>{abbreviateTaskId(task.task_id)}</code>
                <StatusBadge status={task.status} />
              </div>
              <div className="showcase-task-lcd-row">
                <span className="showcase-task-lcd-label">{t("methodLabel")}</span>
                <span>{method}</span>
              </div>
              <div className="showcase-task-lcd-row">
                <span className="showcase-task-lcd-label">{t("routeLabel")}</span>
                <span className="showcase-task-lcd-route">{route}</span>
              </div>
            </div>
          ) : (
            <div className="showcase-task-lcd">{t("showcaseNoTask")}</div>
          )}
          {!taskId ? (
            <p className="muted showcase-hub-upload-hint">
              <Link to="/upload">{t("goUpload")}</Link>
            </p>
          ) : null}
        </RackPanel>
        <div className="showcase-bento">
          {bentoLinks.map((b) => (
            <Link key={b.to} to={b.to} className={`showcase-bento-card showcase-bento-card--${b.accent}`}>
              <span className="showcase-bento-code">{b.code}</span>
              <h4>{t(b.titleKey)}</h4>
              <p>{t(b.descKey)}</p>
              <MiniScope height={40} freqMul={b.freq} variant={b.accent === "s02" ? "amber" : "signal"} />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
