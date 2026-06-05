import { useEffect, type RefObject } from "react";
import { motionFlags, pointerStore } from "../lib/pointerStore";

const LERP = 0.09;
const IDLE_CENTER = { x: 0.5, y: 0.4 };

function setCoords(target: { x: number; y: number }, clientX: number, clientY: number) {
  target.x = clientX / window.innerWidth;
  target.y = clientY / window.innerHeight;
}

export function useStudioPointer(atmosphereRef: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const target = { ...IDLE_CENTER, active: false };
    const current = { ...IDLE_CENTER, active: false };
    let raf = 0;
    let idlePhase = 0;

    const applyToDom = () => {
      const el = atmosphereRef.current;
      if (!el) return;

      const px = current.x * 100;
      const py = current.y * 100;
      const dx = (current.x - 0.5) * 100;
      const dy = (current.y - 0.5) * 100;
      const gx = (current.x - 0.5) * 24;
      const gy = (current.y - 0.5) * 18 + motionFlags.scrollY * 0.04;
      const boost = motionFlags.processing ? 1.2 : 1;

      el.style.setProperty("--pointer-x", `${px}%`);
      el.style.setProperty("--pointer-y", `${py}%`);
      el.style.setProperty("--pointer-dx", String(dx));
      el.style.setProperty("--pointer-dy", String(dy));
      el.style.setProperty("--grid-shift-x", `${gx * boost}px`);
      el.style.setProperty("--grid-shift-y", `${gy}px`);
      el.style.setProperty("--scroll-parallax", `${motionFlags.scrollY * 0.08}px`);

      el.classList.toggle("studio-atmosphere-active", current.active);
      el.classList.toggle("studio-atmosphere-processing", motionFlags.processing);

      pointerStore.x = current.x;
      pointerStore.y = current.y;
      pointerStore.active = current.active;
    };

    const onMove = (clientX: number, clientY: number) => {
      setCoords(target, clientX, clientY);
      target.active = true;
    };

    const onMouseMove = (e: MouseEvent) => onMove(e.clientX, e.clientY);
    const onTouchMove = (e: TouchEvent) => {
      const t = e.touches[0];
      if (t) onMove(t.clientX, t.clientY);
    };

    const onLeave = () => {
      target.active = false;
      target.x = IDLE_CENTER.x;
      target.y = IDLE_CENTER.y;
    };

    const tick = () => {
      if (!motionFlags.visible || motionFlags.reduced) {
        raf = requestAnimationFrame(tick);
        return;
      }

      if (!target.active && !motionFlags.reduced) {
        idlePhase += motionFlags.processing ? 0.014 : 0.006;
        target.x = IDLE_CENTER.x + Math.sin(idlePhase) * 0.06;
        target.y = IDLE_CENTER.y + Math.cos(idlePhase * 0.85) * 0.04;
      }

      current.x += (target.x - current.x) * LERP;
      current.y += (target.y - current.y) * LERP;
      current.active = target.active;
      applyToDom();
      raf = requestAnimationFrame(tick);
    };

    if (!motionFlags.reduced) {
      window.addEventListener("mousemove", onMouseMove, { passive: true });
      window.addEventListener("mouseleave", onLeave);
      window.addEventListener("touchmove", onTouchMove, { passive: true });
      window.addEventListener("touchend", onLeave);
      applyToDom();
      raf = requestAnimationFrame(tick);
    } else {
      applyToDom();
    }

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseleave", onLeave);
      window.removeEventListener("touchmove", onTouchMove);
      window.removeEventListener("touchend", onLeave);
      cancelAnimationFrame(raf);
    };
  }, [atmosphereRef]);
}
