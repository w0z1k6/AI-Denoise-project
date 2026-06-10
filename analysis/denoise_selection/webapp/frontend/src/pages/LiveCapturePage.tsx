import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AudioComparePlayer from "../components/AudioComparePlayer";
import GlassButton from "../components/GlassButton";
import LiveWaveformScope from "../components/live/LiveWaveformScope";
import RecordTransport from "../components/live/RecordTransport";
import MethodSelector from "../components/MethodSelector";
import RackPanel from "../components/RackPanel";
import VuMeterBar from "../components/showcase/VuMeterBar";
import { useLiveCapture } from "../hooks/useLiveCapture";
import { useI18n } from "../i18n/I18nContext";
import { motionFlags } from "../lib/pointerStore";
import { usesNoisereduceStrength } from "../lib/methodOptions";

type Props = {
  setTaskId: (taskId: string) => void;
};

export default function LiveCapturePage({ setTaskId }: Props) {
  const { t } = useI18n();
  const nav = useNavigate();
  const cap = useLiveCapture();
  const [method, setMethod] = useState("auto");
  const [runDistill, setRunDistill] = useState(false);
  const [strength, setStrength] = useState(0.8);

  const flowSteps = [
    { n: "01", key: "recordFlowMic", active: cap.phase === "idle" },
    { n: "02", key: "recordFlowRec", active: cap.phase === "arming" || cap.phase === "recording" },
    { n: "03", key: "recordFlowAnc", active: cap.phase === "recording" && cap.ancEnabled },
    { n: "04", key: "recordFlowCommit", active: cap.phase === "preview" || cap.phase === "committing" },
  ] as const;

  useEffect(() => {
    motionFlags.processing =
      cap.phase === "arming" || cap.phase === "recording" || cap.phase === "committing";
    return () => {
      motionFlags.processing = false;
    };
  }, [cap.phase]);

  const led =
    cap.phase === "recording" ? "active" : cap.phase === "committing" || cap.phase === "arming" ? "processing" : "idle";

  const strengthEnabled = usesNoisereduceStrength(method);
  const ancToggleDisabled = cap.phase !== "recording";

  const onCommit = async () => {
    const taskId = await cap.commitTask({
      method,
      run_distill_refine: runDistill,
      noisereduce_strength: strength,
    });
    if (taskId) {
      setTaskId(taskId);
      nav("/progress");
    }
  };

  const micMsg =
    cap.micError === "recordMicDenied"
      ? t("recordMicDenied")
      : cap.micError;

  return (
    <RackPanel
      className="stagger live-capture-page"
      moduleId="MOD-07"
      channel="LIVE"
      led={led}
      title={t("recordTitle")}
      subtitle={t("recordSubtitle")}
    >
      <ol className="upload-flow-strip record-flow-strip" aria-label={t("recordSubtitle")}>
        {flowSteps.map((s) => (
          <li key={s.n} className={s.active ? "is-active" : ""}>
            <span className="upload-flow-n">{s.n}</span>
            {t(s.key)}
          </li>
        ))}
      </ol>

      <div className="live-tier-strip" aria-label={t("recordTierAria")}>
        <span className={`live-tier-pill ${cap.phase === "recording" ? "is-active" : ""}`}>
          <strong>L1</strong> {t("recordTierL1")}
        </span>
        <span className={`live-tier-pill ${cap.phase === "preview" ? "is-active" : ""}`}>
          <strong>L2</strong> {t("recordTierL2")}
        </span>
        <span
          className={`live-tier-pill ${cap.phase === "preview" || cap.phase === "committing" ? "is-active is-pipeline" : ""}`}
        >
          <strong>L3</strong> {t("recordTierL3")}
        </span>
      </div>

      <section
        className="live-module live-module-input live-scope-solo"
        data-recording={cap.phase === "recording" ? "true" : "false"}
      >
        <header className="live-module-head">
          <span>MOD-07A / INPUT</span>
          <span className="live-preview-tag">{t("recordPreviewTag")}</span>
          <span className={`rack-led rack-led-${led}`} aria-hidden="true" />
        </header>
        <div className="live-scope-meta">
          <span className="live-scope-channel mono">{t("recordScopeChannel")}</span>
          <span className="live-scope-mode mono">
            {cap.phase === "recording" ? t("recordScopeLive") : t("recordScopeStandby")}
          </span>
        </div>
        <LiveWaveformScope
          analyser={cap.analyser}
          recording={cap.phase === "recording"}
          idleHint={cap.phase === "idle" || cap.phase === "arming" ? t("recordScopeIdle") : ""}
          height={168}
        />
        <div className="live-vu-row">
          <VuMeterBar value={cap.inputLevel * 4} label="IN" vertical pulse={cap.phase === "recording"} />
          <VuMeterBar value={cap.outputLevel * 4} label="ANC" vertical pulse={cap.ancEnabled} />
        </div>
        <div className="live-anc-bar">
          <label className="live-anc-toggle live-anc-toggle-inline">
            <input
              type="checkbox"
              checked={cap.ancEnabled}
              disabled={ancToggleDisabled}
              onChange={(e) => cap.setAncEnabled(e.target.checked)}
            />
            <span>{cap.ancEnabled ? t("recordAncOn") : t("recordAncOff")}</span>
          </label>
          {cap.latencyMs > 0 ? (
            <span className="live-latency mono">{t("recordLatency").replace("{ms}", String(cap.latencyMs))}</span>
          ) : null}
          {cap.ancDegraded ? <span className="live-anc-degraded">{t("recordAncDegraded")}</span> : null}
        </div>
      </section>

      <RecordTransport
        phase={cap.phase}
        timerSec={cap.timerSec}
        levelDb={cap.levelDb}
        onStart={() => void cap.startRecording()}
        onStop={() => void cap.stopRecording()}
        onRetake={cap.retake}
        disabled={cap.phase === "committing"}
      />

      {micMsg ? <p className="live-error">{micMsg}</p> : null}

      {cap.previewUrls ? (
        <div className="live-preview-block stagger-fast">
          <header className="live-section-head">
            <span className="live-section-tag live-section-tag-l2">{t("recordTierL2")}</span>
            <h4 className="live-section-title">{t("recordPreviewSection")}</h4>
          </header>
          <AudioComparePlayer originalUrl={cap.previewUrls.raw} denoisedUrl={cap.previewUrls.preview} />
          <header className="live-section-head">
            <span className="live-section-tag live-section-tag-l3">{t("recordPipelineTag")}</span>
            <h4 className="live-section-title">{t("recordCommitSection")}</h4>
          </header>
          <div className="column gap live-commit-panel">
            <MethodSelector value={method} onChange={setMethod} />
            <label>
              <input type="checkbox" checked={runDistill} onChange={(e) => setRunDistill(e.target.checked)} /> {t("runDistill")}
            </label>
            <label>
              {t("strength")}
              <input
                type="range"
                min={0.1}
                max={1}
                step={0.05}
                value={strength}
                disabled={!strengthEnabled}
                onChange={(e) => setStrength(Number(e.target.value))}
              />
            </label>
            <GlassButton variant="primary" onClick={() => void onCommit()} disabled={cap.phase === "committing"}>
              {t("recordCommit")}
            </GlassButton>
          </div>
        </div>
      ) : null}
    </RackPanel>
  );
}
