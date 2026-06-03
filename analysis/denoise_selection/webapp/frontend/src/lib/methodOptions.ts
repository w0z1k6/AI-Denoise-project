export type MethodGroupId = "recommended" | "math" | "dl" | "baseline";

export type MethodOption = {
  value: string;
  group: MethodGroupId;
  labelKey: string;
  hintKey: string;
};

export const METHOD_OPTIONS: MethodOption[] = [
  { value: "auto", group: "recommended", labelKey: "methodAuto", hintKey: "methodAutoHint" },
  {
    value: "deepfilter",
    group: "dl",
    labelKey: "methodDeepfilter",
    hintKey: "methodDeepfilterHint",
  },
  {
    value: "base_omlsa_mcra",
    group: "math",
    labelKey: "methodOmlsa",
    hintKey: "methodOmlsaHint",
  },
  { value: "wpe_omlsa", group: "math", labelKey: "methodWpe", hintKey: "methodWpeHint" },
  {
    value: "subspace_denoise",
    group: "math",
    labelKey: "methodSubspace",
    hintKey: "methodSubspaceHint",
  },
  { value: "nmf_denoise", group: "math", labelKey: "methodNmf", hintKey: "methodNmfHint" },
  { value: "kalman_ar", group: "math", labelKey: "methodKalman", hintKey: "methodKalmanHint" },
  { value: "chirp_notch", group: "math", labelKey: "methodChirp", hintKey: "methodChirpHint" },
  {
    value: "noisereduce",
    group: "baseline",
    labelKey: "methodNoisereduce",
    hintKey: "methodNoisereduceHint",
  },
  { value: "wiener", group: "baseline", labelKey: "methodWiener", hintKey: "methodWienerHint" },
  { value: "omlsa", group: "baseline", labelKey: "methodOmlsaShort", hintKey: "methodOmlsaHint" },
];

export const METHOD_GROUP_ORDER: MethodGroupId[] = ["recommended", "math", "dl", "baseline"];

export function methodHintKey(value: string): string {
  return METHOD_OPTIONS.find((m) => m.value === value)?.hintKey ?? "";
}

export function usesNoisereduceStrength(method: string): boolean {
  return method === "noisereduce";
}
