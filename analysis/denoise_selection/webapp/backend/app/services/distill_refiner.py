from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

PROJECT_DENOISE_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOT = PROJECT_DENOISE_ROOT.parent.parent
DISTILL_ROOT = PROJECT_DENOISE_ROOT / "distill"
DEFAULT_DISTILL_CONFIG = DISTILL_ROOT / "distill_config.json"

if str(PROJECT_DENOISE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_DENOISE_ROOT))
if str(DISTILL_ROOT) not in sys.path:
    sys.path.insert(0, str(DISTILL_ROOT))

from algorithms.common import load_audio_mono, save_audio  # noqa: E402
from train_student_distill import TinyResidualRefiner  # noqa: E402


def resolve_distill_checkpoint(project_root: Path | None = None) -> tuple[Path, float]:
    """Resolve checkpoint path and residual scale from env or distill_config.json."""
    root = project_root or PROJECT_ROOT
    env_ckpt = os.getenv("DISTILL_CHECKPOINT", "").strip()
    env_scale = os.getenv("DISTILL_RESIDUAL_SCALE", "").strip()

    if env_ckpt:
        checkpoint = Path(env_ckpt)
        if not checkpoint.is_absolute():
            checkpoint = root / checkpoint
        scale = float(env_scale) if env_scale else 1.0
        return checkpoint.resolve(), scale

    config_path = DEFAULT_DISTILL_CONFIG
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        rel_ckpt = cfg.get("selected_checkpoint", "")
        scale = float(cfg.get("inference_residual_scale", 1.0))
        if env_scale:
            scale = float(env_scale)
        checkpoint = Path(rel_ckpt)
        if not checkpoint.is_absolute():
            checkpoint = root / checkpoint
        return checkpoint.resolve(), scale

    fallback = root / "analysis/denoise_selection/distill/checkpoints/student_runK.pt"
    scale = float(env_scale) if env_scale else 1.0
    return fallback.resolve(), scale


def refine_with_student(
    input_wav: Path,
    noisy_wav: Path,
    output_wav: Path,
    checkpoint: Path,
    residual_scale: float = 1.0,
) -> bool:
    if not checkpoint.exists():
        return False
    ckpt = torch.load(checkpoint, map_location="cpu")
    n_fft = int(ckpt.get("n_fft", 512))
    hop = int(ckpt.get("hop", 128))
    alpha = float(ckpt.get("residual_alpha", 0.8)) * float(residual_scale)

    model = TinyResidualRefiner()
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    den, sr = load_audio_mono(input_wav)
    noisy, sr2 = load_audio_mono(noisy_wav)
    if sr != sr2:
        return False
    m = min(len(den), len(noisy))
    den = den[:m]
    noisy = noisy[:m]

    win = torch.hann_window(n_fft)
    with torch.no_grad():
        d = torch.from_numpy(den)
        n = torch.from_numpy(noisy)
        D = torch.stft(d, n_fft=n_fft, hop_length=hop, win_length=n_fft, window=win, center=True, return_complex=True)
        N = torch.stft(n, n_fft=n_fft, hop_length=hop, win_length=n_fft, window=win, center=True, return_complex=True)
        inp = torch.stack([torch.log1p(torch.abs(D)), torch.log1p(torch.abs(N))], dim=0).unsqueeze(0)
        residual = model(inp).squeeze(0).squeeze(0)
        mask = torch.clamp(1.0 + alpha * residual, 0.2, 1.8)
        Y = mask * D
        y = torch.istft(Y, n_fft=n_fft, hop_length=hop, win_length=n_fft, window=win, center=True, length=len(den))
        y_np = y.numpy().astype(np.float32)
        peak = float(np.max(np.abs(y_np)) + 1e-12)
        if peak > 0.99:
            y_np = y_np * (0.99 / peak)
        save_audio(output_wav, y_np, sr)
    return True
