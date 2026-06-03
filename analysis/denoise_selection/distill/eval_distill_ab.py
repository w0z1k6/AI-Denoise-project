from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), int(sr)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    pair_path = root / "analysis" / "denoise_selection" / "distill" / "distill_pairs.json"
    with pair_path.open("r", encoding="utf-8") as f:
        pairs = json.load(f)

    out_json = root / "analysis" / "denoise_selection" / "distill" / "distill_eval.json"
    out_md = root / "analysis" / "denoise_selection" / "distill" / "distill_eval.md"
    refined_dir = root / "analysis" / "denoise_selection" / "outputs" / "distill_refined"

    rows = {}
    for p in pairs:
        scene = p["scene"]
        clean, sr_c = load_mono(Path(p["clean_wav"]))
        routed, sr_r = load_mono(Path(p["math_input_wav"]))
        teacher, sr_t = load_mono(Path(p["teacher_wav"]))
        refined_path = refined_dir / Path(p["math_input_wav"]).name.replace("_routed.wav", "_distill_refined.wav")
        if not refined_path.exists():
            continue
        refined, sr_f = load_mono(refined_path)
        if len({sr_c, sr_r, sr_t, sr_f}) != 1:
            continue
        n = min(len(clean), len(routed), len(teacher), len(refined))
        c = clean[:n]
        routed_e = rms(routed[:n] - c)
        refined_e = rms(refined[:n] - c)
        teacher_e = rms(teacher[:n] - c)
        rows[scene] = {
            "routed_err_rms": routed_e,
            "distill_refined_err_rms": refined_e,
            "teacher_err_rms": teacher_e,
            "improve_vs_routed_rms": routed_e - refined_e,
            "gap_to_teacher_rms": refined_e - teacher_e,
        }

    summary = {
        "scene_count": len(rows),
        "better_than_routed_count": int(sum(v["improve_vs_routed_rms"] > 0 for v in rows.values())),
        "mean_improve_vs_routed_rms": float(np.mean([v["improve_vs_routed_rms"] for v in rows.values()])) if rows else 0.0,
    }
    payload = {"summary": summary, "scenes": rows}
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    lines = [
        "# Distillation AB Evaluation",
        "",
        f"- scene_count: {summary['scene_count']}",
        f"- better_than_routed_count: {summary['better_than_routed_count']}",
        f"- mean_improve_vs_routed_rms: {summary['mean_improve_vs_routed_rms']:.6f}",
        "",
        "| Scene | Routed RMS | Distill RMS | Teacher RMS | Improve |",
        "|---|---:|---:|---:|---:|",
    ]
    for scene, v in rows.items():
        lines.append(
            f"| {scene} | {v['routed_err_rms']:.6f} | {v['distill_refined_err_rms']:.6f} | {v['teacher_err_rms']:.6f} | {v['improve_vs_routed_rms']:.6f} |"
        )
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_md}")


if __name__ == "__main__":
    main()
