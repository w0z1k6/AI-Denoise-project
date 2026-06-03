from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import istft, medfilt, stft
from scipy.special import exp1


def omlsa_gain(prior_snr: np.ndarray, post_snr: np.ndarray, gain_floor: float) -> np.ndarray:
    eps = 1e-12
    xi = np.maximum(prior_snr, 0.0)
    gamma = np.maximum(post_snr, 1e-6)
    v = gamma * xi / (1.0 + xi + eps)
    gh1 = (xi / (1.0 + xi + eps)) * np.exp(0.5 * exp1(np.maximum(v, 1e-12)))
    return np.clip(gh1, gain_floor, 1.0)


def enhance_omlsa_mcra(X: np.ndarray) -> np.ndarray:
    power = np.abs(X) ** 2
    n_freq, n_time = power.shape
    eps = 1e-12
    init_frames = min(12, n_time)
    noise_psd = np.mean(power[:, :init_frames], axis=1, keepdims=True).repeat(n_time, axis=1)

    p_smooth = power[:, 0].copy()
    win_min = 30
    min_buf = np.tile(p_smooth[:, None], (1, win_min))
    buf_idx = 0

    alpha_p = 0.8
    alpha_dd = 0.98
    alpha_noise = 0.92
    gain_floor = 0.03
    gain = np.ones_like(power, dtype=np.float32)
    prev_gain2 = np.ones(n_freq, dtype=np.float32)
    prev_gamma = np.ones(n_freq, dtype=np.float32)

    for t in range(n_time):
        p = power[:, t]
        p_smooth = alpha_p * p_smooth + (1.0 - alpha_p) * p
        min_buf[:, buf_idx] = p_smooth
        buf_idx = (buf_idx + 1) % win_min
        p_min = np.min(min_buf, axis=1)

        noise_prev = noise_psd[:, t - 1] if t > 0 else noise_psd[:, 0]
        gamma = np.maximum(p / (noise_prev + eps), 1e-6)
        if t == 0:
            xi = np.maximum(gamma - 1.0, 0.0)
        else:
            xi = alpha_dd * prev_gain2 * prev_gamma + (1.0 - alpha_dd) * np.maximum(gamma - 1.0, 0.0)
        xi = np.maximum(xi, 0.0)

        v = gamma * xi / (1.0 + xi + eps)
        p_h1 = 1.0 / (1.0 + np.exp(-(v - 1.0)))
        p_noise = 1.0 - p_h1
        alpha_t = alpha_noise + 0.06 * p_h1
        noise_new = alpha_t * noise_prev + (1.0 - alpha_t) * (p_noise * p + (1.0 - p_noise) * p_min)
        noise_new = np.maximum(noise_new, eps)
        noise_psd[:, t] = noise_new

        gamma = np.maximum(p / (noise_new + eps), 1e-6)
        gh1 = omlsa_gain(xi, gamma, gain_floor=gain_floor)
        g = np.power(gh1, p_h1) * np.power(gain_floor, 1.0 - p_h1)
        gain[:, t] = np.clip(g, gain_floor, 1.0).astype(np.float32)
        prev_gain2 = gain[:, t] ** 2
        prev_gamma = gamma
    return gain * X


def detect_track(X: np.ndarray, freqs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mag = np.abs(X)
    mag_db = 20.0 * np.log10(mag + 1e-12)
    n_freq, n_time = mag.shape
    bins = np.where(freqs >= 400.0)[0]
    track = np.full(n_time, -1, dtype=np.int32)
    prom = np.zeros(n_time, dtype=np.float32)
    if len(bins) == 0:
        return track, prom

    prev_k = -1
    for t in range(n_time):
        hb = mag_db[bins, t]
        idx = int(np.argmax(hb))
        k = int(bins[idx])
        p = float(mag_db[k, t] - np.median(hb))
        hb_lin = mag[bins, t] + 1e-12
        flat = float(np.exp(np.mean(np.log(hb_lin))) / np.mean(hb_lin))
        ok = p > 7.0 and flat < 0.30
        if prev_k >= 0 and ok and abs(k - prev_k) > 16:
            ok = p > 12.0
        if ok:
            track[t] = k
            prom[t] = p
            prev_k = k

    valid = np.where(track >= 0)[0]
    if len(valid) >= 5:
        tr = track.astype(np.float32)
        tr[track < 0] = np.nan
        x = np.arange(n_time, dtype=np.float32)
        tr_interp = np.interp(x, valid.astype(np.float32), tr[valid])
        track = np.clip(np.round(medfilt(tr_interp, kernel_size=11)), 0, n_freq - 1).astype(np.int32)
    return track, prom


def apply_ultrahard(X: np.ndarray, freqs: np.ndarray, track: np.ndarray, prom: np.ndarray) -> np.ndarray:
    Y = X.copy()
    mag = np.abs(Y)
    ph = np.exp(1j * np.angle(Y))
    n_freq, n_time = Y.shape
    k = np.arange(n_freq, dtype=np.float32)

    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 400.0:
            continue
        p = float(prom[t])
        s = np.clip((p - 7.0) / 8.0, 0.0, 1.0)

        beta = 0.8 + 0.45 * s
        sigma = 1.1 + 0.7 * (1.0 - s)
        w = np.exp(-0.5 * ((k - kc) / sigma) ** 2).astype(np.float32)
        w /= float(np.max(w) + 1e-12)

        protect = np.ones(n_freq, dtype=np.float32)
        protect[freqs < 700.0] = 0.45
        protect[(freqs >= 700.0) & (freqs < 1500.0)] = 0.8
        Y[:, t] = Y[:, t] - beta * protect * w * Y[:, t]

        # Aggressive ridge inpainting
        width = 3 if s < 0.5 else 4
        l0 = max(0, kc - width)
        r0 = min(n_freq - 1, kc + width)
        left = mag[max(0, l0 - 8) : max(0, l0 - 3), t]
        right = mag[min(n_freq, r0 + 4) : min(n_freq, r0 + 9), t]
        if len(left) or len(right):
            if len(left) == 0:
                repl = float(np.median(right))
            elif len(right) == 0:
                repl = float(np.median(left))
            else:
                repl = float(0.5 * (np.median(left) + np.median(right)))
            mag[l0 : r0 + 1, t] = repl

    Y = mag * ph
    # Global notch-like mask on tracked bins
    mask = np.ones((n_freq, n_time), dtype=np.float32)
    for t in range(n_time):
        kc = int(track[t])
        if kc < 0:
            continue
        sigma = 2.0
        notch = 1.0 - 0.93 * np.exp(-0.5 * ((k - kc) / sigma) ** 2)
        mask[:, t] = np.clip(notch, 0.02, 1.0).astype(np.float32)
    if n_time > 2:
        mask[:, 1:-1] = 0.2 * mask[:, :-2] + 0.6 * mask[:, 1:-1] + 0.2 * mask[:, 2:]
    return Y * mask


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    in_path = root / "noisy_testset" / "scene09_chirp_interference_snr8.wav"
    out_path = root / "analysis" / "denoise_selection" / "outputs" / "routed" / "scene09_chirp_interference_snr8_ultrahard.wav"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    x, sr = sf.read(in_path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)

    freqs, _, X = stft(
        x,
        fs=sr,
        window="hann",
        nperseg=512,
        noverlap=384,
        nfft=512,
        boundary="zeros",
        padded=True,
    )
    track, prom = detect_track(X, freqs)
    X1 = apply_ultrahard(X, freqs, track, prom)
    X2 = enhance_omlsa_mcra(X1)
    _, y = istft(
        X2,
        fs=sr,
        window="hann",
        nperseg=512,
        noverlap=384,
        nfft=512,
        input_onesided=True,
        boundary=True,
    )
    y = y[: len(x)].astype(np.float32)
    peak = float(np.max(np.abs(y)) + 1e-12)
    if peak > 0.99:
        y *= 0.99 / peak
    sf.write(out_path, y, sr)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
