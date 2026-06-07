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


def _conda_base(conda: str) -> Path | None:
    completed = subprocess.run([conda, "info", "--base"], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return None
    base = completed.stdout.strip()
    return Path(base) if base else None


def _conda_env_deepfilter(conda: str, env_name: str) -> Path | None:
    base = _conda_base(conda)
    if base is None:
        return None
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    env_root = base / "envs" / env_name / bin_dir
    for name in ("deepFilter.exe", "deepFilter", "deep-filter"):
        candidate = env_root / name
        if candidate.exists():
            return candidate.resolve()
    return None


def _cli_supports_no_suffix(cli: Path) -> bool:
    completed = subprocess.run([str(cli), "--help"], check=False, capture_output=True, text=True)
    help_text = f"{completed.stdout}\n{completed.stderr}"
    return "--no-suffix" in help_text


def _resolve_deepfilter_cli() -> tuple[str, str]:
    """
    Return (executable path or command name, flavor).
    flavor is 'python' (deepfilternet pip package) or 'rust' (standalone deepFilter.exe).
    """
    explicit = os.getenv("DEEPFILTER_CLI", "").strip()
    if explicit:
        cli = Path(explicit).resolve()
        if not cli.exists():
            raise DeepFilterNetError(f"DEEPFILTER_CLI not found: {cli}")
        flavor = "python" if _cli_supports_no_suffix(cli) else "rust"
        return str(cli), flavor

    conda_env = os.getenv("DEEPFILTER_CONDA_ENV", "dfnet311").strip()
    conda = shutil.which("conda")
    if conda and conda_env:
        env_cli = _conda_env_deepfilter(conda, conda_env)
        if env_cli is not None:
            return str(env_cli), "python"
        return f"conda:{conda_env}", "python"

    for name in ("deepFilter", "deep-filter"):
        path = shutil.which(name)
        if path:
            cli = Path(path).resolve()
            flavor = "python" if _cli_supports_no_suffix(cli) else "rust"
            return str(cli), flavor

    raise DeepFilterNetError(
        "DeepFilterNet CLI not found. Install deepfilternet in conda env dfnet311 "
        "(pip install deepfilternet) and set DEEPFILTER_CONDA_ENV=dfnet311, "
        "or set DEEPFILTER_CLI to the full path of deepFilter.exe."
    )


def build_deepfilter_cmd(in_wav: Path, out_dir: Path, model_dir: Path) -> list[str]:
    """Build CLI argv. Prefer conda env (dfnet311) when DEEPFILTER_CONDA_ENV is set."""
    in_wav = in_wav.resolve()
    out_dir = out_dir.resolve()
    model_dir = model_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cli_ref, flavor = _resolve_deepfilter_cli()

    if flavor == "python":
        tail = [str(in_wav), "-o", str(out_dir), "--no-suffix", "-m", str(model_dir)]
    else:
        raise DeepFilterNetError(
            "Detected Rust deepFilter.exe, which requires a model tar.gz and is incompatible "
            "with models/DeepFilterNet3/ checkpoints. Use the Python CLI from conda env dfnet311 "
            "(set DEEPFILTER_CONDA_ENV=dfnet311). If ./deepFilter.exe in the repo root shadows "
            "the conda binary, delete it from PATH or set DEEPFILTER_CLI explicitly."
        )

    if cli_ref.startswith("conda:"):
        env_name = cli_ref.split(":", 1)[1]
        conda = shutil.which("conda")
        if not conda:
            raise DeepFilterNetError("conda not found")
        return [conda, "run", "-n", env_name, "--no-capture-output", "deepFilter", *tail]

    return [cli_ref, *tail]


def _find_produced_wav(out_dir: Path, in_wav: Path, flavor: str) -> Path | None:
    exact = out_dir / in_wav.name
    if exact.exists():
        return exact
    if flavor == "rust":
        matches = sorted(out_dir.glob(f"{in_wav.stem}*.wav"))
        if matches:
            return matches[0]
    return None


def run_deepfilter(in_wav: Path, out_wav: Path, model_dir: Path) -> str:
    """
    Run DeepFilterNet3 on in_wav and write enhanced audio to out_wav.
    Returns a short engine description for logging/metrics.
    """
    out_dir = out_wav.parent
    _, flavor = _resolve_deepfilter_cli()
    cmd = build_deepfilter_cmd(in_wav, out_dir, model_dir)
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    produced = _find_produced_wav(out_dir, in_wav, flavor)
    if completed.returncode != 0 or produced is None:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        hint = stderr or stdout or f"exit code {completed.returncode}"
        if "unexpected argument '--no-suffix'" in hint:
            hint += (
                " | Hint: repo-root deepFilter.exe (Rust) shadowed dfnet311. "
                "Restart backend after update, or set DEEPFILTER_CLI to "
                "miniconda3/envs/dfnet311/Scripts/deepFilter.exe."
            )
        if "libdf" in hint.lower() or "No module named" in hint:
            hint += (
                " | Hint: use conda env with deepfilternet, e.g. "
                "DEEPFILTER_CONDA_ENV=dfnet311 (base miniconda deepFilter is often broken)."
            )
        raise DeepFilterNetError(f"DeepFilterNet command failed: {hint}")

    if out_wav.exists():
        out_wav.unlink()
    produced.rename(out_wav)
    if len(cmd) >= 4 and cmd[0].endswith("conda") and cmd[1] == "run":
        engine = f"deepfilter_conda:{cmd[3]}"
    elif os.getenv("DEEPFILTER_CLI"):
        engine = "deepfilter_cli:custom"
    else:
        engine = f"deepfilter_cli:{flavor}"
    return engine
