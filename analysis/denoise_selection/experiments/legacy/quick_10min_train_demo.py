import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torch.nn as nn


class TinyMaskNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(8, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(8, 1, kernel_size=1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def mix_at_snr(clean: np.ndarray, snr_db: float) -> np.ndarray:
    noise = np.random.randn(*clean.shape).astype(np.float32)
    clean_rms = rms(clean)
    noise_rms = rms(noise)
    target_noise_rms = clean_rms / (10 ** (snr_db / 20))
    noise *= target_noise_rms / (noise_rms + 1e-12)
    return clean + noise


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
    root = Path(__file__).resolve().parents[2]
    out_dir = Path(__file__).resolve().parent

    clean_path = root / "noisy_testset" / "clean_reference.wav"
    noisy_path = root / "noisy_testset" / "scene02_white_snr5.wav"
    out_wav = out_dir / "scene02_demo_trained_out.wav"
    out_json = out_dir / "scene02_demo_training_log.json"

    clean_np, sr = sf.read(clean_path)
    noisy_np, sr_noisy = sf.read(noisy_path)
    if sr != sr_noisy:
        raise ValueError("Sample rates differ.")
    if clean_np.ndim > 1:
        clean_np = clean_np.mean(axis=1)
    if noisy_np.ndim > 1:
        noisy_np = noisy_np.mean(axis=1)
    clean_np = clean_np.astype(np.float32)
    noisy_np = noisy_np.astype(np.float32)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(42)
    np.random.seed(42)

    n_fft = 512
    hop = 128
    chunk_len = sr  # 1 sec
    max_steps = 500
    max_seconds = 600  # 10 minutes upper bound

    win = torch.hann_window(n_fft, device=device)
    model = TinyMaskNet().to(device)
    optim = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    start = time.time()
    losses = []
    clean_torch = torch.from_numpy(clean_np).to(device)

    for step in range(max_steps):
        if time.time() - start > max_seconds:
            break
        s0 = np.random.randint(0, max(1, len(clean_np) - chunk_len))
        chunk = clean_np[s0 : s0 + chunk_len]
        if len(chunk) < chunk_len:
            pad = np.zeros(chunk_len, dtype=np.float32)
            pad[: len(chunk)] = chunk
            chunk = pad

        snr_db = float(np.random.uniform(0, 15))
        mix = mix_at_snr(chunk, snr_db)

        clean = torch.from_numpy(chunk).to(device)
        mix_t = torch.from_numpy(mix).to(device)

        S = stft_torch(clean, n_fft, hop, win)
        X = stft_torch(mix_t, n_fft, hop, win)
        mag_s = torch.abs(S)
        mag_x = torch.abs(X)
        target_mask = torch.clamp(mag_s / (mag_x + 1e-8), 0.0, 1.0)

        inp = torch.log1p(mag_x).unsqueeze(0).unsqueeze(0)
        tgt = target_mask.unsqueeze(0).unsqueeze(0)

        pred = model(inp)
        loss = criterion(pred, tgt)

        optim.zero_grad()
        loss.backward()
        optim.step()

        losses.append(float(loss.item()))
        if (step + 1) % 100 == 0:
            print(f"step={step+1}, loss={losses[-1]:.6f}")

    model.eval()
    with torch.no_grad():
        noisy_t = torch.from_numpy(noisy_np).to(device)
        Xn = stft_torch(noisy_t, n_fft, hop, win)
        mag_xn = torch.abs(Xn)
        inp = torch.log1p(mag_xn).unsqueeze(0).unsqueeze(0)
        mask = model(inp).squeeze(0).squeeze(0)
        Y = Xn * mask
        y = torch.istft(
            Y,
            n_fft=n_fft,
            hop_length=hop,
            win_length=n_fft,
            window=win,
            center=True,
            length=len(noisy_np),
        )
        y_np = y.detach().cpu().numpy().astype(np.float32)

    sf.write(out_wav, y_np, sr)
    payload = {
        "device": str(device),
        "steps_run": len(losses),
        "elapsed_sec": time.time() - start,
        "final_loss": losses[-1] if losses else None,
        "output_wav": str(out_wav),
    }
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_wav}")
    print(f"Saved: {out_json}")
    print(payload)


if __name__ == "__main__":
    main()
