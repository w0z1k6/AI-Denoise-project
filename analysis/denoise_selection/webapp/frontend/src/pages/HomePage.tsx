import { Link } from "react-router-dom";
import { useI18n } from "../i18n/I18nContext";
import GlassButton from "../components/GlassButton";
import TiltContainer from "../components/TiltContainer";

export default function HomePage() {
  const { t } = useI18n();

  const features = [
    { icon: "🎵", cls: "feature-icon-blue", title: t("featUpload"), desc: t("featUploadDesc") },
    { icon: "📊", cls: "feature-icon-cyan", title: t("featMetrics"), desc: t("featMetricsDesc") },
    { icon: "📈", cls: "feature-icon-purple", title: t("featCharts"), desc: t("featChartsDesc") },
    { icon: "🎧", cls: "feature-icon-orange", title: t("featAbx"), desc: t("featAbxDesc") },
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
                📋
              </Link>
              <Link to="/upload" className="neu-icon-btn neu-icon-btn-primary" title={t("homeStart")}>
                ▶
              </Link>
              <Link to="/charts" className="neu-icon-btn" title={t("navCharts")}>
                📈
              </Link>
            </div>
          </div>
        </TiltContainer>
      </div>

      <div className="home-stats">
        <div className="home-stat">
          <strong>24+</strong>
          <span>{t("homeStatCharts")}</span>
        </div>
        <div className="home-stat">
          <strong>8</strong>
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
            <div className={`feature-icon ${f.cls}`}>{f.icon}</div>
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
