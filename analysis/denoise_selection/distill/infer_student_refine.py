from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
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


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), int(sr)


def stft_torch(x: torch.Tensor, n_fft: int, hop: int, win: torch.Tensor) -> torch.Tensor:
    return torch.stft(
        x,
        n_fft=n_fft,
        hop_length=hop,
        win_length=n_fft,
        window=win,
        center=True,
        return_complex=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run student distill refiner inference on routed outputs.")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--pairs", type=str, default="analysis/denoise_selection/distill/distill_pairs.json")
    parser.add_argument("--out-dir", type=str, default="analysis/denoise_selection/outputs/distill_refined")
    parser.add_argument("--residual-scale", type=float, default=1.0, help="Multiplier on checkpoint residual alpha.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    ckpt = torch.load(root / args.checkpoint, map_location="cpu")
    n_fft = int(ckpt["n_fft"])
    hop = int(ckpt["hop"])
    residual_alpha = float(ckpt.get("residual_alpha", 0.8)) * float(args.residual_scale)
    model = TinyResidualRefiner()
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    with (root / args.pairs).open("r", encoding="utf-8") as f:
        pairs = json.load(f)

    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    win = torch.hann_window(n_fft)

    logs = []
    with torch.no_grad():
        for p in pairs:
            in_path = Path(p["math_input_wav"])
            noisy_path = Path(p["noisy_wav"])
            x_np, sr = load_mono(in_path)
            n_np, sr_n = load_mono(noisy_path)
            if sr_n != sr:
                raise ValueError(f"Sample rate mismatch: {in_path} vs {noisy_path}")
            m = min(len(x_np), len(n_np))
            x_np = x_np[:m]
            n_np = n_np[:m]
            x = torch.from_numpy(x_np)
            n = torch.from_numpy(n_np)
            X = stft_torch(x, n_fft, hop, win)
            N = stft_torch(n, n_fft, hop, win)
            mag = torch.abs(X)
            mag_n = torch.abs(N)
            inp = torch.stack([torch.log1p(mag), torch.log1p(mag_n)], dim=0).unsqueeze(0)
            residual = model(inp).squeeze(0).squeeze(0)
            pred_mask = torch.clamp(1.0 + residual_alpha * residual, 0.2, 1.8)
            Y = pred_mask * X
            y = torch.istft(
                Y,
                n_fft=n_fft,
                hop_length=hop,
                win_length=n_fft,
                window=win,
                center=True,
                length=len(x_np),
            )
            y_np = y.numpy().astype(np.float32)
            peak = float(np.max(np.abs(y_np)) + 1e-12)
            if peak > 0.99:
                y_np = y_np * (0.99 / peak)

            out_name = in_path.name.replace("_routed.wav", "_distill_refined.wav")
            out_path = out_dir / out_name
            sf.write(out_path, y_np, sr)
            logs.append({"scene": p["scene"], "input": str(in_path), "output": str(out_path)})
            print(f"[REFINE] {p['scene']} -> {out_name}")

    log_path = root / "analysis" / "denoise_selection" / "distill" / "infer_log.json"
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"Saved: {log_path}")


if __name__ == "__main__":
    main()
