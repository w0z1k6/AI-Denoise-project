import { useEffect, useRef, useState, type CSSProperties } from "react";
import { motionFlags } from "../lib/pointerStore";

type PowerState = "pending" | "powering" | "powered";

export function useRackPowerOn(moduleId: string, powerDelay = 0) {
  const ref = useRef<HTMLElement>(null);
  const [state, setState] = useState<PowerState>("pending");

  useEffect(() => {
    if (motionFlags.reduced) {
      setState("powered");
      return;
    }

    const seenKey = `rack-seen-${moduleId}`;
    if (sessionStorage.getItem(seenKey)) {
      setState("powered");
      return;
    }

    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        setState("powering");
        sessionStorage.setItem(seenKey, "1");
        window.setTimeout(() => setState("powered"), 720 + powerDelay);
        observer.disconnect();
      },
      { threshold: 0.2 },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [moduleId, powerDelay]);

  const className =
    state === "powering" ? "rack-powering" : state === "powered" ? "rack-powered" : "";

  return {
    ref,
    className,
    style: { "--rack-power-delay": `${powerDelay}ms` } as CSSProperties,
  };
}
