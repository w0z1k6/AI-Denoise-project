import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import RackPanel from "../components/RackPanel";
import { useI18n } from "../i18n/I18nContext";
import { getTask } from "../lib/api";
import type { TaskStatusResponse } from "../types/api";

type Props = {
  taskId: string;
};

export default function TaskProgressPage({ taskId }: Props) {
  const nav = useNavigate();
  const { t } = useI18n();
  const [task, setTask] = useState<TaskStatusResponse | null>(null);

  useEffect(() => {
    if (!taskId) return;
    const poll = async () => {
      const tsk = await getTask(taskId);
      setTask(tsk);
      if (tsk.status === "completed") nav("/overview");
    };
    poll();
    const timer = setInterval(poll, 1500);
    return () => clearInterval(timer);
  }, [taskId, nav]);

  if (!taskId)
    return (
      <p className="muted">
        {t("noTask")}
        <Link to="/upload">{t("goUpload")}</Link>
      </p>
    );

  const pct = Math.round((task?.progress ?? 0) * 100);
  const processing = task?.status === "processing" || task?.status === "queued";
  const led = task?.status === "failed" ? "error" : processing ? "processing" : task?.status === "completed" ? "active" : "idle";

  return (
    <RackPanel
      moduleId="MOD-08"
      channel="PROC"
      led={led}
      title={t("progressTitle")}
      subtitle={t("progressSubtitle")}
      className={processing ? "progress-processing" : ""}
    >
      <p className="muted" role="status" aria-live="polite">
        {t("status")}: {task?.status ?? t("loading")}
      </p>
      <div className="progress-vu-wrap">
        <div className="progress-vu-label">
          <span>VU</span>
          <strong>{pct}%</strong>
        </div>
        <div className="progress-wrap progress-vu-bar">
          <div className="progress-bar" style={{ width: `${pct}%` }} />
        </div>
      </div>
      {task?.message ? (
        <p className="muted" role="status" aria-live="polite">
          {task.message}
        </p>
      ) : null}
      {task?.error ? (
        <p className="error" role="alert">
          {task.error}
        </p>
      ) : null}
    </RackPanel>
  );
}
