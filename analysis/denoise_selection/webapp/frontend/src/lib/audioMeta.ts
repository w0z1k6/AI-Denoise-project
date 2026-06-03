export type AudioFileMeta = {
  name: string;
  sizeKb: number;
  durationSec: number | null;
  sampleRate: number | null;
};

export async function probeAudioFile(file: File): Promise<AudioFileMeta> {
  const base: AudioFileMeta = {
    name: file.name,
    sizeKb: Math.round(file.size / 1024),
    durationSec: null,
    sampleRate: null,
  };
  try {
    const ctx = new AudioContext();
    const buf = await file.arrayBuffer();
    const audio = await ctx.decodeAudioData(buf.slice(0));
    await ctx.close();
    return {
      ...base,
      durationSec: Math.round(audio.duration * 100) / 100,
      sampleRate: audio.sampleRate,
    };
  } catch {
    return base;
  }
}
