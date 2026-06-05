import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FileDropZone from "../components/FileDropZone";
import GlassButton from "../components/GlassButton";
import MethodSelector from "../components/MethodSelector";
import RackPanel from "../components/RackPanel";
import { useI18n } from "../i18n/I18nContext";
import { probeAudioFile, type AudioFileMeta } from "../lib/audioMeta";
import { usesNoisereduceStrength } from "../lib/methodOptions";
import { startProcess, uploadAudio } from "../lib/api";

type Props = {
  setTaskId: (taskId: string) => void;
};

export default function UploadConfigPage({ setTaskId }: Props) {
  const nav = useNavigate();
  const { t } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [meta, setMeta] = useState<AudioFileMeta | null>(null);
  const [method, setMethod] = useState("auto");

  useEffect(() => {
    const pre = sessionStorage.getItem("upload_method_prefill");
    if (pre) {
      setMethod(pre);
      sessionStorage.removeItem("upload_method_prefill");
    }
  }, []);
  const [runDistill, setRunDistill] = useState(false);
  const [strength, setStrength] = useState(0.8);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const flowSteps = [
    { n: "01", key: "flowUpload", active: true },
    { n: "02", key: "flowMethod", active: false },
    { n: "03", key: "flowProgress", active: false },
    { n: "04", key: "flowListen", active: false },
  ] as const;

  useEffect(() => {
    if (!file) {
      setMeta(null);
      return;
    }
    let cancelled = false;
    probeAudioFile(file).then((m) => {
      if (!cancelled) setMeta(m);
    });
    return () => {
      cancelled = true;
    };
  }, [file]);

  const strengthEnabled = usesNoisereduceStrength(method);
  const led = loading ? "processing" : file ? "active" : "idle";

  const submit = async () => {
    if (!file) return;
    setLoading(true);
    setMsg("");
    try {
      const uploaded = await uploadAudio(file);
      setTaskId(uploaded.task_id);
      await startProcess({
        task_id: uploaded.task_id,
        method,
        run_distill_refine: runDistill,
        noisereduce_strength: strength,
      });
      setMsg(`${t("taskQueued")}: ${uploaded.task_id}`);
      nav("/progress");
    } catch (e) {
      setMsg(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <RackPanel
      className="stagger upload-page"
      moduleId="MOD-02"
      channel="INPUT"
      led={led}
      title={t("uploadTitle")}
      subtitle={t("uploadSubtitle")}
    >
      <ol className="upload-flow-strip" aria-label={t("uploadFlowHint")}>
        {flowSteps.map((s) => (
          <li key={s.n} className={s.active ? "is-active" : ""}>
            <span className="upload-flow-n">{s.n}</span>
            {t(s.key)}
          </li>
        ))}
      </ol>
      <div className="column gap">
        <FileDropZone
          file={file}
          meta={meta}
          onFile={(f) => {
            setFile(f);
            if (!f) setMeta(null);
          }}
        />

        <div className="upload-options">
          <MethodSelector value={method} onChange={setMethod} />
          <div className="upload-side-options">
            <label className="toggle-row">
              <input type="checkbox" checked={runDistill} onChange={(e) => setRunDistill(e.target.checked)} />
              {t("runDistill")}
            </label>
            <label className={`strength-row ${strengthEnabled ? "" : "is-disabled"}`}>
              {t("strength")}: {strength.toFixed(2)}
              {!strengthEnabled ? <span className="muted"> — {t("strengthDisabled")}</span> : null}
              <input
                type="range"
                min={0.1}
                max={1.0}
                step={0.05}
                value={strength}
                disabled={!strengthEnabled}
                onChange={(e) => setStrength(Number(e.target.value))}
              />
            </label>
          </div>
        </div>

        <div className="actions">
          <GlassButton variant="primary" disabled={!file || loading} onClick={submit}>
            {loading ? t("uploading") : t("uploadBtn")}
          </GlassButton>
        </div>
        {msg ? (
          <p className={msg.includes("Error") || msg.includes("失败") ? "error" : "muted"} role="status" aria-live="polite">
            {msg}
          </p>
        ) : null}
      </div>
    </RackPanel>
  );
}
