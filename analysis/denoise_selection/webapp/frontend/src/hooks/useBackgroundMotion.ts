import { useEffect, useState } from "react";
import { getTask } from "../lib/api";
import { motionFlags } from "../lib/pointerStore";

export function useBackgroundMotion(taskId: string) {
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const reducedMq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const mobileMq = window.matchMedia("(max-width: 768px)");

    const sync = () => {
      motionFlags.reduced = reducedMq.matches;
      motionFlags.mobile = mobileMq.matches;
    };
    sync();
    reducedMq.addEventListener("change", sync);
    mobileMq.addEventListener("change", sync);

    const onVisibility = () => {
      motionFlags.visible = document.visibilityState === "visible";
    };
    document.addEventListener("visibilitychange", onVisibility);
    onVisibility();

    const onScroll = () => {
      motionFlags.scrollY = window.scrollY;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    return () => {
      reducedMq.removeEventListener("change", sync);
      mobileMq.removeEventListener("change", sync);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  useEffect(() => {
    if (!taskId) {
      setProcessing(false);
      motionFlags.processing = false;
      return;
    }
    let cancelled = false;
    const poll = async () => {
      try {
        const t = await getTask(taskId);
        if (cancelled) return;
        const busy = t.status === "processing" || t.status === "queued";
        setProcessing(busy);
        motionFlags.processing = busy;
      } catch {
        if (!cancelled) {
          setProcessing(false);
          motionFlags.processing = false;
        }
      }
    };
    poll();
    const id = window.setInterval(poll, 2000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [taskId]);

  return { processing, reduced: motionFlags.reduced, mobile: motionFlags.mobile };
}
