import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n/I18nContext";
import { fadeVolumes } from "../lib/audioCrossfade";
import GlassButton from "./GlassButton";
import RackPanel from "./RackPanel";

type Props = {
  originalUrl: string;
  denoisedUrl: string;
  residualUrl?: string;
};

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

  const channels: { key: "original" | "denoised" | "residual"; label: string; volKey: keyof typeof vol; show: boolean }[] = [
    { key: "original", label: t("trackOriginal"), volKey: "original", show: true },
    { key: "denoised", label: t("trackDenoised"), volKey: "denoised", show: true },
    { key: "residual", label: t("trackResidual"), volKey: "residual", show: !!residualUrl },
  ];

  return (
    <RackPanel moduleId="MOD-04" channel="A/B" led="active" title={t("audioTitle")} subtitle={t("audioSubtitle")}>
      <div className="mixer-transport">
        <GlassButton variant="primary" onClick={playPause}>
          {t("playPause")}
        </GlassButton>
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
      <div className="mixer-strip">
        {channels
          .filter((c) => c.show)
          .map((c) => (
            <div key={c.key} className={`mixer-channel ${active === c.key ? "is-active" : ""}`}>
              <div className="mixer-channel-head">
                <span className={`rack-led ${active === c.key ? "rack-led-active" : "rack-led-idle"}`} />
                <span>{c.label}</span>
              </div>
              <GlassButton
                variant={active === c.key ? "primary" : "secondary"}
                onClick={() => syncSwitch(c.key)}
              >
                {active === c.key ? "ON" : "SEL"}
              </GlassButton>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={vol[c.volKey]}
                onChange={(e) => setVol((v) => ({ ...v, [c.volKey]: Number(e.target.value) }))}
                aria-label={c.label}
              />
            </div>
          ))}
      </div>
      <audio ref={oRef} src={originalUrl} preload="auto" />
      <audio ref={dRef} src={denoisedUrl} preload="auto" />
      {residualUrl ? <audio ref={rRef} src={residualUrl} preload="auto" /> : null}
    </RackPanel>
  );
}
