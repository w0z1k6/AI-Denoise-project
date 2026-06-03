import { useState } from "react";
import { useNavigate } from "react-router-dom";
import GlassButton from "../components/GlassButton";
import GlassCard from "../components/GlassCard";
import { useI18n } from "../i18n/I18nContext";
import { startProcess, uploadAudio } from "../lib/api";

type Props = {
  setTaskId: (taskId: string) => void;
};

export default function UploadConfigPage({ setTaskId }: Props) {
  const nav = useNavigate();
  const { t } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [method, setMethod] = useState("auto");
  const [runDistill, setRunDistill] = useState(false);
  const [strength, setStrength] = useState(0.8);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const submit = async () => {
    if (!file) return;
    setLoading(true);
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
    <GlassCard className="stagger" title={t("uploadTitle")} subtitle={t("uploadSubtitle")}>
      <div className="column gap">
        <input type="file" accept=".wav,.mp3,.flac" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <div className="grid2">
          <label>
            {t("method")}
            <select value={method} onChange={(e) => setMethod(e.target.value)}>
              <option value="auto">auto</option>
              <option value="noisereduce">noisereduce</option>
              <option value="wiener">wiener</option>
              <option value="omlsa">omlsa</option>
              <option value="deepfilter">deepfilter</option>
              <option value="base_omlsa_mcra">base_omlsa_mcra</option>
              <option value="kalman_ar">kalman_ar</option>
              <option value="subspace_denoise">subspace_denoise</option>
            </select>
          </label>
          <label>
            {t("runDistill")}
            <input type="checkbox" checked={runDistill} onChange={(e) => setRunDistill(e.target.checked)} />
          </label>
        </div>
        <label>
          {t("strength")}: {strength.toFixed(2)}
          <input type="range" min={0.1} max={1.0} step={0.05} value={strength} onChange={(e) => setStrength(Number(e.target.value))} />
        </label>
        <div className="actions">
          <GlassButton variant="primary" disabled={!file || loading} onClick={submit}>
            {loading ? t("uploading") : t("uploadBtn")}
          </GlassButton>
        </div>
        {msg ? <p className="muted">{msg}</p> : null}
      </div>
    </GlassCard>
  );
}
