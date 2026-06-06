from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torch.nn as nn


class TinyResidualRefiner(nn.Module):
    def __init__(self):
        super().__init__()
    
        self.conv1 = nn.Conv2d(2, 32, kernel_size=3, padding=1)
        
        self.res1 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=3, padding=2, dilation=2),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
        )
        self.res2 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=3, padding=4, dilation=4),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
        )
        self.res3 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=3, padding=8, dilation=8),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
        )
        self.out = nn.Conv2d(32, 1, kernel_size=1)
        self.act = nn.Tanh()

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = x + self.res1(x)
        x = x + self.res2(x)
        x = x + self.res3(x)
        return self.act(self.out(x))

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


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), int(sr)


def pick_aligned_chunks(
    routed: np.ndarray, teacher: np.ndarray, noisy: np.ndarray, clean: np.ndarray, chunk_len: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = min(len(routed), len(teacher), len(noisy), len(clean))
    routed = routed[:n]
    teacher = teacher[:n]
    noisy = noisy[:n]
    clean = clean[:n]
    if n >= chunk_len:
        s = int(rng.integers(0, n - chunk_len + 1))
        e = s + chunk_len
        return routed[s:e].copy(), teacher[s:e].copy(), noisy[s:e].copy(), clean[s:e].copy()
    ro = np.zeros(chunk_len, dtype=np.float32)
    to = np.zeros(chunk_len, dtype=np.float32)
    no = np.zeros(chunk_len, dtype=np.float32)
    co = np.zeros(chunk_len, dtype=np.float32)
    ro[:n] = routed
    to[:n] = teacher
    no[:n] = noisy
    co[:n] = clean
    return ro, to, no, co


def compressed_mag_loss(y_hat: torch.Tensor, y_ref: torch.Tensor, c: float) -> torch.Tensor:
    mag_hat = torch.clamp(torch.abs(y_hat), min=1e-8).pow(c)
    mag_ref = torch.clamp(torch.abs(y_ref), min=1e-8).pow(c)
    return torch.mean((mag_hat - mag_ref) ** 2)


def multi_resolution_stft_loss(
    y_hat_wav: torch.Tensor,
    y_ref_wav: torch.Tensor,
    device: torch.device,
) -> torch.Tensor:
    loss = torch.tensor(0.0, device=device)
    for n_fft in [512, 1024, 2048]:
        hop = n_fft // 4
        win = torch.hann_window(n_fft, device=device)
        S_hat = torch.stft(y_hat_wav, n_fft, hop, window=win, return_complex=True)
        S_ref = torch.stft(y_ref_wav, n_fft, hop, window=win, return_complex=True)
        mag_hat = torch.abs(S_hat)
        mag_ref = torch.abs(S_ref)
        loss += torch.mean((mag_hat - mag_ref) ** 2)
        loss += torch.mean((torch.log1p(mag_hat) - torch.log1p(mag_ref)) ** 2)
    return loss / 3.0


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train tiny student refiner by distillation.")
    parser.add_argument("--config", type=str, default="analysis/denoise_selection/distill/distill_config.json")
    parser.add_argument("--pairs", type=str, default="analysis/denoise_selection/distill/distill_pairs.json")
    parser.add_argument("--split", type=str, default="analysis/denoise_selection/distill/distill_split.json")
    parser.add_argument("--tag", type=str, default="runA")
    parser.add_argument("--lr-scale", type=float, default=1.0)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    cfg = read_json(root / args.config)
    pairs = read_json(root / args.pairs)
    split = read_json(root / args.split)
    train_set = {x for x in split.get("train_scenes", [])}
    val_set = {x for x in split.get("val_scenes", [])}

    train_pairs = [p for p in pairs if p["scene"] in train_set]
    val_pairs = [p for p in pairs if p["scene"] in val_set]
    if not train_pairs:
        raise RuntimeError("No train pairs available.")
    if not val_pairs:
        val_pairs = train_pairs[-2:]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(int(cfg.get("seed", 42)))
    np.random.seed(int(cfg.get("seed", 42)))
    rng = np.random.default_rng(int(cfg.get("seed", 42)))

    n_fft = int(cfg.get("n_fft", 512))
    hop = int(cfg.get("hop", 128))
    chunk_len = int(float(cfg.get("chunk_seconds", 1.0)) * int(cfg.get("sample_rate", 16000)))
    max_steps = int(cfg.get("max_steps", 1200))
    max_seconds = float(cfg.get("max_train_seconds", 900))
    cexp = float(cfg.get("compress_exponent", 0.5))
    w_l1 = float(cfg.get("loss_weights", {}).get("distill_l1", 1.0))
    w_mag = float(cfg.get("loss_weights", {}).get("mag_compress", 0.3))
    w_clean = float(cfg.get("loss_weights", {}).get("clean_aux_mag", 0.15))
    w_mrstft = float(cfg.get("loss_weights", {}).get("mrstft", 0.3))
    residual_alpha = float(cfg.get("train_residual_alpha", 0.8))
    lr = float(cfg.get("learning_rate", 5e-4)) * float(args.lr_scale)
    hard_scene_weights = cfg.get("hard_scene_weights", {"scene02_white_snr5": 3.0, "scene09_chirp_interference_snr8": 3.5})

    model = TinyResidualRefiner().to(device)
    optim = torch.optim.Adam(model.parameters(), lr=lr)
    l1 = nn.L1Loss()
    win = torch.hann_window(n_fft, device=device)

    start = time.time()
    losses = []

    def load_pair_audio(pair: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
        routed, sr1 = load_mono(Path(pair["math_input_wav"]))
        teacher, sr2 = load_mono(Path(pair["teacher_wav"]))
        noisy, sr3 = load_mono(Path(pair["noisy_wav"]))
        clean, sr4 = load_mono(Path(pair["clean_wav"]))
        if len({sr1, sr2, sr3, sr4}) != 1:
            raise ValueError("Sample rate mismatch in pair.")
        m = min(len(routed), len(teacher), len(noisy), len(clean))
        return routed[:m], teacher[:m], noisy[:m], clean[:m], sr1

    scene_weights = np.array([float(hard_scene_weights.get(p["scene"], 1.0)) for p in train_pairs], dtype=np.float64)
    probs = scene_weights / np.sum(scene_weights)

    for step in range(max_steps):
        if time.time() - start > max_seconds:
            break
        pair_idx = int(rng.choice(len(train_pairs), p=probs))
        pair = train_pairs[pair_idx]
        routed_np, teacher_np, noisy_np, clean_np, _ = load_pair_audio(pair)
        rin, tin, nin, cin = pick_aligned_chunks(routed_np, teacher_np, noisy_np, clean_np, chunk_len, rng)

        routed = torch.from_numpy(rin).to(device)
        teacher = torch.from_numpy(tin).to(device)
        noisy = torch.from_numpy(nin).to(device)
        clean = torch.from_numpy(cin).to(device)
        X = stft_torch(routed, n_fft, hop, win)
        T = stft_torch(teacher, n_fft, hop, win)
        N = stft_torch(noisy, n_fft, hop, win)
        C = stft_torch(clean, n_fft, hop, win)

        mag_x = torch.abs(X)
        mag_t = torch.abs(T)
        mag_n = torch.abs(N)
        teacher_mask = torch.clamp(mag_t / (mag_x + 1e-8), 0.2, 1.8)
        teacher_mask = torch.nan_to_num(teacher_mask, nan=1.0, posinf=1.8, neginf=0.2)

        inp = torch.stack([torch.log1p(mag_x), torch.log1p(mag_n)], dim=0).unsqueeze(0)
        residual = model(inp).squeeze(0).squeeze(0)
        pred_mask = torch.clamp(1.0 + residual_alpha * residual, 0.2, 1.8)
        pred_mask = torch.nan_to_num(pred_mask, nan=1.0, posinf=1.8, neginf=0.2)

        Y_hat = pred_mask * X
        y_hat_wav = torch.istft(
            Y_hat, n_fft, hop, window=win, center=True, length=len(rin)
            )
        w_mrstft = float(cfg.get("loss_weights", {}).get("mrstft", 0.3))

        loss = (
                w_l1 * l1(pred_mask, teacher_mask)
                + w_mag * compressed_mag_loss(Y_hat, T, cexp)
                + w_clean * compressed_mag_loss(Y_hat, C, cexp)
                + w_mrstft * multi_resolution_stft_loss(y_hat_wav, teacher, device)
            )
        if not torch.isfinite(loss):
            continue
        optim.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optim.step()
        losses.append(float(loss.item()))
        if (step + 1) % 200 == 0:
            print(f"step={step+1}, loss={losses[-1]:.6f}")

    # quick val
    model.eval()
    with torch.no_grad():
        val_losses = []
        for pair in val_pairs:
            routed_np, teacher_np, noisy_np, clean_np, _ = load_pair_audio(pair)
            rin, tin, nin, cin = pick_aligned_chunks(routed_np, teacher_np, noisy_np, clean_np, chunk_len, rng)
            routed = torch.from_numpy(rin).to(device)
            teacher = torch.from_numpy(tin).to(device)
            noisy = torch.from_numpy(nin).to(device)
            clean = torch.from_numpy(cin).to(device)
            X = stft_torch(routed, n_fft, hop, win)
            T = stft_torch(teacher, n_fft, hop, win)
            N = stft_torch(noisy, n_fft, hop, win)
            C = stft_torch(clean, n_fft, hop, win)
            mag_x = torch.abs(X)
            mag_t = torch.abs(T)
            mag_n = torch.abs(N)
            teacher_mask = torch.clamp(mag_t / (mag_x + 1e-8), 0.2, 1.8)
            teacher_mask = torch.nan_to_num(teacher_mask, nan=1.0, posinf=1.8, neginf=0.2)
            inp = torch.stack([torch.log1p(mag_x), torch.log1p(mag_n)], dim=0).unsqueeze(0)
            residual = model(inp).squeeze(0).squeeze(0)
            pred_mask = torch.clamp(1.0 + residual_alpha * residual, 0.2, 1.8)
            pred_mask = torch.nan_to_num(pred_mask, nan=1.0, posinf=1.8, neginf=0.2)
            Y_hat = pred_mask * X
            val_loss = (
                w_l1 * torch.mean(torch.abs(pred_mask - teacher_mask))
                + w_mag * compressed_mag_loss(Y_hat, T, cexp)
                + w_clean * compressed_mag_loss(Y_hat, C, cexp)
            )
            val_losses.append(float(val_loss.item()))
        val_l1 = float(np.mean(val_losses)) if val_losses else None

    out_dir = root / "analysis" / "denoise_selection" / "distill" / "checkpoints"
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt = out_dir / f"student_{args.tag}.pt"
    torch.save(
        {
            "model_state": model.state_dict(),
            "n_fft": n_fft,
            "hop": hop,
            "tag": args.tag,
            "val_l1": val_l1,
            "residual_alpha": residual_alpha,
        },
        ckpt,
    )
    runlog = root / "analysis" / "denoise_selection" / "distill" / f"train_log_{args.tag}.json"
    payload = {
        "checkpoint": str(ckpt),
        "device": str(device),
        "steps_run": len(losses),
        "elapsed_sec": time.time() - start,
        "final_train_loss": losses[-1] if losses else None,
        "val_l1_mask": val_l1,
        "lr": lr,
    }
    with runlog.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved checkpoint: {ckpt}")
    print(f"Saved run log: {runlog}")
    print(payload)


if __name__ == "__main__":
    main()
