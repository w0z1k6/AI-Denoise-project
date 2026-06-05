/** Shared pointer state — updated in rAF, read by canvas without React re-renders. */
export type PointerNorm = {
  x: number;
  y: number;
  active: boolean;
};

export const pointerStore: PointerNorm = { x: 0.5, y: 0.4, active: false };

export type MotionFlags = {
  reduced: boolean;
  mobile: boolean;
  visible: boolean;
  processing: boolean;
  scrollY: number;
};

export const motionFlags: MotionFlags = {
  reduced:
    typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  mobile: typeof window !== "undefined" && window.matchMedia("(max-width: 768px)").matches,
  visible: true,
  processing: false,
  scrollY: 0,
};
