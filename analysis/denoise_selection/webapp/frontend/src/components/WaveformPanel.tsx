import { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";
import { useI18n } from "../i18n/I18nContext";
import GlassCard from "./GlassCard";

type Props = {
  url: string;
  title: string;
  onSeek?: (timeSec: number) => void;
};

export default function WaveformPanel({ url, title, onSeek }: Props) {
  const { theme } = useI18n();
  const boxRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WaveSurfer | null>(null);

  useEffect(() => {
    if (!boxRef.current) return;
    wsRef.current?.destroy();
    const waveColor = theme === "light" ? "#93c5fd" : "#6b8cff";
    const progressColor = theme === "light" ? "#2563eb" : "#2a4cff";
    wsRef.current = WaveSurfer.create({
      container: boxRef.current,
      url,
      waveColor,
      progressColor,
      height: 90,
    });
    wsRef.current.on("seeking", (p: number) => {
      const duration = wsRef.current?.getDuration() ?? 0;
      onSeek?.(p * duration);
    });
    return () => wsRef.current?.destroy();
  }, [url, onSeek, theme]);

  return (
    <GlassCard title={title}>
      <div ref={boxRef} />
    </GlassCard>
  );
}
