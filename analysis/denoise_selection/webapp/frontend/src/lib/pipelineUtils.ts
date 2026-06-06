export function isDeepfilterMismatch(method: string, route: string[], reason: string): boolean {
  if (method !== "deepfilter") return false;
  const routeOk = route.some((r) => r.toLowerCase().includes("deepfilter"));
  const reasonOk = reason.toLowerCase().includes("deepfilter");
  const fallback =
    reason.toLowerCase().includes("fallback") ||
    reason.toLowerCase().includes("unavailable") ||
    route.some((r) => r.includes("omlsa") && !routeOk);
  return !routeOk || fallback || (!reasonOk && reason.length > 0);
}

export function abbreviateTaskId(id: string, head = 5, tail = 4): string {
  if (!id || id.length <= head + tail + 1) return id || "—";
  return `${id.slice(0, head)}…${id.slice(-tail)}`;
}
