import { useCallback, useEffect, useRef, useState } from "react";
import GlassButton from "../../components/GlassButton";
import RackPanel from "../../components/RackPanel";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import { useI18n } from "../../i18n/I18nContext";
import type { DictKey } from "../../i18n";
import { getHistory, getMetrics } from "../../lib/api";
import { isDeepfilterMismatch } from "../../lib/pipelineUtils";
import { animatePipelineSteps } from "../../lib/showcasePipelineAnim";
import { PIPELINE_PRESETS } from "../../lib/showcasePresets";

type Props = {
  taskId: string;
};

type PipelineMode = "preset" | "task";

export default function PipelineTheaterPage({ taskId }: Props) {
  const { t } = useI18n();
  const [presetId, setPresetId] = useState("auto");
  const [litCount, setLitCount] = useState(-1);
  const [route, setRoute] = useState<string[]>(PIPELINE_PRESETS[0].route);
  const [reason, setReason] = useState(PIPELINE_PRESETS[0].reason);
  const [method, setMethod] = useState("auto");
  const [mode, setMode] = useState<PipelineMode>("preset");
  const [presetHint, setPresetHint] = useState("");
  const [completeFlash, setCompleteFlash] = useState(false);
  const [liveMsg, setLiveMsg] = useState("");
  const animCleanup = useRef<(() => void) | null>(null);

  const preset = PIPELINE_PRESETS.find((p) => p.id === presetId) ?? PIPELINE_PRESETS[0];
  const mismatch = isDeepfilterMismatch(method, route, reason);
  const nodes = ["INPUT", ...route, "OUTPUT"];
  const complete = litCount >= nodes.length - 1;

  const runAnimation = useCallback((nodeCount: number) => {
    animCleanup.current?.();
    animCleanup.current = animatePipelineSteps(nodeCount, (idx) => {
      setLitCount(idx);
      if (idx >= nodeCount - 1) {
        setCompleteFlash(true);
        window.setTimeout(() => setCompleteFlash(false), 150);
      }
    });
  }, []);

  const applyPreset = useCallback(
    (id: string) => {
      const p = PIPELINE_PRESETS.find((x) => x.id === id) ?? PIPELINE_PRESETS[0];
      setPresetId(id);
      setRoute(p.route);
      setReason(p.reason);
      setMethod(id === "deepfilter" ? "deepfilter" : id === "auto" ? "auto" : p.route[0] ?? id);
      setMode("preset");
      if (mode === "task") {
        setPresetHint(t("showcaseSwitchedToPreset"));
        window.setTimeout(() => setPresetHint(""), 2800);
      }
      runAnimation(p.route.length + 2);
    },
    [mode, runAnimation, t],
  );

  useEffect(() => {
    runAnimation(PIPELINE_PRESETS[0].route.length + 2);
    return () => animCleanup.current?.();
  }, [runAnimation]);

  const loadTask = async () => {
    if (!taskId) return;
    const apply = (r: string[], rs: string, m: string) => {
      setRoute(r);
      setReason(rs);
      setMethod(m);
      setMode("task");
      setLiveMsg(`${t("routeLabel")}: ${r.join(" → ") || "—"}`);
      runAnimation(r.length + 2);
    };
    try {
      const metrics = await getMetrics(taskId);
      apply(metrics.route ?? [], metrics.reason ?? "", metrics.method ?? "auto");
    } catch {
      const items = await getHistory();
      const task = items.find((x) => x.task_id === taskId);
      if (task) {
        const m = task.settings?.method;
        apply(task.route ?? [], task.reason ?? "", typeof m === "string" ? m : "auto");
      }
    }
  };

  return (
    <div className="showcase-page showcase-page-inner stagger-fast">
      <ShowcaseSubNav />
      <ShowcasePageHeader
        variant="inner"
        moduleId="MOD-S02"
        channel="ROUTE"
        title={t("showcasePipelineTitle")}
        subtitle={t("showcasePipelineSubtitle")}
      />
      <RackPanel
        moduleId="MOD-S02"
        channel="ROUTE"
        led={mismatch ? "error" : complete ? "active" : "processing"}
        alert={mismatch}
        className="pipeline-theater rack-no-corner-led"
      >
        {mismatch ? <p className="pipeline-alert-text">{t("pipelineMismatchHint")}</p> : null}
        {presetHint ? <p className="showcase-inline-hint">{presetHint}</p> : null}
        <div className="pipeline-presets">
          {PIPELINE_PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              className={`pipeline-preset-btn ${mode === "preset" && presetId === p.id ? "is-active" : ""} ${mode === "task" ? "is-dimmed" : ""}`}
              onClick={() => applyPreset(p.id)}
            >
              {t(p.labelKey as DictKey)}
            </button>
          ))}
          {taskId ? (
            <GlassButton variant="accent" onClick={loadTask}>
              {mode === "task" ? t("showcaseReloadTask") : t("showcaseLoadTask")}
            </GlassButton>
          ) : null}
        </div>
        <div
          className={`pipeline-flow ${complete ? "pipeline-flow-complete" : ""} ${completeFlash ? "pipeline-flow-flash" : ""}`}
          role="list"
          aria-label={t("showcasePipelineTitle")}
        >
          {nodes.map((node, idx) => {
            const lit = idx <= litCount;
            const isOutput = node === "OUTPUT" && idx === nodes.length - 1;
            return (
              <div key={`${node}-${idx}`} style={{ display: "contents" }}>
                <div
                  className={`pipeline-node ${lit ? "is-lit" : ""} ${isOutput ? "pipeline-node-output" : ""}`}
                  role="listitem"
                  aria-label={node}
                >
                  <span className={`rack-led rack-led-${lit ? "active" : "idle"}`} />
                  <div className="pipeline-node-box">{node}</div>
                </div>
                {idx < nodes.length - 1 ? (
                  <div className="pipeline-connector">
                    {lit && idx < litCount ? (
                      <span className="pipeline-dot" style={{ animationDelay: `${idx * 0.35}s` }} />
                    ) : null}
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
        <div className="pipeline-reason-lcd method-lcd">
          <span className={`showcase-mode-badge ${mode === "task" ? "showcase-live-badge" : "showcase-sim-badge"}`}>
            {mode === "task" ? t("showcaseLiveBadge") : t("showcaseSimBadge")}
          </span>
          <span>
            <strong>{t("reasonLabel")}: </strong>
            {reason || "—"}
            {mode === "task" ? ` · ${t("showcaseTaskSource")}` : ` · ${t(preset.labelKey as DictKey)}`}
            {complete ? ` · ${t("showcasePipelineComplete")}` : ""}
          </span>
        </div>
        <p className="sr-only" role="status" aria-live="polite">
          {liveMsg}
        </p>
      </RackPanel>
    </div>
  );
}
