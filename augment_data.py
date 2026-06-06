"""
扩增蒸馏数据:LibriSpeech 干净语音 x 现有噪声 → 更多训练样本
"""

import json
import random
from pathlib import Path

import numpy as np
import soundfile as sf

PROJECT_ROOT = Path(__file__).resolve().parent
NOISY_DIR = PROJECT_ROOT / "noisy_testset"
LIBS_DIR = PROJECT_ROOT / "data" / "LibriSpeech" / "dev-clean"
AUG_DIR = PROJECT_ROOT / "augmented_noisy"

MAX_CLEAN = 30
SNRS = [5, 10, 15]

random.seed(42)
np.random.seed(42)


def load_mono(path):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), sr


def mix_at_snr(clean, noise, target_snr):
    n = min(len(clean), len(noise))
    c, nz = clean[:n], noise[:n]
    clean_rms = np.sqrt(np.mean(c**2) + 1e-12)
    noise_rms = np.sqrt(np.mean(nz**2) + 1e-12)
    current_snr = 20 * np.log10(clean_rms / (noise_rms + 1e-12))
    scale = 10 ** ((current_snr - target_snr) / 20)
    mixed = c + nz * scale
    peak = np.max(np.abs(mixed))
    if peak > 0.99:
        mixed = mixed * (0.99 / peak)
    return mixed.astype(np.float32)


def extract_noise(scene_wav, clean_wav):
    noisy, sr_n = load_mono(scene_wav)
    clean, sr_c = load_mono(clean_wav)
    if sr_n != sr_c:
        return None
    n = min(len(noisy), len(clean))
    return (noisy[:n] - clean[:n]).astype(np.float32)


def main():
    print("=" * 50)
    print("扩增蒸馏数据")
    print("=" * 50)


    clean_ref = NOISY_DIR / "clean_reference.wav"
    scenes = sorted(p for p in NOISY_DIR.glob("scene*.wav")
                    if p.name != "clean_reference.wav")

    noises = []
    for sp in scenes:
        noise_type = sp.stem.split("_")[1]
        noise = extract_noise(sp, clean_ref)
        if noise is not None:
            noises.append((noise_type, noise))
            print(f"  [{noise_type}] {sp.name}")

    print(f"\n提取了 {len(noises)} 种噪声")


    if not LIBS_DIR.exists():
        print(f"[ERROR] 没找到 LibriSpeech: {LIBS_DIR}")
        return

    flacs = sorted(LIBS_DIR.rglob("*.flac"))
    print(f"找到 {len(flacs)} 个 FLAC")
    if MAX_CLEAN and len(flacs) > MAX_CLEAN:
        flacs = random.sample(flacs, MAX_CLEAN)


    AUG_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for flac in flacs:
        clean, sr = load_mono(flac)
        if sr != 16000:
            continue
        for noise_type, noise in noises:
            for snr in SNRS:
                count += 1
                name = f"aug{count:04d}_{noise_type}_snr{snr}"
                mixed = mix_at_snr(clean, noise, snr)
                sf.write(str(AUG_DIR / f"{name}.wav"), mixed, 16000)

    print(f"\n生成了 {count} 条扩增音频 → {AUG_DIR}/")

    print()
    print("=" * 50)
    print("下一步：")
    print("=" * 50)
    print("""
1. 把扩增文件复制到 noisy_testset:
   xcopy /E /I augmented_noisy\\*.wav noisy_testset\\

2. 跑路由 pipeline:
   python analysis/denoise_selection/run_pipeline.py --all

3. 重新生成 distill 数据:
   python analysis/denoise_selection/distill/build_distill_pairs.py

4. 重新训练:
   python analysis/denoise_selection/distill/train_student_distill.py --tag runF
""")


if __name__ == "__main__":
    main()