export type PlotTheme = "light" | "dark";

export function plotLayoutBase(theme: PlotTheme) {
  const isLight = theme === "light";
  return {
    autosize: true,
    paper_bgcolor: isLight ? "#f5f7fb" : "#1a2238",
    plot_bgcolor: isLight ? "#eef2f8" : "#141c30",
    font: {
      family: '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif',
      color: isLight ? "#1a2332" : "#e8edf8",
      size: 12,
    },
    title: { font: { size: 14, color: isLight ? "#0f172a" : "#f1f5ff" } },
    xaxis: {
      gridcolor: isLight ? "rgba(15, 23, 42, 0.08)" : "rgba(255,255,255,0.12)",
      linecolor: isLight ? "rgba(15, 23, 42, 0.2)" : "rgba(255,255,255,0.25)",
      tickfont: { color: isLight ? "#334155" : "#cbd5e1" },
      title: { font: { color: isLight ? "#1e293b" : "#e2e8f0" } },
    },
    yaxis: {
      gridcolor: isLight ? "rgba(15, 23, 42, 0.08)" : "rgba(255,255,255,0.12)",
      linecolor: isLight ? "rgba(15, 23, 42, 0.2)" : "rgba(255,255,255,0.25)",
      tickfont: { color: isLight ? "#334155" : "#cbd5e1" },
      title: { font: { color: isLight ? "#1e293b" : "#e2e8f0" } },
    },
    legend: {
      bgcolor: isLight ? "rgba(255,255,255,0.92)" : "rgba(26,34,56,0.92)",
      bordercolor: isLight ? "rgba(15,23,42,0.12)" : "rgba(255,255,255,0.15)",
      font: { color: isLight ? "#1e293b" : "#e2e8f0" },
    },
    margin: { l: 48, r: 24, t: 48, b: 40 },
  };
}
