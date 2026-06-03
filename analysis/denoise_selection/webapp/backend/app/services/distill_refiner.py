from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn


class TinyResidualRefiner(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(2, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 1, kernel_size=1),
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


PROJECT_DENOISE_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_DENOISE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_DENOISE_ROOT))
from algorithms.common import load_audio_mono, save_audio  # noqa: E402


def refine_with_student(input_wav: Path, noisy_wav: Path, output_wav: Path, checkpoint: Path, residual_scale: float = 1.0) -> bool:
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
        save_audio(output_wav, y.numpy().astype(np.float32), sr)
    return True

