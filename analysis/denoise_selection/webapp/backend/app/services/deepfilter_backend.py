from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class DeepFilterNetError(RuntimeError):
    """Raised when DeepFilterNet3 cannot be invoked successfully."""


def default_model_dir(denoise_root: Path) -> Path:
    explicit = os.getenv("DEEPFILTER_MODEL_DIR", "").strip()
    if explicit:
        return Path(explicit).resolve()
    return (denoise_root / "models" / "DeepFilterNet3").resolve()


def resolve_model_dir(denoise_root: Path, override: str | None) -> Path:
    if override and override.strip():
        model_dir = Path(override.strip()).resolve()
    else:
        model_dir = default_model_dir(denoise_root)
    if not model_dir.exists():
        raise DeepFilterNetError(
            f"DeepFilterNet3 model directory not found: {model_dir}. "
            "Download or place weights under analysis/denoise_selection/models/DeepFilterNet3."
        )
    ckpt_dir = model_dir / "checkpoints"
    if not ckpt_dir.exists() or not any(ckpt_dir.glob("*.ckpt*")):
        raise DeepFilterNetError(
            f"No checkpoints under {ckpt_dir}. Run download_df_model.py or copy DeepFilterNet3 weights."
        )
    return model_dir


def build_deepfilter_cmd(in_wav: Path, out_dir: Path, model_dir: Path) -> list[str]:
    """Build CLI argv. Prefer conda env (dfnet311) when DEEPFILTER_CONDA_ENV is set."""
    in_wav = in_wav.resolve()
    out_dir = out_dir.resolve()
    model_dir = model_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    tail = [
        str(in_wav),
        "-o",
        str(out_dir),
        "--no-suffix",
        "-m",
        str(model_dir),
    ]

    cli = os.getenv("DEEPFILTER_CLI", "").strip()
    if cli:
        return [cli, *tail]

    conda_env = os.getenv("DEEPFILTER_CONDA_ENV", "dfnet311").strip()
    conda = shutil.which("conda")
    if conda and conda_env:
        return [conda, "run", "-n", conda_env, "--no-capture-output", "deepFilter", *tail]

    for name in ("deepFilter", "deep-filter"):
        path = shutil.which(name)
        if path:
            return [path, *tail]

    raise DeepFilterNetError(
        "DeepFilterNet CLI not found. Install deepfilternet in conda env dfnet311 "
        "(pip install deepfilternet) and set DEEPFILTER_CONDA_ENV=dfnet311, "
        "or set DEEPFILTER_CLI to the full path of deepFilter.exe."
    )


def run_deepfilter(in_wav: Path, out_wav: Path, model_dir: Path) -> str:
    """
    Run DeepFilterNet3 on in_wav and write enhanced audio to out_wav.
    Returns a short engine description for logging/metrics.
    """
    out_dir = out_wav.parent
    cmd = build_deepfilter_cmd(in_wav, out_dir, model_dir)
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    produced = out_dir / in_wav.name
    if completed.returncode != 0 or not produced.exists():
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        hint = stderr or stdout or f"exit code {completed.returncode}"
        if "libdf" in hint.lower() or "No module named" in hint:
            hint += (
                " | Hint: use conda env with deepfilternet, e.g. "
                "DEEPFILTER_CONDA_ENV=dfnet311 (base miniconda deepFilter is often broken)."
            )
        raise DeepFilterNetError(f"DeepFilterNet command failed: {hint}")

    if out_wav.exists():
        out_wav.unlink()
    produced.rename(out_wav)
    if len(cmd) >= 4 and cmd[1] == "run":
        engine = f"deepfilter_conda:{cmd[3]}"
    elif os.getenv("DEEPFILTER_CLI"):
        engine = "deepfilter_cli:custom"
    else:
        engine = "deepfilter_cli"
    return engine
