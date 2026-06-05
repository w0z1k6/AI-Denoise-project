import { Link } from "react-router-dom";
import { useI18n } from "../i18n/I18nContext";

export default function HomePage() {
  const { t } = useI18n();

  const features = [
    { title: t("featUpload"), desc: t("featUploadDesc") },
    { title: t("featMetrics"), desc: t("featMetricsDesc") },
    { title: t("featCharts"), desc: t("featChartsDesc") },
    { title: t("featAbx"), desc: t("featAbxDesc") },
  ];

  const flowSteps = [
    { n: "01", label: t("flowUpload") },
    { n: "02", label: t("flowMethod") },
    { n: "03", label: t("flowProgress") },
    { n: "04", label: t("flowListen") },
    { n: "05", label: t("flowCharts") },
    { n: "06", label: t("flowHistory") },
  ];

  return (
    <div className="console-home stagger">
      <section className="console-hero">
        <p className="console-eyebrow">{t("homeHeroTagline")}</p>
        <h1 className="console-title">
          Denoise
          <em>Studio</em>
        </h1>
        <p className="console-lede">{t("homeHeroSubtitle")}</p>
        <div className="console-actions">
          <Link to="/upload" className="console-cta-primary">
            {t("homeStart")}
            <svg viewBox="0 0 1024 1024" aria-hidden="true">
              <path d="M779.18 473.23 322.35 16.41c-21.41-21.41-56.12-21.41-77.53 0-21.41 21.41-21.41 56.12 0 77.53l418.06 418.06L244.82 930.06c-21.41 21.41-21.41 56.12 0 77.53 10.71 10.71 24.76 16.06 38.77 16.06s28.06-5.35 38.77-16.06L779.18 550.77c21.41-21.41 21.41-56.12 0-77.54z" />
            </svg>
          </Link>
          <Link to="/overview" className="console-cta-ghost">
            {t("homeViewResults")}
          </Link>
        </div>
      </section>

      <aside className="console-rack">
        <div className="console-module">
          <div className="console-module-head">
            <span>MOD-01 / INPUT</span>
            <span className="console-module-led" aria-hidden="true" />
          </div>
          <div className="console-meter-row" aria-hidden="true">
            <div />
            <div />
            <div />
            <div />
            <div />
          </div>
          <div className="console-readouts">
            <div className="console-readout">
              <strong>28</strong>
              <span>{t("homeStatCharts")}</span>
            </div>
            <div className="console-readout">
              <strong>10+</strong>
              <span>{t("homeStatAlgos")}</span>
            </div>
            <div className="console-readout">
              <strong>ABX</strong>
              <span>{t("homeStatAbx")}</span>
            </div>
          </div>
        </div>
      </aside>

      <ol className="console-flow" aria-label={t("homeFlowAria")}>
        {flowSteps.map((s) => (
          <li key={s.n}>
            <span className="console-flow-n">{s.n}</span>
            {s.label}
          </li>
        ))}
      </ol>

      <div className="console-bento">
        {features.map((f) => (
          <article key={f.title} className="console-tile">
            <h4>{f.title}</h4>
            <p>{f.desc}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
