from __future__ import annotations

import numpy as np
from scipy.signal import filtfilt, iirnotch, welch

from .base_omlsa_mcra import process as omlsa_process


def detect_tonal_peaks(x: np.ndarray, sr: int, max_peaks: int = 6) -> list[float]:
    f, p = welch(x, fs=sr, nperseg=2048)
    p_db = 10.0 * np.log10(p + 1e-12)
    peaks: list[tuple[float, float]] = []
    for i in range(2, len(f) - 2):
        local = p_db[i - 2 : i + 3]
        if p_db[i] == np.max(local):
            prominence = p_db[i] - float(np.median(local))
            if prominence > 6.0 and 40.0 <= f[i] <= min(0.48 * sr, 7800.0):
                peaks.append((float(f[i]), float(prominence)))
    peaks.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in peaks[:max_peaks]]


def apply_notch_bank(x: np.ndarray, sr: int, peaks: list[float]) -> np.ndarray:
    y = x.astype(np.float32).copy()
    for f0 in peaks:
        w0 = f0 / (sr / 2.0)
        if not 0.0 < w0 < 1.0:
            continue
        q = 35.0 if f0 < 500 else 50.0
        b, a = iirnotch(w0=w0, Q=q)
        y = filtfilt(b, a, y).astype(np.float32)
    return y


def process(x: np.ndarray, sr: int) -> np.ndarray:
    peaks = detect_tonal_peaks(x, sr, max_peaks=8)
    # Always include hum priors and first harmonics
    for base in (50.0, 60.0):
        for h in (1, 2, 3, 4):
            f0 = base * h
            if f0 < sr / 2:
                peaks.append(f0)
    # deduplicate nearby peaks
    peaks = sorted(peaks)
    merged: list[float] = []
    for p in peaks:
        if not merged or abs(p - merged[-1]) > 8.0:
            merged.append(p)
    y = apply_notch_bank(x, sr, merged)
    return omlsa_process(y, sr)
