export type PipelinePreset = {
  id: string;
  labelKey: string;
  route: string[];
  reason: string;
};

export const PIPELINE_PRESETS: PipelinePreset[] = [
  {
    id: "auto",
    labelKey: "showcasePresetAuto",
    route: ["analyze", "route", "denoise", "metrics"],
    reason: "scene-adaptive routing",
  },
  {
    id: "deepfilter",
    labelKey: "showcasePresetDeepfilter",
    route: ["deepfilter", "metrics"],
    reason: "DeepFilterNet3 teacher",
  },
  {
    id: "omlsa",
    labelKey: "showcasePresetOmlsa",
    route: ["base_omlsa_mcra", "metrics"],
    reason: "OM-LSA / MCRA core",
  },
  {
    id: "wpe",
    labelKey: "showcasePresetWpe",
    route: ["wpe", "base_omlsa_mcra", "metrics"],
    reason: "WPE dereverb + OM-LSA",
  },
  {
    id: "baseline",
    labelKey: "showcasePresetBaseline",
    route: ["noisereduce", "metrics"],
    reason: "library baseline",
  },
];

export const DEMO_METRICS = {
  sample_rate: 48000,
  length_sec: 12.4,
  method: "auto",
  route: ["analyze", "route", "denoise", "metrics"],
  reason: "demo telemetry",
  snr_db: { input_est: 8.24, output_est: 14.87, delta: 6.63 },
  rms: { residual: 0.002841 },
  residual_stats: { kurtosis: 2.91 },
};
