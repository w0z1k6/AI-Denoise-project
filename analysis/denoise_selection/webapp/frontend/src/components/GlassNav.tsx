import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useI18n } from "../i18n/I18nContext";
import GlassButton from "./GlassButton";

type Props = {
  currentTaskId: string;
};

const navPaths = [
  { to: "/", key: "navHome" as const, end: true },
  { to: "/upload", key: "navUpload" as const, end: false },
  { to: "/progress", key: "navProgress" as const, end: false },
  { to: "/overview", key: "navOverview" as const, end: false },
  { to: "/charts", key: "navCharts" as const, end: false },
  { to: "/history", key: "navHistory" as const, end: false },
];

export default function GlassNav({ currentTaskId }: Props) {
  const [open, setOpen] = useState(false);
  const { t, toggleLang, toggleTheme, theme } = useI18n();

  return (
    <header className="glass-nav-shell">
      <div className="glass-nav">
        <Link to="/" className="glass-nav-brand" onClick={() => setOpen(false)}>
          <span className="brand-dot" />
          <div>
            <h1>{t("brandTitle")}</h1>
            <small>{t("brandSubtitle")}</small>
          </div>
        </Link>
        <nav className={`glass-nav-links ${open ? "open" : ""}`}>
          {navPaths.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={() => setOpen(false)}
              className={({ isActive }) => `glass-nav-link ${isActive ? "active" : ""}`}
            >
              {t(item.key)}
            </NavLink>
          ))}
        </nav>
        <div className="glass-nav-right">
          <span className="task-pill">
            {t("taskLabel")}: {currentTaskId || "-"}
          </span>
          <GlassButton className="icon-btn" variant="ghost" onClick={toggleTheme} title={theme === "light" ? t("themeDark") : t("themeLight")}>
            {theme === "light" ? "🌙" : "☀️"}
          </GlassButton>
          <GlassButton className="icon-btn" variant="ghost" onClick={toggleLang}>
            {t("langSwitch")}
          </GlassButton>
          <GlassButton className="menu-btn" variant="ghost" onClick={() => setOpen((v) => !v)}>
            {t("menu")}
          </GlassButton>
        </div>
      </div>
    </header>
  );
}
