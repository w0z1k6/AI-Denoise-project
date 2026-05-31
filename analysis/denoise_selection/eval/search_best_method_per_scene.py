from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from algorithms import (
    adaptive_notch_bank,
    base_omlsa_mcra,
    chirp_notch,
    kalman_ar,
    nmf_denoise,
    subspace_denoise,
    wpe_omlsa,
)
from algorithms.common import load_audio_mono, rms


METHODS = {
    "base_omlsa_mcra": base_omlsa_mcra,
    "wpe_omlsa": wpe_omlsa,
    "nmf_denoise": nmf_denoise,
    "kalman_ar": kalman_ar,
    "subspace_denoise": subspace_denoise,
    "adaptive_notch_bank": adaptive_notch_bank,
    "chirp_notch": chirp_notch,
}


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    noisy_dir = root / "noisy_testset"
    clean_path = noisy_dir / "clean_reference.wav"
    out_json = root / "analysis" / "denoise_selection" / "eval" / "best_method_search.json"
    out_override = root / "analysis" / "denoise_selection" / "config" / "scene_method_overrides.json"

    clean, sr_c = load_audio_mono(clean_path)
    results = {}
    overrides = {}

    for scene in sorted(noisy_dir.glob("scene*.wav")):
        noisy, sr_n = load_audio_mono(scene)
        if sr_n != sr_c:
            continue
        n = min(len(clean), len(noisy))
        c = clean[:n]
        x = noisy[:n]

        scene_scores = {}
        best_name = None
        best_err = 1e18
        for name, fn in METHODS.items():
            try:
                y = fn(x, sr_n)
                m = min(len(y), n)
                err = rms(y[:m] - c[:m])
                scene_scores[name] = err
                if err < best_err:
                    best_err = err
                    best_name = name
            except Exception as e:
                scene_scores[name] = f"ERROR: {e}"

        base_err = scene_scores.get("base_omlsa_mcra")
        improve_vs_base = None
        if isinstance(base_err, float) and best_name is not None and isinstance(scene_scores[best_name], float):
            improve_vs_base = float(base_err - scene_scores[best_name])
        results[scene.name] = {
            "best_method": best_name,
            "best_err_rms": best_err if best_name else None,
            "base_err_rms": base_err,
            "improve_vs_base_rms": improve_vs_base,
            "all_methods_err_rms": scene_scores,
        }
        if best_name:
            overrides[scene.name] = best_name
        print(f"[SEARCH] {scene.name} best={best_name} err={best_err:.6f}")

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with out_override.open("w", encoding="utf-8") as f:
        json.dump(overrides, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_json}")
    print(f"Saved: {out_override}")


if __name__ == "__main__":
    main()
