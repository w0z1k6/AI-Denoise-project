from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.stats import kurtosis


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), int(sr)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def align(*xs: np.ndarray) -> list[np.ndarray]:
    n = min(len(x) for x in xs)
    return [x[:n] for x in xs]


def evaluate_scene(clean: np.ndarray, noisy: np.ndarray, base: np.ndarray, routed: np.ndarray) -> dict[str, float]:
    clean, noisy, base, routed = align(clean, noisy, base, routed)
    noisy_err = noisy - clean
    base_err = base - clean
    routed_err = routed - clean
    return {
        "noisy_err_rms": rms(noisy_err),
        "base_err_rms": rms(base_err),
        "routed_err_rms": rms(routed_err),
        "improve_vs_noisy_rms": rms(noisy_err) - rms(routed_err),
        "improve_vs_base_rms": rms(base_err) - rms(routed_err),
        "noisy_err_kurtosis": float(kurtosis(noisy_err, fisher=False, bias=False)),
        "base_err_kurtosis": float(kurtosis(base_err, fisher=False, bias=False)),
        "routed_err_kurtosis": float(kurtosis(routed_err, fisher=False, bias=False)),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    noisy_dir = root / "noisy_testset"
    clean_path = noisy_dir / "clean_reference.wav"
    base_dir = root / "analysis" / "denoise_selection" / "outputs" / "base"
    routed_dir = root / "analysis" / "denoise_selection" / "outputs" / "routed"

    out_json = root / "analysis" / "denoise_selection" / "eval" / "batch_eval_metrics.json"
    out_md = root / "analysis" / "denoise_selection" / "eval" / "batch_eval_report.md"

    clean, sr_clean = load_mono(clean_path)
    rows: dict[str, dict[str, float]] = {}
    for scene in sorted(noisy_dir.glob("scene*.wav")):
        noisy, sr_n = load_mono(scene)
        base_path = base_dir / scene.name.replace(".wav", "_routed.wav")
        routed_path = routed_dir / scene.name.replace(".wav", "_routed.wav")
        if not base_path.exists() or not routed_path.exists():
            continue
        base, sr_b = load_mono(base_path)
        routed, sr_r = load_mono(routed_path)
        if len({sr_clean, sr_n, sr_b, sr_r}) != 1:
            continue
        rows[scene.stem] = evaluate_scene(clean, noisy, base, routed)

    summary = {
        "scene_count": len(rows),
        "better_than_base_count": int(sum(v["improve_vs_base_rms"] > 0 for v in rows.values())),
        "mean_improve_vs_base_rms": float(np.mean([v["improve_vs_base_rms"] for v in rows.values()])) if rows else 0.0,
    }
    payload = {"summary": summary, "scenes": rows}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    lines = [
        "# Batch Evaluation Report",
        "",
        f"- scene_count: {summary['scene_count']}",
        f"- better_than_base_count: {summary['better_than_base_count']}",
        f"- mean_improve_vs_base_rms: {summary['mean_improve_vs_base_rms']:.6f}",
        "",
        "| Scene | Base RMS | Routed RMS | Improve vs Base |",
        "|---|---:|---:|---:|",
    ]
    for k, v in rows.items():
        lines.append(
            f"| {k} | {v['base_err_rms']:.6f} | {v['routed_err_rms']:.6f} | {v['improve_vs_base_rms']:.6f} |"
        )
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_json}")
    print(f"Saved: {out_md}")


if __name__ == "__main__":
    main()
