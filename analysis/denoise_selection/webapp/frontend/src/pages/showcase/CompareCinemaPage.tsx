import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import WaveSurfer from "wavesurfer.js";
import GlassButton from "../../components/GlassButton";
import StatusBadge from "../../components/StatusBadge";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import VuMeterBar from "../../components/showcase/VuMeterBar";
import { useI18n } from "../../i18n/I18nContext";
import { audioUrl, getHistory } from "../../lib/api";
import { fadeVolumes } from "../../lib/audioCrossfade";
import type { TaskItem } from "../../types/api";

type Props = {
  taskId: string;
};

type Track = "original" | "denoised" | "residual";

export default function CompareCinemaPage({ taskId }: Props) {
  const { t, theme } = useI18n();
  const shellRef = useRef<HTMLDivElement>(null);
  const oBox = useRef<HTMLDivElement>(null);
  const dBox = useRef<HTMLDivElement>(null);
  const rBox = useRef<HTMLDivElement>(null);
  const oRef = useRef<HTMLAudioElement>(null);
  const dRef = useRef<HTMLAudioElement>(null);
  const rRef = useRef<HTMLAudioElement>(null);
  const [task, setTask] = useState<TaskItem | null>(null);
  const [active, setActive] = useState<Track>("original");
  const [playing, setPlaying] = useState(false);
  const [vu, setVu] = useState(0.4);
  const [residualOpen, setResidualOpen] = useState(false);
  const [keysHint, setKeysHint] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    getHistory()
      .then((items) => setTask(items.find((x) => x.task_id === taskId) ?? null))
      .catch(() => undefined);
  }, [taskId]);

  useEffect(() => {
    if (!taskId) return;
    const waveColor = theme === "light" ? "rgba(0, 122, 98, 0.35)" : "rgba(20, 245, 200, 0.35)";
    const progressColor = theme === "light" ? "#007a62" : "#14f5c8";
    const opts = { waveColor, progressColor, height: 80 };
    const instances: WaveSurfer[] = [];
    if (oBox.current) instances.push(WaveSurfer.create({ container: oBox.current, url: audioUrl(taskId, "original"), ...opts }));
    if (dBox.current) instances.push(WaveSurfer.create({ container: dBox.current, url: audioUrl(taskId, "denoised"), ...opts }));
    if (rBox.current && residualOpen)
      instances.push(WaveSurfer.create({ container: rBox.current, url: audioUrl(taskId, "residual"), ...opts }));
    return () => instances.forEach((w) => w.destroy());
  }, [taskId, theme, residualOpen]);

  useEffect(() => {
    if (oRef.current) oRef.current.volume = active === "original" ? 1 : 0;
    if (dRef.current) dRef.current.volume = active === "denoised" ? 1 : 0;
    if (rRef.current) rRef.current.volume = active === "residual" ? 1 : 0;
  }, [active]);

  useEffect(() => {
    const a = active === "original" ? oRef.current : active === "denoised" ? dRef.current : rRef.current;
    if (!a) return;
    const onTime = () => {
      const phase = (a.currentTime % 1) * Math.PI * 2;
      setVu(0.35 + Math.abs(Math.sin(phase)) * 0.45);
    };
    a.addEventListener("timeupdate", onTime);
    return () => a.removeEventListener("timeupdate", onTime);
  }, [active, playing]);

  useEffect(() => {
    if (!keysHint) return;
    const tmr = window.setTimeout(() => setKeysHint(false), 3000);
    return () => clearTimeout(tmr);
  }, [keysHint]);

  const getActiveEl = (): HTMLAudioElement | null => {
    if (active === "original") return oRef.current;
    if (active === "denoised") return dRef.current;
    return rRef.current;
  };

  const switchTrack = (next: Track) => {
    const curr = getActiveEl();
    if (!curr) return;
    const time = curr.currentTime;
    const wasPlaying = !curr.paused;
    let target: HTMLAudioElement | null = null;
    if (next === "original") target = oRef.current;
    if (next === "denoised") target = dRef.current;
    if (next === "residual") target = rRef.current;
    if (!target) return;
    target.currentTime = time;
    if (wasPlaying) target.play().catch(() => undefined);
    fadeVolumes(curr, target);
    setActive(next);
  };

  const togglePlay = async () => {
    const a = getActiveEl();
    if (!a) return;
    if (a.paused) {
      await a.play();
      setPlaying(true);
    } else {
      a.pause();
      setPlaying(false);
      setVu(0.2);
    }
  };

  useEffect(() => {
    const root = shellRef.current;
    if (!root || !taskId) return;
    root.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        togglePlay();
      }
      if (e.key === "1") switchTrack("original");
      if (e.key === "2") switchTrack("denoised");
      if (e.key === "3") {
        setResidualOpen(true);
        switchTrack("residual");
      }
    };
    root.addEventListener("keydown", onKey);
    return () => root.removeEventListener("keydown", onKey);
  });

  if (!taskId) {
    return (
      <div className="showcase-page showcase-page-inner stagger-fast">
        <ShowcaseSubNav />
        <ShowcasePageHeader
          variant="inner"
          moduleId="MOD-S04"
          channel="CINEMA"
          title={t("showcaseCinemaTitle")}
          subtitle={t("showcaseCinemaSubtitle")}
        />
        <div className="showcase-empty">
          <p>{t("showcaseNoTask")}</p>
          <Link to="/upload">
            <GlassButton variant="primary">{t("homeStart")}</GlassButton>
          </Link>
        </div>
      </div>
    );
  }

  const status = task?.status ?? "completed";

  return (
    <div
      ref={shellRef}
      className="showcase-page showcase-cinema-page showcase-cinema-immersive stagger-fast"
      tabIndex={0}
      aria-label={t("showcaseCinemaTitle")}
    >
      <div className="cinema-topbar">
        <div>
          <span className="rack-panel-id">MOD-S04 / CINEMA</span>
          <h3 className="section-title">{task?.filename ?? taskId}</h3>
          <p className="cinema-status" role="status" aria-live="polite">
            {playing ? t("showcaseCinemaPlaying") : t("showcaseCinemaPaused")}
          </p>
        </div>
        <div className="row gap">
          <StatusBadge status={status} />
          <Link to="/overview" className="glass-btn glass-btn-ghost">
            {t("showcaseCinemaBack")}
          </Link>
        </div>
      </div>
      <div className="cinema-shell">
        <VuMeterBar value={vu} vertical pulse={playing} />
        <div className="cinema-main">
          <div className="cinema-wave-row">
            <div className="cinema-wave-panel">
              <span className="monitor-label">{t("waveformOriginal")}</span>
              <div ref={oBox} className="cinema-wave-host" />
            </div>
            <div className="cinema-wave-panel">
              <span className="monitor-label">{t("waveformDenoised")}</span>
              <div ref={dBox} className="cinema-wave-host" />
            </div>
          </div>
          <div className={`cinema-residual-panel ${residualOpen ? "is-open" : ""}`}>
            <button type="button" className="cinema-residual-toggle" onClick={() => setResidualOpen((v) => !v)}>
              R — {t("trackResidual")} {residualOpen ? "▾" : "▸"}
            </button>
            {residualOpen ? <div ref={rBox} className="cinema-wave-host" /> : null}
          </div>
          <div className="mixer-transport">
            <GlassButton variant="primary" onClick={togglePlay}>
              {t("playPause")}
            </GlassButton>
          </div>
          <div className="mixer-strip cinema-mixer">
            {(
              [
                { key: "original" as const, label: t("trackOriginal") },
                { key: "denoised" as const, label: t("trackDenoised") },
                { key: "residual" as const, label: t("trackResidual") },
              ] as const
            ).map((c) => (
              <div key={c.key} className={`mixer-channel ${active === c.key ? "is-active" : ""}`}>
                <div className="mixer-channel-head">
                  <span className={`rack-led ${active === c.key ? "rack-led-active" : "rack-led-idle"}`} />
                  <span>{c.label}</span>
                </div>
                <GlassButton variant={active === c.key ? "primary" : "secondary"} onClick={() => switchTrack(c.key)}>
                  {active === c.key ? "ON" : "SEL"}
                </GlassButton>
              </div>
            ))}
          </div>
        </div>
        <VuMeterBar value={vu * 0.85} vertical pulse={playing} />
      </div>
      <div className={`cinema-keys-hint ${keysHint ? "is-prominent" : ""}`}>{t("showcaseCinemaKeys")}</div>
      <audio ref={oRef} src={audioUrl(taskId, "original")} preload="auto" />
      <audio ref={dRef} src={audioUrl(taskId, "denoised")} preload="auto" />
      <audio ref={rRef} src={audioUrl(taskId, "residual")} preload="auto" />
    </div>
  );
}
