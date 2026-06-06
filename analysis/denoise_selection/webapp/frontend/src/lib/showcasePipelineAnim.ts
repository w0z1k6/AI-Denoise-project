/** Stagger-lit pipeline nodes from index 0 .. stepCount-1. Returns cleanup. */
export function animatePipelineSteps(
  stepCount: number,
  onStep: (litIndex: number) => void,
  intervalMs = 80,
): () => void {
  if (stepCount <= 0) {
    onStep(-1);
    return () => undefined;
  }
  let i = -1;
  onStep(-1);
  const timer = window.setInterval(() => {
    i += 1;
    onStep(i);
    if (i >= stepCount - 1) window.clearInterval(timer);
  }, intervalMs);
  return () => window.clearInterval(timer);
}
