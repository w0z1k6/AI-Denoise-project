from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from scipy.signal import istft, stft


STFT_NFFT = 512
STFT_HOP = 128
STFT_WIN = "hann"


def load_audio_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), int(sr)


def save_audio(path: Path, x: np.ndarray, sr: int) -> None:
    y = x.astype(np.float32)
    peak = float(np.max(np.abs(y)) + 1e-12)
    if peak > 0.99:
        y = y * (0.99 / peak)
    sf.write(path, y, sr)


def stft_complex(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    freqs, _, X = stft(
        x,
        fs=sr,
        window=STFT_WIN,
        nperseg=STFT_NFFT,
        noverlap=STFT_NFFT - STFT_HOP,
        nfft=STFT_NFFT,
        boundary="zeros",
        padded=True,
    )
    return freqs, X


def istft_complex(X: np.ndarray, sr: int, target_len: int) -> np.ndarray:
    _, y = istft(
        X,
        fs=sr,
        window=STFT_WIN,
        nperseg=STFT_NFFT,
        noverlap=STFT_NFFT - STFT_HOP,
        nfft=STFT_NFFT,
        input_onesided=True,
        boundary=True,
    )
    return y[:target_len].astype(np.float32)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def band_snr(clean: np.ndarray, test: np.ndarray, sr: int, f0: float, f1: float) -> float:
    freqs, C = stft_complex(clean, sr)
    _, T = stft_complex(test, sr)
    m = min(C.shape[1], T.shape[1])
    C = C[:, :m]
    T = T[:, :m]
    N = T - C
    p_sig = np.mean(np.abs(C[(freqs >= f0) & (freqs < f1), :]) ** 2) + 1e-12
    p_n = np.mean(np.abs(N[(freqs >= f0) & (freqs < f1), :]) ** 2) + 1e-12
    return float(10.0 * np.log10(p_sig / p_n))


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def apply_chain(x: np.ndarray, sr: int, funcs: list) -> np.ndarray:
    y = x
    for f in funcs:
        y = f(y, sr)
    return y


def serialize_float_map(d: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, np.generic):
            out[k] = float(v)
        else:
            out[k] = v
    return out
