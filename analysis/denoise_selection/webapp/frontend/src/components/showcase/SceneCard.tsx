import MiniScope from "./MiniScope";
import type { ScenePreset } from "../../lib/scenePresets";
import { useI18n } from "../../i18n/I18nContext";

type Props = {
  preset: ScenePreset;
  selected: boolean;
  onSelect: () => void;
};

export default function SceneCard({ preset, selected, onSelect }: Props) {
  const { t } = useI18n();

  return (
    <button
      type="button"
      className={`scene-card ${selected ? "is-selected" : ""}`}
      onClick={onSelect}
      aria-pressed={selected}
    >
      <span className="scene-card-code">{preset.code}</span>
      <span className="scene-card-tag">{t(preset.tagKey)}</span>
      <h4 className="scene-card-title">{t(preset.titleKey)}</h4>
      <p className="scene-card-desc">{t(preset.descKey)}</p>
      <div className="scene-card-meta">
        <span>SNR {preset.snr} dB</span>
        <span>{preset.durationSec}s</span>
      </div>
      <MiniScope height={36} freqMul={0.8 + preset.waveformSeed} variant={selected ? "signal" : "amber"} />
    </button>
  );
}
