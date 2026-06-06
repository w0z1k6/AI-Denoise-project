from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from algorithms import (
    adaptive_notch_bank,
    base_omlsa_mcra,
    chirp_notch,
    kalman_ar,
    nmf_denoise,
    subspace_denoise,
    wpe_omlsa,
)
from algorithms.common import ensure_parent, load_audio_mono, save_audio
from router import choose_route


METHODS: dict[str, Callable] = {
    "base_omlsa_mcra": base_omlsa_mcra,
    "wpe_omlsa": wpe_omlsa,
    "nmf_denoise": nmf_denoise,
    "kalman_ar": kalman_ar,
    "subspace_denoise": subspace_denoise,
    "adaptive_notch_bank": adaptive_notch_bank,
    "chirp_notch": chirp_notch,
}


def list_scenes(noisy_dir: Path) -> list[Path]:
    return sorted(
        [p for p in noisy_dir.glob("[sa]*.wav") if p.name.lower() != "clean_reference.wav"],
        key=lambda p: p.name,
    )


def run_one(in_path: Path, out_dir: Path, project_root: Path, force_method: str | None) -> dict:
    x, sr = load_audio_mono(in_path)
    decision = choose_route(in_path.name, project_root, force_method=force_method)
    y = x
    for method in decision.chain:
        fn = METHODS.get(method)
        if fn is None:
            raise KeyError(f"Unknown method: {method}")
        y = fn(y, sr)

    out_path = out_dir / in_path.name.replace(".wav", "_routed.wav")
    ensure_parent(out_path)
    save_audio(out_path, y, sr)
    return {
        "input": str(in_path),
        "output": str(out_path),
        "route_name": decision.route_name,
        "chain": decision.chain,
        "reason": decision.reason,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-method denoise router pipeline")
    parser.add_argument("--scene", type=str, default=None, help="Single scene wav filename")
    parser.add_argument("--all", action="store_true", help="Process all scene*.wav files")
    parser.add_argument("--force-method", type=str, default=None, choices=sorted(METHODS.keys()))
    parser.add_argument("--out-dir", type=str, default="analysis/denoise_selection/outputs/routed")
    parser.add_argument("--log-json", type=str, default="analysis/denoise_selection/outputs/route_log.json")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    noisy_dir = project_root / "noisy_testset"
    out_dir = project_root / args.out_dir
    log_path = project_root / args.log_json

    if not args.all and not args.scene:
        raise ValueError("Use --scene <file.wav> or --all")

    inputs: list[Path] = []
    if args.all:
        inputs.extend(list_scenes(noisy_dir))
    if args.scene:
        p = noisy_dir / args.scene
        if not p.exists():
            raise FileNotFoundError(f"Scene not found: {p}")
        if p not in inputs:
            inputs.append(p)

    logs = []
    for p in inputs:
        rec = run_one(p, out_dir, project_root, args.force_method)
        logs.append(rec)
        print(f"[OK] {p.name} -> {Path(rec['output']).name} via {rec['chain']}")

    ensure_parent(log_path)
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"Saved log: {log_path}")


if __name__ == "__main__":
    main()
