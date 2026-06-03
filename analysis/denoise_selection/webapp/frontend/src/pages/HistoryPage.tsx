import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import GlassButton from "../components/GlassButton";
import GlassCard from "../components/GlassCard";
import { useI18n } from "../i18n/I18nContext";
import { deleteTask, getHistory } from "../lib/api";
import type { TaskItem } from "../types/api";

type Props = {
  setTaskId: (taskId: string) => void;
};

export default function HistoryPage({ setTaskId }: Props) {
  const { t } = useI18n();
  const [items, setItems] = useState<TaskItem[]>([]);

  const reload = async () => setItems(await getHistory());
  useEffect(() => {
    reload().catch(() => undefined);
  }, []);

  return (
    <GlassCard title={t("historyTitle")} subtitle={t("historySubtitle")}>
      <table>
        <thead>
          <tr>
            <th>{t("colTask")}</th>
            <th>{t("colFile")}</th>
            <th>{t("colStatus")}</th>
            <th>{t("colUpdated")}</th>
            <th>{t("colAction")}</th>
          </tr>
        </thead>
        <tbody>
          {items.map((it) => (
            <tr key={it.task_id}>
              <td>{it.task_id}</td>
              <td>{it.filename}</td>
              <td>{it.status}</td>
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
    </GlassCard>
  );
}
