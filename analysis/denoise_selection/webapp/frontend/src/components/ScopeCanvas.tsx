import { useEffect, useRef } from "react";
import { motionFlags, pointerStore } from "../lib/pointerStore";

export default function ScopeCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    let t = 0;
    const barHeights = Array.from({ length: 48 }, () => 0.3);

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener("resize", resize);

    const drawSpectrum = (w: number, h: number, mx: number, boost: number) => {
      const cols = motionFlags.mobile ? 28 : 48;
      const gap = w / cols;
      const signal =
        getComputedStyle(document.documentElement).getPropertyValue("--signal").trim() || "#14f5c8";

      for (let i = 0; i < cols; i++) {
        const target =
          0.15 +
          Math.abs(Math.sin(t * 0.8 + i * 0.22 + mx * 2)) * 0.55 * boost +
          Math.abs(Math.cos(i * 0.15 - mx)) * 0.12;
        barHeights[i % barHeights.length] += (target - barHeights[i % barHeights.length]) * 0.08;
        const bh = barHeights[i % barHeights.length] * h * 0.42;
        const x = i * gap + gap * 0.2;
        ctx.fillStyle = signal;
        ctx.globalAlpha = 0.12 + (i / cols) * 0.08;
        ctx.fillRect(x, h - bh, gap * 0.55, bh);
      }
      ctx.globalAlpha = 1;
    };

    const draw = () => {
      if (!motionFlags.visible) {
        raf = requestAnimationFrame(draw);
        return;
      }

      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (w === 0 || h === 0) {
        raf = requestAnimationFrame(draw);
        return;
      }

      ctx.clearRect(0, 0, w, h);

      const mx = pointerStore.x;
      const my = pointerStore.y;
      const boost = motionFlags.processing ? 1.2 : 1;
      const ampBase = h * 0.22 * boost;
      const amp = ampBase * (0.65 + my * 0.7);
      const phaseShift = (mx - 0.5) * Math.PI * 1.6;
      const freq = 0.018 + mx * 0.012;

      if (!motionFlags.reduced && !motionFlags.mobile) {
        drawSpectrum(w, h, mx, boost);
      }

      if (motionFlags.reduced) return;

      t += motionFlags.processing ? 0.065 : 0.045;

      const drawWave = (color: string, alpha: number, yOff: number, speed: number) => {
        ctx.beginPath();
        const step = motionFlags.mobile ? 5 : 3;
        for (let x = 0; x <= w; x += step) {
          const n = Math.sin(x * freq + t * speed + phaseShift) * 0.55;
          const n2 = Math.sin(x * freq * 2.3 - t * speed * 0.7) * 0.18;
          const y = h * 0.5 + yOff + (n + n2) * amp;
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = color;
        ctx.globalAlpha = alpha;
        ctx.lineWidth = motionFlags.mobile ? 1.2 : 1.5;
        ctx.stroke();
        ctx.globalAlpha = 1;
      };

      const signal =
        getComputedStyle(document.documentElement).getPropertyValue("--signal").trim() || "#14f5c8";
      const amber =
        getComputedStyle(document.documentElement).getPropertyValue("--amber").trim() || "#ffb020";

      const activeBoost = pointerStore.active ? 1.18 : 1;
      drawWave(signal, (pointerStore.active ? 0.55 : 0.35) * activeBoost, -8, 1);
      drawWave(amber, (pointerStore.active ? 0.28 : 0.16) * activeBoost, 14, 1.35);

      if (!motionFlags.reduced) raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(raf);
    };
  }, []);

  return <canvas ref={canvasRef} className="studio-scope-canvas" aria-hidden="true" />;
}
