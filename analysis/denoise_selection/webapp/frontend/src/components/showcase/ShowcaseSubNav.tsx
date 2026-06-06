import { NavLink } from "react-router-dom";
import { useI18n } from "../../i18n/I18nContext";
import type { DictKey } from "../../i18n";

const links: { to: string; key: DictKey; code: string; end?: boolean }[] = [
  { to: "/showcase", key: "showcaseSubNavHub", code: "HUB", end: true },
  { to: "/showcase/algorithms", key: "showcaseNavAlgo", code: "S01" },
  { to: "/showcase/pipeline", key: "showcaseNavPipeline", code: "S02" },
  { to: "/showcase/monitor", key: "showcaseNavMonitor", code: "S03" },
  { to: "/showcase/cinema", key: "showcaseNavCinema", code: "S04" },
];

type Props = {
  hidden?: boolean;
};

export default function ShowcaseSubNav({ hidden = false }: Props) {
  const { t } = useI18n();
  if (hidden) return null;
  return (
    <nav className={`showcase-subnav ${hidden ? "showcase-subnav-hidden" : ""}`} aria-label={t("showcaseSubNavAria")}>
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.end}
          className={({ isActive }) => `showcase-subnav-link ${isActive ? "is-active" : ""}`}
        >
          <span className="showcase-subnav-code">{l.code}</span>
          {t(l.key)}
        </NavLink>
      ))}
    </nav>
  );
}
