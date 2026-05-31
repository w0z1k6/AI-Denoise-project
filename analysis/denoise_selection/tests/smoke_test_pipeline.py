from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def run_cmd(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=str(cwd), check=False, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    run_pipeline = root / "analysis" / "denoise_selection" / "run_pipeline.py"
    scene = "scene01_white_snr15.wav"

    run_cmd([sys.executable, str(run_pipeline), "--scene", scene, "--force-method", "base_omlsa_mcra", "--out-dir", "analysis/denoise_selection/outputs/base"], root)
    run_cmd([sys.executable, str(run_pipeline), "--scene", scene, "--out-dir", "analysis/denoise_selection/outputs/routed"], root)

    out_base = root / "analysis" / "denoise_selection" / "outputs" / "base" / "scene01_white_snr15_routed.wav"
    out_routed = root / "analysis" / "denoise_selection" / "outputs" / "routed" / "scene01_white_snr15_routed.wav"
    for p in (out_base, out_routed):
        if not p.exists():
            raise FileNotFoundError(f"Missing output: {p}")
        x, _ = sf.read(p)
        if not np.isfinite(np.asarray(x)).all():
            raise ValueError(f"Non-finite output found: {p}")
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
