import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import GlassCard from "../components/GlassCard";
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

  return (
    <GlassCard title={t("progressTitle")} subtitle={t("progressSubtitle")}>
      <p className="muted">
        {t("taskLabel")}: {taskId}
      </p>
      <p>
        {t("status")}: {task?.status ?? t("loading")}
      </p>
      <div className="progress-wrap">
        <div className="progress-bar" style={{ width: `${((task?.progress ?? 0) * 100).toFixed(1)}%` }} />
      </div>
      <p className="muted">{task?.message}</p>
      {task?.error ? <p className="error">{task.error}</p> : null}
    </GlassCard>
  );
}
