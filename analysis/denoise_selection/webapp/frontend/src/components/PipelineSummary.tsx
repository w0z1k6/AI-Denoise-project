import { useI18n } from "../i18n/I18nContext";
import { isDeepfilterMismatch } from "../lib/pipelineUtils";

type Props = {
  method: string;
  route: string[];
  reason: string;
};

export default function PipelineSummary({ method, route, reason }: Props) {
  const { t } = useI18n();
  const mismatch = isDeepfilterMismatch(method, route, reason);
  const routeText = route.length ? route.join(" → ") : "—";

  return (
    <div className={`pipeline-summary rack-no-corner-led ${mismatch ? "pipeline-alert rack-panel-alert" : ""}`}>
      <div className="rack-panel-head">
        <span className="rack-panel-id">MOD-03 / PIPELINE</span>
        <span className={`rack-led ${mismatch ? "rack-led-error" : "rack-led-active"}`} aria-hidden="true" />
      </div>
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
