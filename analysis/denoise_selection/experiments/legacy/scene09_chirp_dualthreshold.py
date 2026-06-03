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
    min_win = 30
    min_buf = np.tile(p_smooth[:, None], (1, min_win))
    buf_idx = 0

    alpha_p = 0.8
    alpha_dd = 0.98
    alpha_noise = 0.92
    gain_floor = 0.06
    gain = np.ones_like(power, dtype=np.float32)
    prev_gain2 = np.ones(n_freq, dtype=np.float32)
    prev_gamma = np.ones(n_freq, dtype=np.float32)

    for t in range(n_time):
        p = power[:, t]
        p_smooth = alpha_p * p_smooth + (1.0 - alpha_p) * p
        min_buf[:, buf_idx] = p_smooth
        buf_idx = (buf_idx + 1) % min_win
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
    n_freq, n_time = X.shape
    bins = np.where(freqs >= 700.0)[0]
    track = np.full(n_time, -1, dtype=np.int32)
    prom = np.zeros(n_time, dtype=np.float32)
    if len(bins) == 0:
        return track, prom

    prev_k = -1
    for t in range(n_time):
        hb = mag_db[bins, t]
        k = int(bins[int(np.argmax(hb))])
        p = float(mag_db[k, t] - np.median(hb))
        hb_lin = mag[bins, t] + 1e-12
        flat = float(np.exp(np.mean(np.log(hb_lin))) / np.mean(hb_lin))
        if freqs[k] < 1500.0:
            ok = p > 10.0 and flat < 0.18
        else:
            ok = p > 8.0 and flat < 0.25
        if prev_k >= 0 and ok and abs(k - prev_k) > 12:
            ok = p > 14.0
        if ok:
            track[t] = k
            prom[t] = p
            prev_k = k

    valid = np.where(track >= 0)[0]
    if len(valid) >= 5:
        tr = track.astype(np.float32)
        tr[track < 0] = np.nan
        x = np.arange(n_time, dtype=np.float32)
        tr = np.interp(x, valid.astype(np.float32), tr[valid])
        tr = medfilt(tr, kernel_size=9)
        track = np.clip(np.round(tr), 0, n_freq - 1).astype(np.int32)
    return track, prom


def confidence_from_prom(prom: np.ndarray, low: float = 9.0, high: float = 15.0) -> np.ndarray:
    c = np.clip((prom - low) / max(high - low, 1e-6), 0.0, 1.0)
    # temporal smoothing for stable switching
    if len(c) > 4:
        c2 = c.copy()
        c2[2:-2] = 0.1 * c[:-4] + 0.2 * c[1:-3] + 0.4 * c[2:-2] + 0.2 * c[3:-1] + 0.1 * c[4:]
        c = c2
    return c.astype(np.float32)


def adaptive_cancel(X: np.ndarray, track: np.ndarray, conf: np.ndarray, freqs: np.ndarray) -> np.ndarray:
    Y = X.copy()
    n_freq, n_time = X.shape
    k = np.arange(n_freq, dtype=np.float32)
    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 700.0:
            continue
        c = float(conf[t])
        # interpolate between soft and hard parameters
        beta = (1.0 - c) * 0.62 + c * 1.08
        sigma = (1.0 - c) * 1.8 + c * 1.2
        if freqs[kc] < 1500.0:
            beta *= 0.72
            sigma *= 1.2
        w = np.exp(-0.5 * ((k - kc) / sigma) ** 2).astype(np.float32)
        w /= float(np.max(w) + 1e-12)
        protect = np.ones(n_freq, dtype=np.float32)
        protect[freqs < 500.0] = 0.25
        protect[(freqs >= 500.0) & (freqs < 1200.0)] = 0.45
        protect[(freqs >= 1200.0) & (freqs < 1800.0)] = 0.65
        Y[:, t] = Y[:, t] - beta * protect * w * Y[:, t]
    return Y


def adaptive_notch_and_inpaint(S: np.ndarray, track: np.ndarray, conf: np.ndarray, freqs: np.ndarray) -> np.ndarray:
    n_freq, n_time = S.shape
    k = np.arange(n_freq, dtype=np.float32)
    mag = np.abs(S)
    ph = np.exp(1j * np.angle(S))
    mask = np.ones((n_freq, n_time), dtype=np.float32)

    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 700.0:
            continue
        c = float(conf[t])
        depth = (1.0 - c) * 0.62 + c * 0.93
        sigma = (1.0 - c) * 2.2 + c * 1.6
        if freqs[kc] < 1500.0:
            depth *= 0.82
            sigma *= 1.15
        notch = 1.0 - depth * np.exp(-0.5 * ((k - kc) / sigma) ** 2)
        mask[:, t] = np.clip(notch, 0.04, 1.0).astype(np.float32)

        # inpaint strength tracks confidence: high confidence -> wider inpaint
        width = 2 + int(c > 0.6) + int(c > 0.85)
        l0 = max(0, kc - width)
        r0 = min(n_freq - 1, kc + width)
        left = mag[max(0, l0 - 6) : max(0, l0 - 2), t]
        right = mag[min(n_freq, r0 + 3) : min(n_freq, r0 + 7), t]
        if len(left) or len(right):
            if len(left) == 0:
                repl = float(np.median(right))
            elif len(right) == 0:
                repl = float(np.median(left))
            else:
                repl = float(0.5 * (np.median(left) + np.median(right)))
            mag[l0 : r0 + 1, t] = repl

    if n_time > 2:
        mask[:, 1:-1] = 0.2 * mask[:, :-2] + 0.6 * mask[:, 1:-1] + 0.2 * mask[:, 2:]
    return mag * ph * mask


def rms_err(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    return float(np.sqrt(np.mean((a[:n] - b[:n]) ** 2) + 1e-12))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    in_path = root / "noisy_testset" / "scene09_chirp_interference_snr8.wav"
    out_path = root / "analysis" / "denoise_selection" / "outputs" / "routed" / "scene09_chirp_interference_snr8_dualthreshold.wav"
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
    conf = confidence_from_prom(prom, low=9.0, high=15.0)
    X1 = adaptive_cancel(X, track, conf, freqs)
    X2 = enhance_omlsa_mcra(X1)
    X3 = adaptive_notch_and_inpaint(X2, track, conf, freqs)

    _, y = istft(
        X3,
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

    # quick diagnostic vs noisy
    c_path = root / "noisy_testset" / "clean_reference.wav"
    if c_path.exists():
        c, _ = sf.read(c_path)
        if c.ndim > 1:
            c = c.mean(axis=1)
        c = c.astype(np.float32)
        half = min(len(c), len(y)) // 2
        print(f"global_err_rms: {rms_err(y, c):.6f}")
        print(f"front_err_rms: {rms_err(y[:half], c[:half]):.6f}")


if __name__ == "__main__":
    main()
