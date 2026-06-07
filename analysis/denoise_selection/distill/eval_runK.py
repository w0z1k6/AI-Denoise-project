"""Evaluate runK student refiner vs routed baseline and teacher."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
PAIRS_PATH = ROOT / "analysis/denoise_selection/distill/distill_pairs.json"
RUNK_DIR = ROOT / "analysis/denoise_selection/outputs/distill_refined_runK"
OLD_DIR = ROOT / "analysis/denoise_selection/outputs/distill_refined"
OUT_JSON = ROOT / "analysis/denoise_selection/distill/distill_eval_runK.json"
OUT_MD = ROOT / "analysis/denoise_selection/distill/distill_eval_runK.md"


def load_mono(path: str | Path) -> np.ndarray:
    x, _ = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32)


def err_rms(clean: np.ndarray, est: np.ndarray) -> float:
    n = min(len(clean), len(est))
    return float(np.sqrt(np.mean((est[:n] - clean[:n]) ** 2) + 1e-12))


def snr_db(clean: np.ndarray, est: np.ndarray) -> float:
    n = min(len(clean), len(est))
    c, e = clean[:n], est[:n]
    err = e - c
    sig = np.sqrt(np.mean(c**2) + 1e-12)
    noise = np.sqrt(np.mean(err**2) + 1e-12) + 1e-12
    return float(20 * np.log10(sig / noise))


def main() -> None:
    pairs = json.loads(PAIRS_PATH.read_text(encoding="utf-8"))
    rows = []

    for p in pairs:
        scene = p["scene"]
        clean = load_mono(p["clean_wav"])
        noisy = load_mono(p["noisy_wav"])
        routed = load_mono(p["math_input_wav"])
        teacher = load_mono(p["teacher_wav"])

        runk_name = Path(p["math_input_wav"]).name.replace(
            "_routed.wav", "_distill_refined.wav"
        )
        runk = load_mono(RUNK_DIR / runk_name)

        row = {
            "scene": scene,
            "noisy_snr": snr_db(clean, noisy),
            "routed_snr": snr_db(clean, routed),
            "runK_snr": snr_db(clean, runk),
            "teacher_snr": snr_db(clean, teacher),
            "routed_err": err_rms(clean, routed),
            "runK_err": err_rms(clean, runk),
            "teacher_err": err_rms(clean, teacher),
            "improve_rms": err_rms(clean, routed) - err_rms(clean, runk),
        }

        old_path = OLD_DIR / runk_name
        if old_path.exists():
            old = load_mono(old_path)
            row["old_refined_snr"] = snr_db(clean, old)
            row["runK_vs_old_snr"] = row["runK_snr"] - row["old_refined_snr"]

        rows.append(row)

    summary = {
        "scene_count": len(rows),
        "mean_noisy_snr": float(np.mean([r["noisy_snr"] for r in rows])),
        "mean_routed_snr": float(np.mean([r["routed_snr"] for r in rows])),
        "mean_runK_snr": float(np.mean([r["runK_snr"] for r in rows])),
        "mean_teacher_snr": float(np.mean([r["teacher_snr"] for r in rows])),
        "mean_improve_rms_vs_routed": float(np.mean([r["improve_rms"] for r in rows])),
        "better_than_routed_count": int(sum(r["improve_rms"] > 0 for r in rows)),
    }
    if all("old_refined_snr" in r for r in rows):
        summary["mean_old_refined_snr"] = float(
            np.mean([r["old_refined_snr"] for r in rows])
        )
        summary["mean_runK_vs_old_snr"] = float(
            np.mean([r["runK_vs_old_snr"] for r in rows])
        )

    OUT_JSON.write_text(
        json.dumps({"summary": summary, "scenes": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# runK Distillation Evaluation",
        "",
        f"- scenes: {summary['scene_count']}",
        f"- mean noisy SNR: {summary['mean_noisy_snr']:.2f} dB",
        f"- mean routed SNR: {summary['mean_routed_snr']:.2f} dB",
        f"- mean runK refined SNR: {summary['mean_runK_snr']:.2f} dB",
        f"- mean teacher SNR: {summary['mean_teacher_snr']:.2f} dB",
        f"- better than routed: {summary['better_than_routed_count']}/{summary['scene_count']}",
        f"- mean RMS improve vs routed: {summary['mean_improve_rms_vs_routed']:.6f}",
        "",
        "| Scene | Noisy | Routed | runK | Teacher | RMS improve |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['scene']} | {r['noisy_snr']:.1f} | {r['routed_snr']:.1f} | "
            f"{r['runK_snr']:.1f} | {r['teacher_snr']:.1f} | {r['improve_rms']:.6f} |"
        )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    legacy_path = ROOT / "analysis/denoise_selection/distill/distill_eval.json"
    legacy_scenes = {}
    for r in rows:
        legacy_scenes[r["scene"]] = {
            "routed_err_rms": r["routed_err"],
            "distill_refined_err_rms": r["runK_err"],
            "teacher_err_rms": r["teacher_err"],
            "improve_vs_routed_rms": r["improve_rms"],
            "gap_to_teacher_rms": r["runK_err"] - r["teacher_err"],
            "noisy_snr_db": r["noisy_snr"],
            "routed_snr_db": r["routed_snr"],
            "distill_refined_snr_db": r["runK_snr"],
            "teacher_snr_db": r["teacher_snr"],
        }
    legacy = {
        "summary": {
            "scene_count": summary["scene_count"],
            "better_than_routed_count": summary["better_than_routed_count"],
            "mean_improve_vs_routed_rms": summary["mean_improve_rms_vs_routed"],
            "checkpoint_tag": "runK",
            "mean_noisy_snr_db": summary["mean_noisy_snr"],
            "mean_routed_snr_db": summary["mean_routed_snr"],
            "mean_distill_refined_snr_db": summary["mean_runK_snr"],
            "mean_teacher_snr_db": summary["mean_teacher_snr"],
        },
        "scenes": legacy_scenes,
    }
    legacy_path.write_text(json.dumps(legacy, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved {OUT_JSON}")
    print(f"Saved {OUT_MD}")
    print(f"Saved {legacy_path}")


if __name__ == "__main__":
    main()
