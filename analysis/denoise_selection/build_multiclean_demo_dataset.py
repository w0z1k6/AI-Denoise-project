import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def random_speed_change(x: np.ndarray, speed: float) -> np.ndarray:
    if len(x) < 4:
        return x
    src_idx = np.arange(len(x), dtype=np.float32)
    dst_len = max(8, int(len(x) / speed))
    dst_idx = np.linspace(0, len(x) - 1, dst_len, dtype=np.float32)
    y = np.interp(dst_idx, src_idx, x).astype(np.float32)
    return y


def simple_reverb(x: np.ndarray, sr: int, rt60: float) -> np.ndarray:
    ir_len = int(min(sr * 0.25, sr * max(0.05, rt60)))
    if ir_len < 8:
        return x
    t = np.arange(ir_len, dtype=np.float32) / sr
    decay = np.exp(-6.91 * t / max(rt60, 1e-3)).astype(np.float32)
    ir = decay
    ir[0] = 1.0
    y = np.convolve(x, ir, mode="full")[: len(x)].astype(np.float32)
    return y


def random_eq(x: np.ndarray, sr: int, rng: np.random.Generator) -> np.ndarray:
    y = x
    if rng.random() < 0.5:
        fc = float(rng.uniform(120.0, 1200.0))
        b, a = butter(1, fc / (sr / 2), btype="low")
        y = lfilter(b, a, y).astype(np.float32)
    if rng.random() < 0.5:
        fc = float(rng.uniform(1200.0, 4200.0))
        b, a = butter(1, fc / (sr / 2), btype="high")
        y = lfilter(b, a, y).astype(np.float32)
    return y


def pad_or_trim(x: np.ndarray, target_len: int) -> np.ndarray:
    if len(x) == target_len:
        return x
    if len(x) > target_len:
        return x[:target_len]
    out = np.zeros(target_len, dtype=np.float32)
    out[: len(x)] = x
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / "noisy_testset" / "clean_reference.wav"
    out_dir = Path(__file__).resolve().parent / "demo_dataset" / "clean"
    out_dir.mkdir(parents=True, exist_ok=True)

    clean, sr = sf.read(src)
    if clean.ndim > 1:
        clean = clean.mean(axis=1)
    clean = clean.astype(np.float32)

    rng = np.random.default_rng(2026)
    clips = []
    num_clips = 160
    clip_sec = 2.0
    clip_len = int(sr * clip_sec)

    for i in range(num_clips):
        if len(clean) > clip_len:
            s = int(rng.integers(0, len(clean) - clip_len))
            x = clean[s : s + clip_len].copy()
        else:
            x = pad_or_trim(clean, clip_len)

        speed = float(rng.uniform(0.9, 1.12))
        x = random_speed_change(x, speed)
        x = pad_or_trim(x, clip_len)

        x = random_eq(x, sr, rng)
        if rng.random() < 0.65:
            x = simple_reverb(x, sr, rt60=float(rng.uniform(0.06, 0.22)))

        gain_db = float(rng.uniform(-6.0, 4.0))
        gain = 10 ** (gain_db / 20.0)
        x = x * gain

        peak = float(np.max(np.abs(x)) + 1e-12)
        if peak > 0.98:
            x = x * (0.98 / peak)

        out_path = out_dir / f"clean_aug_{i:03d}.wav"
        sf.write(out_path, x.astype(np.float32), sr)
        clips.append(str(out_path))

    meta = {
        "source_clean": str(src),
        "num_clips": num_clips,
        "clip_seconds": clip_sec,
        "sample_rate": sr,
        "output_dir": str(out_dir),
    }
    meta_path = out_dir.parent / "dataset_meta.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Generated {num_clips} clips in: {out_dir}")
    print(f"Meta: {meta_path}")
    print(f"Mean RMS: {np.mean([rms(sf.read(p)[0]) for p in clips]):.6f}")


if __name__ == "__main__":
    main()
