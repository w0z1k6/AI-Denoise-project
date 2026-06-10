const TARGET_SR = 16000;

export function downsampleTo16k(input: Float32Array, fromRate: number): Float32Array {
  if (fromRate === TARGET_SR) return input;
  const ratio = fromRate / TARGET_SR;
  const outLen = Math.floor(input.length / ratio);
  const out = new Float32Array(outLen);
  for (let i = 0; i < outLen; i += 1) {
    out[i] = input[Math.floor(i * ratio)] ?? 0;
  }
  return out;
}

export function float32ToPcmB64(samples: Float32Array): string {
  const ints = new Int16Array(samples.length);
  for (let i = 0; i < samples.length; i += 1) {
    const s = Math.max(-1, Math.min(1, samples[i] ?? 0));
    ints[i] = Math.round(s * 32767);
  }
  const bytes = new Uint8Array(ints.buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i] ?? 0);
  }
  return btoa(binary);
}

export function pcmB64ToFloat32(b64: string): Float32Array {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  const ints = new Int16Array(bytes.buffer);
  const out = new Float32Array(ints.length);
  for (let i = 0; i < ints.length; i += 1) {
    out[i] = (ints[i] ?? 0) / 32768;
  }
  return out;
}

export function rmsLevel(samples: Float32Array): number {
  if (samples.length === 0) return 0;
  let sum = 0;
  for (let i = 0; i < samples.length; i += 1) {
    const v = samples[i] ?? 0;
    sum += v * v;
  }
  return Math.sqrt(sum / samples.length);
}

export const CHUNK_SAMPLES = 8192;
export const TARGET_SAMPLE_RATE = TARGET_SR;
export const MAX_RECORD_SEC = 600;
