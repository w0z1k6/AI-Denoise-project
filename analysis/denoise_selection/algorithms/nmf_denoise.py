from __future__ import annotations

import numpy as np

from .base_omlsa_mcra import enhance_spectrum_omlsa_mcra
from .common import istft_complex, stft_complex


def nmf_mu(V: np.ndarray, rank: int, iters: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    f, t = V.shape
    W = rng.random((f, rank), dtype=np.float32) + 1e-4
    H = rng.random((rank, t), dtype=np.float32) + 1e-4
    eps = 1e-8
    for _ in range(iters):
        WH = W @ H + eps
        H *= (W.T @ (V / WH)) / (W.T @ np.ones_like(V) + eps)
        WH = W @ H + eps
        W *= ((V / WH) @ H.T) / (np.ones_like(V) @ H.T + eps)
        W /= np.maximum(np.sum(W, axis=0, keepdims=True), eps)
    return W, H


def process(x: np.ndarray, sr: int) -> np.ndarray:
    _, X = stft_complex(x, sr)
    mag = np.abs(X).astype(np.float32)
    phase = np.exp(1j * np.angle(X))
    f, t = mag.shape
    eps = 1e-8

    # Estimate noise template from early frames.
    n0 = min(12, t)
    V_noise = mag[:, :n0]
    V_speech = mag[:, n0:] if t > n0 else mag

    rank_n = 4
    rank_s = 8
    Wn, _ = nmf_mu(V_noise + eps, rank=rank_n, iters=30, seed=11)
    Ws, _ = nmf_mu(V_speech + eps, rank=rank_s, iters=40, seed=23)
    W = np.concatenate([Ws, Wn], axis=1)
    r = W.shape[1]
    H = np.random.default_rng(42).random((r, t), dtype=np.float32) + 1e-4

    for _ in range(60):
        WH = W @ H + eps
        H *= (W.T @ (mag / WH)) / (W.T @ np.ones_like(mag) + eps)

    Hs = H[:rank_s, :]
    Hn = H[rank_s:, :]
    Vs = Ws @ Hs
    Vn = Wn @ Hn
    gain = Vs / (Vs + Vn + eps)
    gain = np.clip(gain, 0.05, 1.0)

    S0 = gain * mag * phase
    # Use OMLSA as a lightweight post-step for residual suppression.
    S = enhance_spectrum_omlsa_mcra(S0)
    return istft_complex(S, sr, len(x))
