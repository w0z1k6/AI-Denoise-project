import { useEffect, useState } from "react";
import { motionFlags } from "../lib/pointerStore";

type Ripple = { id: number; x: number; y: number };

export default function ClickRipples() {
  const [ripples, setRipples] = useState<Ripple[]>([]);

  useEffect(() => {
    if (motionFlags.reduced) return;

    const add = (clientX: number, clientY: number) => {
      const id = Date.now() + Math.random();
      setRipples((prev) => [...prev.slice(-4), { id, x: clientX, y: clientY }]);
      window.setTimeout(() => {
        setRipples((prev) => prev.filter((r) => r.id !== id));
      }, 1200);
    };

    const onDown = (e: MouseEvent) => add(e.clientX, e.clientY);
    const onTouch = (e: TouchEvent) => {
      const t = e.touches[0];
      if (t) add(t.clientX, t.clientY);
    };

    window.addEventListener("mousedown", onDown);
    window.addEventListener("touchstart", onTouch, { passive: true });
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("touchstart", onTouch);
    };
  }, []);

  if (ripples.length === 0) return null;

  return (
    <div className="studio-ripples" aria-hidden="true">
      {ripples.map((r) => (
        <span
          key={r.id}
          className="studio-ripple"
          style={{ left: r.x, top: r.y }}
        />
      ))}
    </div>
  );
}
