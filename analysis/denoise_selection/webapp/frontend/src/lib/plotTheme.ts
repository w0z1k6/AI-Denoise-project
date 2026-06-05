export type PlotTheme = "light" | "dark";

const SIGNAL_PRIMARY = "#007a62";
const SIGNAL_SECONDARY = "#c47a00";

export function plotLayoutBase(theme: PlotTheme) {
  const isLight = theme === "light";
  return {
    autosize: true,
    paper_bgcolor: isLight ? "#fafbfc" : "#1a2238",
    plot_bgcolor: isLight ? "#fafbfc" : "#141c30",
    font: {
      family: '"Fragment Mono", "Cascadia Code", Consolas, monospace',
      color: isLight ? "#0a0f18" : "#e8edf8",
      size: 12,
    },
    title: { font: { size: 14, color: isLight ? "#0a0f18" : "#f1f5ff" } },
    colorway: [SIGNAL_PRIMARY, SIGNAL_SECONDARY, "#4db8ff", "#ff5c6a", "#5c6d82"],
    xaxis: {
      gridcolor: isLight ? "#e2e8f0" : "rgba(255,255,255,0.12)",
      linecolor: isLight ? "rgba(10, 15, 24, 0.18)" : "rgba(255,255,255,0.25)",
      tickfont: { color: isLight ? "#3d4a5c" : "#cbd5e1" },
      title: { font: { color: isLight ? "#0a0f18" : "#e2e8f0" } },
    },
    yaxis: {
      gridcolor: isLight ? "#e2e8f0" : "rgba(255,255,255,0.12)",
      linecolor: isLight ? "rgba(10, 15, 24, 0.18)" : "rgba(255,255,255,0.25)",
      tickfont: { color: isLight ? "#3d4a5c" : "#cbd5e1" },
      title: { font: { color: isLight ? "#0a0f18" : "#e2e8f0" } },
    },
    legend: {
      bgcolor: isLight ? "rgba(255,255,255,0.92)" : "rgba(26,34,56,0.92)",
      bordercolor: isLight ? "rgba(10,15,24,0.12)" : "rgba(255,255,255,0.15)",
      font: { color: isLight ? "#0a0f18" : "#e2e8f0" },
    },
    margin: { l: 48, r: 24, t: 48, b: 40 },
  };
}
