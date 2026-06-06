import json
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Users\shackelten\AI-Denoise-project")
NOISY_DIR = ROOT / "noisy_testset"
ROUTED_DIR = ROOT / "analysis" / "denoise_selection" / "outputs" / "routed"
TEACHER_DIR = ROOT / "analysis" / "denoise_selection" / "distill" / "teacher"
DISTILL_DIR = ROOT / "analysis" / "denoise_selection" / "distill"
DEEPFILTER = ROOT / "deepFilter.exe"

TEACHER_DIR.mkdir(parents=True, exist_ok=True)

# 1. 跑 deepFilter 生成 teacher
noisy_wavs = sorted(p for p in NOISY_DIR.glob("[sa]*.wav")
                    if p.name != "clean_reference.wav")
print(f"共 {len(noisy_wavs)} 条音频")

for i, sp in enumerate(noisy_wavs):
    teacher_wav = TEACHER_DIR / sp.name.replace(".wav", "_teacher.wav")
    if teacher_wav.exists():
        print(f"  [{i+1}/{len(noisy_wavs)}] 跳过: {sp.name}")
        continue
    print(f"  [{i+1}/{len(noisy_wavs)}] deepFilter: {sp.name}...", end=" ", flush=True)
    cmd = [str(DEEPFILTER), str(sp), "-o", str(TEACHER_DIR)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"失败\n{r.stderr[:200]}")
        continue
    # 找到输出文件并改名
    out_file = TEACHER_DIR / sp.name
    if out_file.exists():
        out_file.rename(teacher_wav)
        print("OK")
    else:
        print("没找到输出")

# 2. 生成 distill_pairs.json
pairs = []
for sp in noisy_wavs:
    name = sp.stem
    routed = ROUTED_DIR / f"{name}_routed.wav"
    teacher = TEACHER_DIR / f"{name}_teacher.wav"
    clean = str(NOISY_DIR / "clean_reference.wav") if name.startswith("scene") else str(sp)
    pairs.append({
        "scene": name,
        "noisy_wav": str(sp),
        "math_input_wav": str(routed) if routed.exists() else str(sp),
        "teacher_wav": str(teacher) if teacher.exists() else str(sp),
        "clean_wav": clean,
    })

with open(DISTILL_DIR / "distill_pairs.json", "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

# 3. 生成 distill_split.json
orig = [p["scene"] for p in pairs if p["scene"].startswith("scene")]
aug = [p["scene"] for p in pairs if p["scene"].startswith("aug")]
n_train = max(1, int(0.8 * len(aug)))
split = {"train_scenes": orig + aug[:n_train], "val_scenes": aug[n_train:]}
with open(DISTILL_DIR / "distill_split.json", "w", encoding="utf-8") as f:
    json.dump(split, f, ensure_ascii=False, indent=2)

print(f"\n✅ distill_pairs.json ({len(pairs)} 条)")
print(f"✅ distill_split.json ({len(split['train_scenes'])} train + {len(split['val_scenes'])} val)")