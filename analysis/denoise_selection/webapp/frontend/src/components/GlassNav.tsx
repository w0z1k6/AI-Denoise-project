import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useI18n } from "../i18n/I18nContext";
import { abbreviateTaskId } from "../lib/pipelineUtils";
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
  { to: "/showcase", key: "navShowcase" as const, end: false },
  { to: "/history", key: "navHistory" as const, end: false },
];

export default function GlassNav({ currentTaskId }: Props) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const { t, toggleLang, toggleTheme, theme } = useI18n();

  const copyTask = async () => {
    if (!currentTaskId) return;
    try {
      await navigator.clipboard.writeText(currentTaskId);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  const taskDisplay = currentTaskId ? abbreviateTaskId(currentTaskId) : "—";

  return (
    <header className="glass-nav-shell">
      <div className="glass-nav">
        <Link to="/" className="glass-nav-brand brand-signal" onClick={() => setOpen(false)}>
          <div className="brand-vu" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>
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
              className={({ isActive }) =>
                `glass-nav-link ${isActive ? "active" : ""} ${isActive && item.to === "/showcase" ? "glass-nav-link-showcase" : ""}`.trim()
              }
            >
              {t(item.key)}
            </NavLink>
          ))}
        </nav>
        <div className="glass-nav-right">
          <span className={`task-pill ${copied ? "task-pill-copied" : ""}`} title={currentTaskId || undefined}>
            <span className="task-pill-label">{t("taskLabel")}</span>
            <code>{taskDisplay}</code>
            {currentTaskId ? (
              <button type="button" className="task-copy-btn" onClick={copyTask}>
                {copied ? t("copied") : t("copyTaskId")}
              </button>
            ) : null}
          </span>
          <GlassButton
            className="icon-btn"
            variant="ghost"
            onClick={toggleTheme}
            title={theme === "light" ? t("themeDark") : t("themeLight")}
          >
            <span className={`theme-icon theme-icon-${theme === "light" ? "moon" : "sun"}`} aria-hidden="true" />
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
