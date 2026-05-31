from __future__ import annotations

import numpy as np
from scipy.signal import medfilt

from .base_omlsa_mcra import enhance_spectrum_omlsa_mcra
from .common import STFT_HOP, istft_complex, stft_complex


def detect_chirp_track(X: np.ndarray, freqs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eps = 1e-12
    mag = np.abs(X)
    mag_db = 20.0 * np.log10(mag + eps)
    n_freq, n_time = mag.shape
    # Include mid band to catch chirp opening sweep.
    high_bins = np.where(freqs >= 700.0)[0]
    track = np.full(n_time, -1, dtype=np.int32)
    prom = np.zeros(n_time, dtype=np.float32)
    if len(high_bins) == 0:
        return track, prom

    prev_k = -1
    for t in range(n_time):
        hb = mag_db[high_bins, t]
        k_local = int(np.argmax(hb))
        k = int(high_bins[k_local])
        p = float(mag_db[k, t] - np.median(hb))
        hb_lin = mag[high_bins, t] + eps
        flat = float(np.exp(np.mean(np.log(hb_lin))) / np.mean(hb_lin))
        # Be more conservative in low-mid frequencies to protect speech harmonics.
        if freqs[k] < 1500.0:
            ok = p > 10.0 and flat < 0.18
        else:
            ok = p > 8.0 and flat < 0.25
        if prev_k >= 0 and ok and abs(k - prev_k) > 10:
            ok = p > 15.0
        if ok:
            track[t] = k
            prom[t] = p
            prev_k = k

    valid = np.where(track >= 0)[0]
    if len(valid) >= 5:
        tr = track.astype(np.float32)
        tr[track < 0] = np.nan
        idx = np.arange(n_time, dtype=np.float32)
        tr_interp = np.interp(idx, valid.astype(np.float32), tr[valid])
        tr_smooth = medfilt(tr_interp, kernel_size=9)
        track = np.clip(np.round(tr_smooth), 0, n_freq - 1).astype(np.int32)
    return track, prom


def apply_chirp_notch(
    S: np.ndarray, track: np.ndarray, prom: np.ndarray, freqs: np.ndarray, frame_time_s: np.ndarray
) -> np.ndarray:
    n_freq, n_time = S.shape
    k = np.arange(n_freq, dtype=np.float32)[:, None]
    mask = np.ones((n_freq, n_time), dtype=np.float32)
    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 700.0:
            continue
        p = float(prom[t])
        depth = np.clip((p - 8.0) / 12.0, 0.0, 1.0)
        early_boost = 1.25 if frame_time_s[t] < 2.5 else 1.0
        depth = np.clip(depth * early_boost, 0.0, 1.0)
        sigma = 1.8 if freqs[kc] < 1500.0 else 1.6
        if freqs[kc] < 1500.0:
            depth *= 0.78
        notch = 1.0 - 0.9 * depth * np.exp(-0.5 * ((k[:, 0] - kc) / sigma) ** 2)
        mask[:, t] = np.clip(notch, 0.06, 1.0).astype(np.float32)

    if n_time > 2:
        mask[:, 1:-1] = 0.2 * mask[:, :-2] + 0.6 * mask[:, 1:-1] + 0.2 * mask[:, 2:]
    return S * mask


def cancel_chirp_component(
    X: np.ndarray, track: np.ndarray, prom: np.ndarray, freqs: np.ndarray, frame_time_s: np.ndarray
) -> np.ndarray:
    """
    Stage-1 chirp cancellation directly on complex spectrum.
    This is intentionally aggressive for narrowband chirp scenes.
    """
    Y = X.copy()
    n_freq, n_time = X.shape
    k = np.arange(n_freq, dtype=np.float32)
    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 700.0:
            continue
        p = float(prom[t])
        strength = np.clip((p - 8.0) / 10.0, 0.0, 1.0)
        beta = 0.55 + 0.40 * strength
        sigma = 1.4 + 0.8 * (1.0 - strength)
        if frame_time_s[t] < 2.5:
            beta *= 1.22
            sigma *= 0.9
        if freqs[kc] < 1500.0:
            # Keep low-band suppression conservative to protect formants.
            beta *= 0.6
            sigma *= 1.25
        w = np.exp(-0.5 * ((k - kc) / sigma) ** 2).astype(np.float32)
        w /= float(np.max(w) + 1e-12)
        protect = np.ones(n_freq, dtype=np.float32)
        protect[freqs < 500.0] = 0.25
        protect[(freqs >= 500.0) & (freqs < 1200.0)] = 0.45
        protect[(freqs >= 1200.0) & (freqs < 1800.0)] = 0.65
        Y[:, t] = Y[:, t] - beta * protect * w * Y[:, t]
    return Y


def inpaint_ridge_mag(
    S: np.ndarray, track: np.ndarray, prom: np.ndarray, freqs: np.ndarray, frame_time_s: np.ndarray
) -> np.ndarray:
    """
    Stage-2 spectral inpainting around detected chirp ridge to remove
    residual thin tonal lines after subtraction.
    """
    Y = S.copy()
    mag = np.abs(Y)
    ph = np.exp(1j * np.angle(Y))
    n_freq, n_time = Y.shape
    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 700.0:
            continue
        p = float(prom[t])
        width = 2 if p < 14.0 else 3
        if frame_time_s[t] < 2.5:
            width += 1
        l0 = max(0, kc - width)
        r0 = min(n_freq - 1, kc + width)
        left = mag[max(0, l0 - 6) : max(0, l0 - 2), t]
        right = mag[min(n_freq, r0 + 3) : min(n_freq, r0 + 7), t]
        if len(left) == 0 and len(right) == 0:
            continue
        if len(left) == 0:
            repl = float(np.median(right))
        elif len(right) == 0:
            repl = float(np.median(left))
        else:
            repl = float(0.5 * (np.median(left) + np.median(right)))
        mag[l0 : r0 + 1, t] = repl
    return mag * ph


def process(x: np.ndarray, sr: int) -> np.ndarray:
    freqs, X = stft_complex(x, sr)
    frame_time_s = np.arange(X.shape[1], dtype=np.float32) * (STFT_HOP / float(sr))
    track, prom = detect_chirp_track(X, freqs)
    x_cancel = cancel_chirp_component(X, track, prom, freqs, frame_time_s)
    base = enhance_spectrum_omlsa_mcra(x_cancel)
    out = apply_chirp_notch(base, track, prom, freqs, frame_time_s)
    out = inpaint_ridge_mag(out, track, prom, freqs, frame_time_s)
    return istft_complex(out, sr, len(x))
