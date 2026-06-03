import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n/I18nContext";
import GlassButton from "./GlassButton";
import GlassCard from "./GlassCard";

type Props = {
  originalUrl: string;
  denoisedUrl: string;
  residualUrl?: string;
};

function fadeVolumes(from: HTMLAudioElement, to: HTMLAudioElement, durationMs = 15): void {
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

export default function AudioComparePlayer({ originalUrl, denoisedUrl, residualUrl }: Props) {
  const { t } = useI18n();
  const oRef = useRef<HTMLAudioElement>(null);
  const dRef = useRef<HTMLAudioElement>(null);
  const rRef = useRef<HTMLAudioElement>(null);
  const [active, setActive] = useState<"original" | "denoised" | "residual">("original");
  const [speed, setSpeed] = useState(1.0);
  const [loop, setLoop] = useState(false);
  const [vol, setVol] = useState({ original: 1, denoised: 1, residual: 1 });

  useEffect(() => {
    [oRef.current, dRef.current, rRef.current].forEach((a) => {
      if (a) {
        a.playbackRate = speed;
        a.loop = loop;
      }
    });
  }, [speed, loop]);

  useEffect(() => {
    if (oRef.current) oRef.current.volume = active === "original" ? vol.original : 0;
    if (dRef.current) dRef.current.volume = active === "denoised" ? vol.denoised : 0;
    if (rRef.current) rRef.current.volume = active === "residual" ? vol.residual : 0;
  }, [active, vol]);

  const getActive = () => {
    if (active === "original") return oRef.current;
    if (active === "denoised") return dRef.current;
    return rRef.current;
  };

  const syncSwitch = (next: "original" | "denoised" | "residual") => {
    const curr = getActive();
    if (!curr) return;
    const time = curr.currentTime;
    const playing = !curr.paused;
    let target: HTMLAudioElement | null = null;
    if (next === "original") target = oRef.current;
    if (next === "denoised") target = dRef.current;
    if (next === "residual") target = rRef.current;
    if (!target) return;
    target.currentTime = time;
    if (playing) target.play().catch(() => undefined);
    fadeVolumes(curr, target);
    setActive(next);
  };

  const playPause = async () => {
    const a = getActive();
    if (!a) return;
    if (a.paused) await a.play();
    else a.pause();
  };

  return (
    <GlassCard title={t("audioTitle")} subtitle={t("audioSubtitle")}>
      <div className="row gap">
        <GlassButton variant="primary" onClick={playPause}>
          {t("playPause")}
        </GlassButton>
        <GlassButton variant={active === "original" ? "primary" : "secondary"} onClick={() => syncSwitch("original")}>
          {t("trackOriginal")}
        </GlassButton>
        <GlassButton variant={active === "denoised" ? "primary" : "secondary"} onClick={() => syncSwitch("denoised")}>
          {t("trackDenoised")}
        </GlassButton>
        {residualUrl ? (
          <GlassButton variant={active === "residual" ? "primary" : "secondary"} onClick={() => syncSwitch("residual")}>
            {t("trackResidual")}
          </GlassButton>
        ) : null}
      </div>
      <div className="grid2" style={{ marginTop: "12px" }}>
        <label>
          {t("playbackSpeed")}
          <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))}>
            <option value={0.75}>0.75x</option>
            <option value={1.0}>1.0x</option>
            <option value={1.25}>1.25x</option>
          </select>
        </label>
        <label>
          {t("loopPlayback")} <input type="checkbox" checked={loop} onChange={(e) => setLoop(e.target.checked)} />
        </label>
      </div>
      <div className="grid3" style={{ marginTop: "12px" }}>
        <label>
          {t("volA")}{" "}
          <input type="range" min={0} max={1} step={0.01} value={vol.original} onChange={(e) => setVol((v) => ({ ...v, original: Number(e.target.value) }))} />
        </label>
        <label>
          {t("volB")}{" "}
          <input type="range" min={0} max={1} step={0.01} value={vol.denoised} onChange={(e) => setVol((v) => ({ ...v, denoised: Number(e.target.value) }))} />
        </label>
        <label>
          {t("volR")}{" "}
          <input type="range" min={0} max={1} step={0.01} value={vol.residual} onChange={(e) => setVol((v) => ({ ...v, residual: Number(e.target.value) }))} />
        </label>
      </div>
      <audio ref={oRef} src={originalUrl} preload="auto" />
      <audio ref={dRef} src={denoisedUrl} preload="auto" />
      {residualUrl ? <audio ref={rRef} src={residualUrl} preload="auto" /> : null}
    </GlassCard>
  );
}
