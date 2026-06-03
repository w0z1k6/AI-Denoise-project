import { useEffect, useMemo, useRef, useState } from "react";
import Plot from "react-plotly.js";
import Plotly from "plotly.js-dist-min";
import GlassButton from "../components/GlassButton";
import GlassCard from "../components/GlassCard";
import StatChip from "../components/StatChip";
import { useI18n } from "../i18n/I18nContext";
import { getPlots } from "../lib/api";
import { highlightText } from "../lib/highlight";
import { plotLayoutBase } from "../lib/plotTheme";
import type { PlotGroup, PlotItem } from "../types/api";

type Props = {
  taskId: string;
};

const OPEN_KEY = (taskId: string) => `chart_open_${taskId}`;
const HEIGHT_KEY = "chart_plot_height";

const HEIGHT_OPTIONS = [280, 350, 420] as const;

function loadOpenState(taskId: string, groups: PlotGroup[]): Record<string, boolean> {
  try {
    const raw = localStorage.getItem(OPEN_KEY(taskId));
    if (raw) return JSON.parse(raw) as Record<string, boolean>;
  } catch {
    /* ignore */
  }
  return Object.fromEntries(groups.map((g) => [g.group, true]));
}

function loadChartHeight(): number {
  try {
    const n = Number(localStorage.getItem(HEIGHT_KEY));
    if (HEIGHT_OPTIONS.includes(n as (typeof HEIGHT_OPTIONS)[number])) return n;
  } catch {
    /* ignore */
  }
  return 350;
}

function PlotCard({
  plot,
  theme,
  heightPx,
  keyword,
}: {
  plot: PlotItem;
  theme: "light" | "dark";
  heightPx: number;
  keyword: string;
}) {
  const graphRef = useRef<HTMLElement | null>(null);
  const { t } = useI18n();
  const baseLayout = plotLayoutBase(theme);

  const exportPng = () => {
    if (!graphRef.current) return;
    Plotly.downloadImage(graphRef.current, { format: "png", filename: plot.id, width: 1200, height: 700 });
  };

  return (
    <div className="plot-shell">
      <div className="row between" style={{ marginBottom: 8 }}>
        <h4 className="section-title plot-title">{highlightText(plot.title, keyword)}</h4>
        <GlassButton variant="accent" onClick={exportPng}>
          {t("exportPng")}
        </GlassButton>
      </div>
      <div className="plot-canvas">
        <Plot
          data={plot.figure.data as never[]}
          layout={{
            ...(plot.figure.layout as object),
            ...baseLayout,
            title: { ...(baseLayout.title as object), text: plot.title },
          }}
          config={{ responsive: true, displaylogo: false, displayModeBar: true }}
          style={{ width: "100%", height: `${heightPx}px` }}
          onInitialized={(_figure: unknown, graphDiv: HTMLElement) => {
            graphRef.current = graphDiv;
          }}
          onUpdate={(_figure: unknown, graphDiv: HTMLElement) => {
            graphRef.current = graphDiv;
          }}
        />
      </div>
    </div>
  );
}

export default function ChartCenterPage({ taskId }: Props) {
  const { t, theme } = useI18n();
  const [groups, setGroups] = useState<PlotGroup[]>([]);
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const [keyword, setKeyword] = useState("");
  const [chartHeight, setChartHeight] = useState(loadChartHeight);

  useEffect(() => {
    if (!taskId) return;
    getPlots(taskId).then((p) => {
      setGroups(p.groups);
      setOpen(loadOpenState(taskId, p.groups));
    });
  }, [taskId]);

  useEffect(() => {
    if (!taskId || groups.length === 0) return;
    localStorage.setItem(OPEN_KEY(taskId), JSON.stringify(open));
  }, [open, taskId, groups.length]);

  useEffect(() => {
    localStorage.setItem(HEIGHT_KEY, String(chartHeight));
  }, [chartHeight]);

  const filteredGroups = useMemo(() => {
    const kw = keyword.trim().toLowerCase();
    return groups
      .map((g) => ({
        ...g,
        plots: g.plots.filter((p) => !kw || p.title.toLowerCase().includes(kw)),
      }))
      .filter((g) => g.plots.length > 0);
  }, [groups, keyword]);

  const totalPlots = groups.reduce((n, g) => n + g.plots.length, 0);
  const visiblePlots = filteredGroups.reduce((n, g) => n + g.plots.length, 0);

  const setAllOpen = (value: boolean) => {
    setOpen(Object.fromEntries(groups.map((g) => [g.group, value])));
  };

  const toggleGroup = (group: string) => {
    setOpen((o) => ({ ...o, [group]: !o[group] }));
  };

  if (!taskId) return <p className="muted">{t("chartsNeedTask")}</p>;

  return (
    <div className="column gap stagger">
      <GlassCard title={t("chartsTitle")} subtitle={t("chartsSubtitle")}>
        <div className="chart-summary-bar">
          <StatChip className="stat-chip-accent" label={t("groupCount")} value={String(groups.length)} />
          <StatChip label={t("plotCount")} value={String(totalPlots)} />
          <StatChip label={t("visibleCount")} value={String(visiblePlots)} />
          <StatChip label={t("filterKeyword")} value={keyword || "-"} />
        </div>
        <div className="chart-toolbar">
          <input
            className="chart-search"
            placeholder={t("searchPlaceholder")}
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <label className="chart-height-picker">
            {t("chartHeight")}
            <select value={chartHeight} onChange={(e) => setChartHeight(Number(e.target.value))}>
              {HEIGHT_OPTIONS.map((h) => (
                <option key={h} value={h}>
                  {h}px
                </option>
              ))}
            </select>
          </label>
          <div className="actions">
            <GlassButton variant="secondary" onClick={() => setAllOpen(true)}>
              {t("expandAll")}
            </GlassButton>
            <GlassButton variant="secondary" onClick={() => setAllOpen(false)}>
              {t("collapseAll")}
            </GlassButton>
          </div>
        </div>
      </GlassCard>

      {filteredGroups.length === 0 ? (
        <GlassCard>
          <p className="muted">{t("noMatch")}</p>
        </GlassCard>
      ) : null}

      {filteredGroups.map((g) => (
        <section key={g.group} className="chart-group">
          <div className="chart-group-header">
            <div>
              <h3 className="chart-group-title">{highlightText(g.title, keyword)}</h3>
              <span className="chart-group-count">{g.plots.length} charts</span>
            </div>
            <GlassButton variant="secondary" onClick={() => toggleGroup(g.group)}>
              {open[g.group] ? t("collapse") : t("expand")}
            </GlassButton>
          </div>
          <div className={`collapse-panel ${open[g.group] ? "open" : ""}`}>
            <div className="collapse-panel-inner">
              {open[g.group] ? (
                <div className="chart-grid">
                  {g.plots.map((p) => (
                    <PlotCard key={p.id} plot={p} theme={theme} heightPx={chartHeight} keyword={keyword} />
                  ))}
                </div>
              ) : null}
            </div>
          </div>
        </section>
      ))}
    </div>
  );
}
