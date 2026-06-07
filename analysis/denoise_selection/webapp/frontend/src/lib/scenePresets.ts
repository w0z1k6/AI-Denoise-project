import type { DictKey } from "../i18n";

export type ScenePreset = {
  id: string;
  code: string;
  titleKey: DictKey;
  descKey: DictKey;
  tagKey: DictKey;
  snr: number;
  durationSec: number;
  methodPrefill: string;
  waveformSeed: number;
};

export const SCENE_PRESETS: ScenePreset[] = [
  {
    id: "chirp-snr8",
    code: "S09",
    titleKey: "sceneChirpTitle",
    descKey: "sceneChirpDesc",
    tagKey: "sceneTagChirp",
    snr: 8,
    durationSec: 5.2,
    methodPrefill: "auto",
    waveformSeed: 0.42,
  },
  {
    id: "bird-snr12",
    code: "S12",
    titleKey: "sceneBirdTitle",
    descKey: "sceneBirdDesc",
    tagKey: "sceneTagBird",
    snr: 12,
    durationSec: 8.0,
    methodPrefill: "deepfilter",
    waveformSeed: 0.18,
  },
  {
    id: "hum-snr6",
    code: "S06",
    titleKey: "sceneHumTitle",
    descKey: "sceneHumDesc",
    tagKey: "sceneTagHum",
    snr: 6,
    durationSec: 6.4,
    methodPrefill: "omlsa",
    waveformSeed: 0.71,
  },
  {
    id: "wind-snr10",
    code: "S14",
    titleKey: "sceneWindTitle",
    descKey: "sceneWindDesc",
    tagKey: "sceneTagWind",
    snr: 10,
    durationSec: 4.8,
    methodPrefill: "wpe",
    waveformSeed: 0.55,
  },
  {
    id: "speech-snr15",
    code: "S18",
    titleKey: "sceneSpeechTitle",
    descKey: "sceneSpeechDesc",
    tagKey: "sceneTagSpeech",
    snr: 15,
    durationSec: 3.6,
    methodPrefill: "auto",
    waveformSeed: 0.33,
  },
  {
    id: "baseline-snr5",
    code: "S03",
    titleKey: "sceneBaselineTitle",
    descKey: "sceneBaselineDesc",
    tagKey: "sceneTagNoise",
    snr: 5,
    durationSec: 7.2,
    methodPrefill: "baseline",
    waveformSeed: 0.89,
  },
];

export function applySceneToUpload(preset: ScenePreset): void {
  sessionStorage.setItem("upload_method_prefill", preset.methodPrefill);
  sessionStorage.setItem("upload_scene_hint", preset.id);
}
