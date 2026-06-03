import { useI18n } from "../i18n/I18nContext";

type Props = {
  status: string;
};

export default function StatusBadge({ status }: Props) {
  const { t } = useI18n();
  const normalized = status.toLowerCase();
  const cls =
    normalized === "completed"
      ? "status-badge status-completed"
      : normalized === "failed"
        ? "status-badge status-failed"
        : normalized === "processing" || normalized === "queued"
          ? "status-badge status-processing"
          : "status-badge status-idle";

  const labelKey =
    normalized === "completed"
      ? "statusCompleted"
      : normalized === "failed"
        ? "statusFailed"
        : normalized === "processing"
          ? "statusProcessing"
          : normalized === "queued"
            ? "statusQueued"
            : "statusUploaded";

  return (
    <span className={cls}>
      {t(labelKey)}
      <span className="status-raw">{status}</span>
    </span>
  );
}
