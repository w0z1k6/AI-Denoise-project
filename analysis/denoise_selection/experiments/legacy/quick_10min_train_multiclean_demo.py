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
            nn.Conv2d(1, 12, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(12, 12, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(12, 1, kernel_size=1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def mix_at_snr(clean: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    noise = rng.standard_normal(clean.shape).astype(np.float32)
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


def list_clean_files(clean_dir: Path) -> list[Path]:
    files = sorted(clean_dir.glob("*.wav"))
    if not files:
        raise FileNotFoundError(f"No clean wav files found in {clean_dir}")
    return files


def load_clean_pool(paths: list[Path]) -> tuple[list[np.ndarray], int]:
    pool = []
    sr_ref = None
    for p in paths:
        x, sr = sf.read(p)
        if x.ndim > 1:
            x = x.mean(axis=1)
        x = x.astype(np.float32)
        if sr_ref is None:
            sr_ref = sr
        elif sr != sr_ref:
            raise ValueError(f"Sample rate mismatch in {p}: {sr} != {sr_ref}")
        pool.append(x)
    if sr_ref is None:
        raise RuntimeError("No valid clean clips.")
    return pool, sr_ref


def pick_chunk(clean_pool: list[np.ndarray], chunk_len: int, rng: np.random.Generator) -> np.ndarray:
    x = clean_pool[int(rng.integers(0, len(clean_pool)))]
    if len(x) >= chunk_len:
        s = int(rng.integers(0, len(x) - chunk_len + 1))
        return x[s : s + chunk_len].copy()
    out = np.zeros(chunk_len, dtype=np.float32)
    out[: len(x)] = x
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out_dir = Path(__file__).resolve().parent
    clean_dir = out_dir / "demo_dataset" / "clean"

    noisy_path = root / "noisy_testset" / "scene02_white_snr5.wav"
    clean_ref_path = root / "noisy_testset" / "clean_reference.wav"
    out_wav = out_dir / "scene02_demo_multiclean_trained_out.wav"
    out_json = out_dir / "scene02_demo_multiclean_training_log.json"

    clean_files = list_clean_files(clean_dir)
    clean_pool, sr = load_clean_pool(clean_files)

    noisy_np, sr_noisy = sf.read(noisy_path)
    if noisy_np.ndim > 1:
        noisy_np = noisy_np.mean(axis=1)
    noisy_np = noisy_np.astype(np.float32)
    if sr_noisy != sr:
        raise ValueError("Noisy sample rate mismatch with clean pool.")

    clean_ref, sr_ref = sf.read(clean_ref_path)
    if clean_ref.ndim > 1:
        clean_ref = clean_ref.mean(axis=1)
    clean_ref = clean_ref.astype(np.float32)
    if sr_ref != sr:
        raise ValueError("Clean reference sample rate mismatch.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(7)
    np.random.seed(7)
    rng = np.random.default_rng(7)

    n_fft = 512
    hop = 128
    chunk_len = sr  # 1 second
    max_steps = 900
    max_seconds = 600

    win = torch.hann_window(n_fft, device=device)
    model = TinyMaskNet().to(device)
    optim = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    start = time.time()
    losses = []

    for step in range(max_steps):
        if time.time() - start > max_seconds:
            break
        clean_chunk = pick_chunk(clean_pool, chunk_len, rng)
        snr_db = float(rng.uniform(-2.0, 18.0))
        mix = mix_at_snr(clean_chunk, snr_db, rng)
        clean = torch.from_numpy(clean_chunk).to(device)
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
        if (step + 1) % 150 == 0:
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

    m = min(len(clean_ref), len(noisy_np), len(y_np))
    noisy_err = rms(noisy_np[:m] - clean_ref[:m])
    denoise_err = rms(y_np[:m] - clean_ref[:m])

    payload = {
        "device": str(device),
        "clean_files": len(clean_files),
        "steps_run": len(losses),
        "elapsed_sec": time.time() - start,
        "final_loss": losses[-1] if losses else None,
        "noisy_err_rms": noisy_err,
        "denoised_err_rms": denoise_err,
        "output_wav": str(out_wav),
    }
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_wav}")
    print(f"Saved: {out_json}")
    print(payload)


if __name__ == "__main__":
    main()
