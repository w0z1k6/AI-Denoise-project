from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def resolve_cli() -> str:
    for name in ("deepFilter", "deep-filter"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("DeepFilterNet CLI not found in PATH.")


def scene_files(noisy_dir: Path) -> list[Path]:
    return sorted(
        [p for p in noisy_dir.glob("scene*.wav") if p.name.lower() != "clean_reference.wav"],
        key=lambda p: p.name,
    )


def run_teacher(cli: str, model_dir: Path, in_wav: Path, teacher_out: Path) -> None:
    cmd = [
        cli,
        str(in_wav),
        "-o",
        str(teacher_out),
        "--no-suffix",
        "-m",
        str(model_dir),
    ]
    completed = subprocess.run(cmd, check=False, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"DeepFilterNet failed for {in_wav.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build distillation pairs from routed outputs and DeepFilterNet teacher.")
    parser.add_argument("--regen-teacher", action="store_true", help="Regenerate teacher outputs even if cached.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    denoise_dir = root / "analysis" / "denoise_selection"
    noisy_dir = root / "noisy_testset"
    routed_dir = denoise_dir / "outputs" / "routed"
    teacher_dir = denoise_dir / "distill" / "teacher"
    teacher_dir.mkdir(parents=True, exist_ok=True)
    pair_path = denoise_dir / "distill" / "distill_pairs.json"
    split_path = denoise_dir / "distill" / "distill_split.json"

    model_dir = denoise_dir / "models" / "DeepFilterNet3"
    if not model_dir.exists():
        raise FileNotFoundError(f"Missing model dir: {model_dir}")

    cli = resolve_cli()
    scenes = scene_files(noisy_dir)
    pairs = []
    for s in scenes:
        routed_wav = routed_dir / s.name.replace(".wav", "_routed.wav")
        if not routed_wav.exists():
            print(f"[SKIP] Missing routed output: {routed_wav}")
            continue

        teacher_wav = teacher_dir / s.name.replace(".wav", "_teacher.wav")
        if args.regen_teacher or not teacher_wav.exists():
            run_teacher(cli, model_dir, s, teacher_dir)
            generated = teacher_dir / s.name
            if generated.exists():
                generated.rename(teacher_wav)
        if not teacher_wav.exists():
            print(f"[SKIP] Missing teacher output: {teacher_wav}")
            continue

        pairs.append(
            {
                "scene": s.stem,
                "noisy_wav": str(s),
                "math_input_wav": str(routed_wav),
                "teacher_wav": str(teacher_wav),
                "clean_wav": str(noisy_dir / "clean_reference.wav"),
            }
        )
        print(f"[PAIR] {s.name}")

    with pair_path.open("w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    # deterministic split: first 80% train, last 20% val
    n = len(pairs)
    n_train = max(1, int(round(0.8 * n))) if n > 0 else 0
    split = {"train_scenes": [p["scene"] for p in pairs[:n_train]], "val_scenes": [p["scene"] for p in pairs[n_train:]]}
    with split_path.open("w", encoding="utf-8") as f:
        json.dump(split, f, ensure_ascii=False, indent=2)

    print(f"Saved: {pair_path}")
    print(f"Saved: {split_path}")
    print(f"pair_count: {len(pairs)}")


if __name__ == "__main__":
    main()
