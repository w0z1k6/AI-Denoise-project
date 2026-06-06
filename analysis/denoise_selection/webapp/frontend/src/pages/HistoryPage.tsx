import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import GlassButton from "../components/GlassButton";
import RackPanel from "../components/RackPanel";
import StatusBadge from "../components/StatusBadge";
import { useI18n } from "../i18n/I18nContext";
import { deleteTask, getHistory } from "../lib/api";
import { abbreviateTaskId, isDeepfilterMismatch } from "../lib/pipelineUtils";
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
    <RackPanel moduleId="MOD-06" channel="LOG" led={items.length ? "active" : "idle"} title={t("historyTitle")} subtitle={t("historySubtitle")}>
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
                <th className="col-status">{t("colStatus")}</th>
                <th>{t("colUpdated")}</th>
                <th>{t("colAction")}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => {
                const method = methodFromTask(it);
                const route = it.route ?? [];
                const reason = it.reason ?? "";
                const mismatch = isDeepfilterMismatch(method, route, reason);
                const rowClass = [
                  it.status === "failed" ? "history-row-failed" : "",
                  mismatch ? "history-row-mismatch" : "",
                ]
                  .filter(Boolean)
                  .join(" ");

                return (
                  <tr key={it.task_id} className={rowClass || undefined}>
                    <td>
                      <code className="history-task-id" title={it.task_id}>
                        {abbreviateTaskId(it.task_id)}
                      </code>
                    </td>
                    <td>{it.filename}</td>
                    <td>{method}</td>
                    <td className="history-route" title={routeSummary(route)}>
                      {routeSummary(route)}
                    </td>
                    <td className="col-status">
                      <StatusBadge status={it.status} />
                    </td>
                    <td>{new Date(it.updated_at).toLocaleString()}</td>
                    <td>
                      <div className="actions">
                        <GlassButton
                          variant="ghost"
                          onClick={() => {
                            setTaskId(it.task_id);
                          }}
                        >
                          {t("select")}
                        </GlassButton>
                        <Link
                          className="glass-btn glass-btn-primary"
                          to="/overview"
                          onClick={() => {
                            setTaskId(it.task_id);
                          }}
                        >
                          {t("open")}
                        </Link>
                        <GlassButton
                          variant="danger"
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
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </RackPanel>
  );
}
