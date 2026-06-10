import { useI18n } from "../../i18n/I18nContext";

export type CapturePhase = "idle" | "arming" | "recording" | "preview" | "committing";

type Props = {
  phase: CapturePhase;
  timerSec: number;
  levelDb: number;
  onStart: () => void;
  onStop: () => void;
  onRetake?: () => void;
  disabled?: boolean;
};

function formatTimer(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export default function RecordTransport({ phase, timerSec, levelDb, onStart, onStop, onRetake, disabled }: Props) {
  const { t } = useI18n();
  const recording = phase === "recording";
  const canStart = phase === "idle" || phase === "arming";
  const canStop = phase === "recording";
  const canRetake = phase === "preview" && onRetake;

  const statusText =
    phase === "recording"
      ? t("recordStatusRecording")
      : phase === "preview"
        ? t("recordStatusPreview")
        : phase === "arming"
          ? t("recordStatusArming")
          : t("recordStatusIdle");

  return (
    <div className="record-transport" aria-live="polite">
      <div className="record-transport-buttons">
        {canStart ? (
          <button
            type="button"
            className={`record-rec-btn ${phase === "arming" ? "is-arming" : ""}`}
            onClick={onStart}
            disabled={disabled || phase === "arming"}
            aria-pressed={recording}
            aria-label={t("recordStart")}
          >
            <span className="record-rec-dot" aria-hidden="true" />
            REC
          </button>
        ) : null}
        {canStop ? (
          <button type="button" className="record-stop-btn" onClick={onStop} aria-label={t("recordStop")}>
            ■ {t("recordStop")}
          </button>
        ) : null}
        {canRetake ? (
          <button type="button" className="record-retake-btn" onClick={onRetake} aria-label={t("recordReTake")}>
            {t("recordReTake")}
          </button>
        ) : null}
      </div>
      <div className="record-transport-readouts">
        <span className="record-timer mono">{formatTimer(timerSec)}</span>
        <span className="record-level mono">{levelDb.toFixed(1)} dBFS</span>
        <span className="record-status">{statusText}</span>
      </div>
    </div>
  );
}
