import { Link } from "react-router-dom";
import { useI18n } from "../i18n/I18nContext";
import GlassButton from "../components/GlassButton";
import TiltContainer from "../components/TiltContainer";

export default function HomePage() {
  const { t } = useI18n();

  const features = [
    { icon: "upload" as const, cls: "feature-icon-blue", title: t("featUpload"), desc: t("featUploadDesc") },
    { icon: "metrics" as const, cls: "feature-icon-cyan", title: t("featMetrics"), desc: t("featMetricsDesc") },
    { icon: "charts" as const, cls: "feature-icon-purple", title: t("featCharts"), desc: t("featChartsDesc") },
    { icon: "abx" as const, cls: "feature-icon-orange", title: t("featAbx"), desc: t("featAbxDesc") },
  ];

  const flowSteps = [
    { n: "1", label: t("flowUpload") },
    { n: "2", label: t("flowMethod") },
    { n: "3", label: t("flowProgress") },
    { n: "4", label: t("flowListen") },
    { n: "5", label: t("flowCharts") },
    { n: "6", label: t("flowHistory") },
  ];

  return (
    <div className="home-page">
      <div className="home-hero-wrap">
        <TiltContainer>
          <div className="hero-neu-card">
            <div className="liquid-orb" aria-hidden="true" />
            <h2 className="hero-title">{t("homeHeroTitle")}</h2>
            <p className="hero-subtitle">{t("homeHeroSubtitle")}</p>
            <p className="hero-tagline">{t("homeHeroTagline")}</p>
            <div className="hero-controls">
              <Link to="/history" className="neu-icon-btn" title={t("navHistory")}>
                <span className="neu-glyph neu-glyph-list" aria-hidden="true" />
              </Link>
              <Link to="/upload" className="neu-icon-btn neu-icon-btn-primary" title={t("homeStart")}>
                <span className="neu-glyph neu-glyph-play" aria-hidden="true" />
              </Link>
              <Link to="/charts" className="neu-icon-btn" title={t("navCharts")}>
                <span className="neu-glyph neu-glyph-chart" aria-hidden="true" />
              </Link>
            </div>
          </div>
        </TiltContainer>
      </div>

      <ol className="home-flow" aria-label={t("homeFlowAria")}>
        {flowSteps.map((s) => (
          <li key={s.n}>
            <span className="home-flow-n">{s.n}</span>
            <span>{s.label}</span>
          </li>
        ))}
      </ol>

      <div className="home-stats">
        <div className="home-stat">
          <strong>28</strong>
          <span>{t("homeStatCharts")}</span>
        </div>
        <div className="home-stat">
          <strong>10+</strong>
          <span>{t("homeStatAlgos")}</span>
        </div>
        <div className="home-stat">
          <strong>ABX</strong>
          <span>{t("homeStatAbx")}</span>
        </div>
      </div>

      <div className="home-features">
        {features.map((f) => (
          <article key={f.title} className="feature-neu-card">
            <div className={`feature-icon ${f.cls}`}>
              <span className={`feature-glyph feature-glyph-${f.icon}`} aria-hidden="true" />
            </div>
            <h4>{f.title}</h4>
            <p>{f.desc}</p>
          </article>
        ))}
      </div>

      <div className="home-cta-row">
        <Link to="/upload">
          <GlassButton variant="primary">{t("homeStart")}</GlassButton>
        </Link>
        <Link to="/overview">
          <GlassButton variant="secondary">{t("homeViewResults")}</GlassButton>
        </Link>
      </div>
    </div>
  );
}
