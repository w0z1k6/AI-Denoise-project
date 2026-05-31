from __future__ import annotations

import numpy as np

from .base_omlsa_mcra import enhance_spectrum_omlsa_mcra
from .common import istft_complex, stft_complex


def process(x: np.ndarray, sr: int) -> np.ndarray:
    """
    Spectral subspace projection:
    1) estimate noise subspace from initial frames,
    2) project mixture magnitude away from that subspace,
    3) apply OMLSA for residual suppression.
    """
    _, X = stft_complex(x, sr)
    mag = np.abs(X).astype(np.float32)
    phase = np.exp(1j * np.angle(X))
    f, t = mag.shape
    eps = 1e-8

    n0 = min(16, t)
    N = mag[:, :n0]
    U, s, _ = np.linalg.svd(N, full_matrices=False)
    # pick noise rank by energy ratio
    energy = np.cumsum(s**2) / (np.sum(s**2) + eps)
    rank_n = int(np.searchsorted(energy, 0.9) + 1)
    rank_n = int(np.clip(rank_n, 1, min(6, U.shape[1])))
    Un = U[:, :rank_n]

    noise_part = Un @ (Un.T @ mag)
    clean_mag = np.maximum(mag - noise_part, 0.0)
    gain = clean_mag / (mag + eps)
    gain = np.clip(gain, 0.06, 1.0)
    S0 = gain * mag * phase
    S = enhance_spectrum_omlsa_mcra(S0)
    return istft_complex(S, sr, len(x))
