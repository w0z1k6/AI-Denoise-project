import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import GlassButton from "../components/GlassButton";
import GlassCard from "../components/GlassCard";
import StatusBadge from "../components/StatusBadge";
import { useI18n } from "../i18n/I18nContext";
import { deleteTask, getHistory } from "../lib/api";
import type { TaskItem } from "../types/api";

type Props = {
  setTaskId: (taskId: string) => void;
};

function routeSummary(route?: string[]): string {
  if (!route?.length) return "—";
  return route.join(" → ");
}

function methodFromTask(it: TaskItem): string {
  const m = it.settings?.method;
  return typeof m === "string" ? m : "—";
}

export default function HistoryPage({ setTaskId }: Props) {
  const { t } = useI18n();
  const [items, setItems] = useState<TaskItem[]>([]);

  const reload = async () => setItems(await getHistory());
  useEffect(() => {
    reload().catch(() => undefined);
  }, []);

  return (
    <GlassCard title={t("historyTitle")} subtitle={t("historySubtitle")}>
      <div className="history-table-wrap">
        {items.length === 0 ? (
          <div className="history-empty">
            <div className="history-empty-icon" aria-hidden="true" />
            <p>{t("historyEmpty")}</p>
            <Link to="/upload">
              <GlassButton variant="primary">{t("homeStart")}</GlassButton>
            </Link>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>{t("colTask")}</th>
                <th>{t("colFile")}</th>
                <th>{t("colMethod")}</th>
                <th>{t("colRoute")}</th>
                <th>{t("colStatus")}</th>
                <th>{t("colUpdated")}</th>
                <th>{t("colAction")}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.task_id}>
                  <td>
                    <code className="history-task-id">{it.task_id}</code>
                  </td>
                  <td>{it.filename}</td>
                  <td>{methodFromTask(it)}</td>
                  <td className="history-route" title={routeSummary(it.route)}>
                    {routeSummary(it.route)}
                  </td>
                  <td>
                    <StatusBadge status={it.status} />
                  </td>
                  <td>{new Date(it.updated_at).toLocaleString()}</td>
                  <td>
                    <div className="actions">
                      <GlassButton
                        variant="secondary"
                        onClick={() => {
                          setTaskId(it.task_id);
                        }}
                      >
                        {t("select")}
                      </GlassButton>
                      <Link
                        className="glass-btn glass-btn-ghost"
                        to="/overview"
                        onClick={() => {
                          setTaskId(it.task_id);
                        }}
                      >
                        {t("open")}
                      </Link>
                      <GlassButton
                        variant="secondary"
                        onClick={async () => {
                          await deleteTask(it.task_id);
                          await reload();
                        }}
                      >
                        {t("delete")}
                      </GlassButton>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </GlassCard>
  );
}
