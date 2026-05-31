from __future__ import annotations

import numpy as np

from .base_omlsa_mcra import enhance_spectrum_omlsa_mcra
from .common import istft_complex, stft_complex


def single_channel_wpe(X: np.ndarray, taps: int = 8, delay: int = 3, iters: int = 2) -> np.ndarray:
    """
    Lightweight single-channel WPE in STFT domain.
    X: [freq, time] complex spectrum.
    """
    n_freq, n_time = X.shape
    Y = X.copy()
    eps = 1e-8
    order = taps

    for _ in range(iters):
        for f in range(n_freq):
            y = Y[f, :]
            if n_time <= delay + order + 2:
                continue
            t0 = delay + order
            rows = n_time - t0
            Z = np.zeros((order, rows), dtype=np.complex64)
            target = y[t0:]
            for k in range(order):
                Z[k, :] = y[t0 - delay - k - 1 : n_time - delay - k - 1]

            var = np.maximum(np.abs(target) ** 2, eps)
            inv_var = 1.0 / var
            Zw = Z * inv_var[None, :]
            R = Zw @ Z.conj().T
            p = Zw @ target.conj()
            try:
                g = np.linalg.solve(R + eps * np.eye(order), p)
            except np.linalg.LinAlgError:
                g = np.linalg.pinv(R + eps * np.eye(order)) @ p
            late = g.conj().T @ Z
            y_new = y.copy()
            y_new[t0:] = target - late
            Y[f, :] = y_new
    return Y


def process(x: np.ndarray, sr: int) -> np.ndarray:
    _, X = stft_complex(x, sr)
    X_dry = single_channel_wpe(X, taps=8, delay=3, iters=2)
    S = enhance_spectrum_omlsa_mcra(X_dry)
    return istft_complex(S, sr, len(x))
