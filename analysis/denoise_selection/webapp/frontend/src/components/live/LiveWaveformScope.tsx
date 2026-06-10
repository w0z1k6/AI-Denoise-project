import { useEffect, useRef } from "react";
import { motionFlags } from "../../lib/pointerStore";

type Props = {
  analyser: AnalyserNode | null;
  recording?: boolean;
  idleHint?: string;
  className?: string;
  height?: number;
};

function drawGrid(ctx: CanvasRenderingContext2D, w: number, h: number) {
  const gridColor =
    getComputedStyle(document.documentElement).getPropertyValue("--live-scope-grid").trim() || "rgba(0,0,0,0.06)";
  const centerColor =
    getComputedStyle(document.documentElement).getPropertyValue("--live-scope-center").trim() || "rgba(0,0,0,0.1)";

  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 1;
  ctx.globalAlpha = 1;

  const stepX = Math.max(24, Math.floor(w / 16));
  const stepY = Math.max(16, Math.floor(h / 6));
  for (let x = 0; x <= w; x += stepX) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 0; y <= h; y += stepY) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  ctx.strokeStyle = centerColor;
  ctx.beginPath();
  ctx.moveTo(0, h / 2);
  ctx.lineTo(w, h / 2);
  ctx.stroke();
}

export default function LiveWaveformScope({
  analyser,
  recording = false,
  idleHint = "",
  className = "",
  height = 96,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const data = new Uint8Array(analyser?.fftSize ?? 2048);
    let raf = 0;

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
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (w === 0 || h === 0) {
        raf = requestAnimationFrame(draw);
        return;
      }

      const bg = getComputedStyle(document.documentElement).getPropertyValue("--live-scope-bg").trim();
      if (bg) {
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, w, h);
      } else {
        ctx.clearRect(0, 0, w, h);
      }

      drawGrid(ctx, w, h);

      if (!analyser || motionFlags.reduced) {
        if (idleHint && !recording) {
          ctx.font = "600 11px Fragment Mono, monospace";
          ctx.fillStyle =
            getComputedStyle(document.documentElement).getPropertyValue("--text-tertiary").trim() || "#888";
          ctx.textAlign = "center";
          ctx.fillText(idleHint, w / 2, h / 2 + 4);
        }
        raf = requestAnimationFrame(draw);
        return;
      }

      analyser.getByteTimeDomainData(data);
      const color = getComputedStyle(document.documentElement).getPropertyValue("--signal").trim() || "#14f5c8";
      const glow = getComputedStyle(document.documentElement).getPropertyValue("--signal-glow").trim() || color;

      ctx.beginPath();
      const slice = w / data.length;
      const t = Date.now() / 16;
      for (let i = 0; i < data.length; i += 1) {
        const v = (data[i] ?? 128) / 128 - 1;
        const y = h / 2 + v * (h * 0.42);
        const x = recording ? ((t + i * slice) % w) : i * slice;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      if (recording) {
        ctx.shadowColor = glow;
        ctx.shadowBlur = 8;
      }
      ctx.strokeStyle = color;
      ctx.globalAlpha = recording ? 0.92 : 0.62;
      ctx.lineWidth = recording ? 2 : 1.5;
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.globalAlpha = 1;

      if (recording) {
        const scanX = t % w;
        ctx.strokeStyle = color;
        ctx.globalAlpha = 0.18;
        ctx.beginPath();
        ctx.moveTo(scanX, 0);
        ctx.lineTo(scanX, h);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(raf);
    };
  }, [analyser, recording, idleHint]);

  return (
    <div className={`live-scope-frame ${recording ? "is-recording" : ""} ${className}`.trim()}>
      <span className="live-scope-corner live-scope-corner-tl" aria-hidden="true" />
      <span className="live-scope-corner live-scope-corner-tr" aria-hidden="true" />
      <span className="live-scope-corner live-scope-corner-bl" aria-hidden="true" />
      <span className="live-scope-corner live-scope-corner-br" aria-hidden="true" />
      <canvas ref={canvasRef} className="live-waveform-scope" style={{ height: `${height}px` }} aria-hidden="true" />
    </div>
  );
}
