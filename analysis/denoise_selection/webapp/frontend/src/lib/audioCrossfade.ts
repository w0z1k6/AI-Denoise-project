export function fadeVolumes(from: HTMLAudioElement, to: HTMLAudioElement, durationMs = 15): void {
  const start = performance.now();
  const fromStart = from.volume;
  const toStart = to.volume;
  const tick = (ts: number) => {
    const k = Math.min(1, (ts - start) / durationMs);
    from.volume = Math.max(0, fromStart * (1 - k));
    to.volume = Math.min(1, toStart + (1 - toStart) * k);
    if (k < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
