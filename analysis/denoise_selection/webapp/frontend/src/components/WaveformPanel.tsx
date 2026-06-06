import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import { useI18n } from "../i18n/I18nContext";
import GlassCard from "./GlassCard";

type Props = {
  url: string;
  title: string;
  onSeek?: (timeSec: number) => void;
};

export default function WaveformPanel({ url, title, onSeek }: Props) {
  const { theme, t } = useI18n();
  const boxRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WaveSurfer | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!boxRef.current) return;
    setLoading(true);
    wsRef.current?.destroy();
    const waveColor = theme === "light" ? "rgba(0, 122, 98, 0.35)" : "rgba(20, 245, 200, 0.35)";
    const progressColor = theme === "light" ? "#007a62" : "#14f5c8";
    wsRef.current = WaveSurfer.create({
      container: boxRef.current,
      url,
      waveColor,
      progressColor,
      height: 90,
    });
    wsRef.current.on("ready", () => setLoading(false));
    wsRef.current.on("error", () => setLoading(false));
    wsRef.current.on("seeking", (p: number) => {
      const duration = wsRef.current?.getDuration() ?? 0;
      onSeek?.(p * duration);
    });
    return () => {
      wsRef.current?.destroy();
      wsRef.current = null;
    };
  }, [url, onSeek, theme]);

  return (
    <GlassCard title={title} className="rack-no-corner-led">
      <div className="wave-host-wrap">
        {loading ? (
          <>
            <p className="wave-scan-label">{t("waveScanning")}</p>
            <div className="wave-skeleton" aria-hidden="true" />
          </>
        ) : null}
        <div ref={boxRef} className="wave-host" />
      </div>
    </GlassCard>
  );
}
