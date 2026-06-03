import { useI18n } from "../i18n/I18nContext";

type Props = {
  method: string;
  route: string[];
  reason: string;
};

function isDeepfilterMismatch(method: string, route: string[], reason: string): boolean {
  if (method !== "deepfilter") return false;
  const routeOk = route.some((r) => r.toLowerCase().includes("deepfilter"));
  const reasonOk = reason.toLowerCase().includes("deepfilter");
  const fallback =
    reason.toLowerCase().includes("fallback") ||
    reason.toLowerCase().includes("unavailable") ||
    route.some((r) => r.includes("omlsa") && !routeOk);
  return !routeOk || fallback || (!reasonOk && reason.length > 0);
}

export default function PipelineSummary({ method, route, reason }: Props) {
  const { t } = useI18n();
  const mismatch = isDeepfilterMismatch(method, route, reason);
  const routeText = route.length ? route.join(" → ") : "—";

  return (
    <div className={`pipeline-summary ${mismatch ? "pipeline-alert" : ""}`}>
      <div className="pipeline-summary-head">
        <h3 className="section-title">{t("pipelineTitle")}</h3>
        {mismatch ? <span className="pipeline-warn-badge">{t("pipelineMismatch")}</span> : null}
      </div>
      <dl className="pipeline-dl">
        <div>
          <dt>{t("methodLabel")}</dt>
          <dd>{method}</dd>
        </div>
        <div>
          <dt>{t("routeLabel")}</dt>
          <dd className="pipeline-route">{routeText}</dd>
        </div>
        <div className="pipeline-reason-row">
          <dt>{t("reasonLabel")}</dt>
          <dd>{reason || "—"}</dd>
        </div>
      </dl>
      {mismatch ? <p className="pipeline-alert-text">{t("pipelineMismatchHint")}</p> : null}
    </div>
  );
}
