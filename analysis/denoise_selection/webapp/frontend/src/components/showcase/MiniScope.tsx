import { useEffect, useRef } from "react";
import { motionFlags, pointerStore } from "../../lib/pointerStore";

type Props = {
  variant?: "signal" | "amber";
  height?: number;
  freqMul?: number;
  className?: string;
};

export default function MiniScope({ variant = "signal", height = 48, freqMul = 1, className = "" }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    let t = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener("resize", resize);

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
      if (motionFlags.reduced) return;

      const mx = pointerStore.x;
      const my = pointerStore.y;
      const amp = h * 0.32 * (0.7 + my * 0.5);
      const freq = (0.022 + mx * 0.014) * freqMul;
      const phaseShift = (mx - 0.5) * Math.PI;
      t += 0.05;

      const colorVar = variant === "amber" ? "--amber" : "--signal";
      const color =
        getComputedStyle(document.documentElement).getPropertyValue(colorVar).trim() ||
        (variant === "amber" ? "#ffb020" : "#14f5c8");

      ctx.beginPath();
      for (let x = 0; x <= w; x += 2) {
        const n = Math.sin(x * freq + t + phaseShift) * 0.6;
        const y = h * 0.5 + n * amp;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = color;
      ctx.globalAlpha = pointerStore.active ? 0.75 : 0.45;
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.globalAlpha = 1;

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(raf);
    };
  }, [variant, freqMul]);

  return (
    <canvas
      ref={canvasRef}
      className={`mini-scope ${className}`.trim()}
      style={{ height: `${height}px` }}
      aria-hidden="true"
    />
  );
}
