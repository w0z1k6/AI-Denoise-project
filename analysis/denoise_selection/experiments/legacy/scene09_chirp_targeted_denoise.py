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


def omlsa_mcra_enhance(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_fft = 512
    hop = 128
    win = "hann"
    freqs, _, X = stft(
        x,
        fs=sr,
        window=win,
        nperseg=n_fft,
        noverlap=n_fft - hop,
        nfft=n_fft,
        boundary="zeros",
        padded=True,
    )

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
    gain_floor = 0.06

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

    S_base = gain * X
    return freqs, X, S_base, gain


def detect_chirp_track(noisy_spec: np.ndarray, freqs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eps = 1e-12
    mag = np.abs(noisy_spec)
    mag_db = 20.0 * np.log10(mag + eps)
    n_freq, n_time = mag.shape

    high_bins = np.where(freqs >= 1800.0)[0]
    if len(high_bins) == 0:
        return np.full(n_time, -1, dtype=np.int32), np.zeros(n_time, dtype=np.float32)

    track = np.full(n_time, -1, dtype=np.int32)
    prom = np.zeros(n_time, dtype=np.float32)

    prev_k = -1
    for t in range(n_time):
        frame_db = mag_db[:, t]
        hb = frame_db[high_bins]
        k_local = int(np.argmax(hb))
        k = int(high_bins[k_local])

        peak_db = frame_db[k]
        med_db = float(np.median(hb))
        p = peak_db - med_db

        # High-band spectral flatness proxy (in linear domain)
        hb_lin = mag[high_bins, t] + eps
        flat = float(np.exp(np.mean(np.log(hb_lin))) / np.mean(hb_lin))

        ok = p > 8.0 and flat < 0.25
        if prev_k >= 0 and ok and abs(k - prev_k) > 10:
            # Reject violent jumps unless prominence is very high
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


def apply_chirp_notch(base_spec: np.ndarray, track: np.ndarray, prom: np.ndarray, freqs: np.ndarray) -> np.ndarray:
    n_freq, n_time = base_spec.shape
    k = np.arange(n_freq, dtype=np.float32)[:, None]
    mask = np.ones((n_freq, n_time), dtype=np.float32)

    for t in range(n_time):
        kc = int(track[t])
        if kc < 0 or freqs[kc] < 1800.0:
            continue

        p = float(prom[t])
        depth = np.clip((p - 8.0) / 14.0, 0.0, 1.0)  # 0..1
        # Keep notch narrow to avoid speech formants damage
        sigma = 1.8
        notch = 1.0 - 0.75 * depth * np.exp(-0.5 * ((k[:, 0] - kc) / sigma) ** 2)
        notch = np.clip(notch, 0.2, 1.0)
        mask[:, t] *= notch.astype(np.float32)

    # Mild temporal smoothing on mask to reduce artifacts
    if n_time > 2:
        mask[:, 1:-1] = 0.2 * mask[:, :-2] + 0.6 * mask[:, 1:-1] + 0.2 * mask[:, 2:]

    return base_spec * mask


def rms_err(a: np.ndarray, b: np.ndarray) -> float:
    m = min(len(a), len(b))
    return float(np.sqrt(np.mean((a[:m] - b[:m]) ** 2) + 1e-12))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out_dir = Path(__file__).resolve().parent

    in_wav = root / "noisy_testset" / "scene09_chirp_interference_snr8.wav"
    clean_ref = root / "noisy_testset" / "clean_reference.wav"
    out_wav = out_dir / "scene09_chirp_targeted_out.wav"

    x, sr = sf.read(in_wav)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)

    freqs, X_noisy, S_base, _ = omlsa_mcra_enhance(x, sr)
    track, prom = detect_chirp_track(X_noisy, freqs)
    S_final = apply_chirp_notch(S_base, track, prom, freqs)

    _, y = istft(
        S_final,
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
        y = y * (0.99 / peak)

    sf.write(out_wav, y, sr)
    print(f"Saved: {out_wav}")

    if clean_ref.exists():
        c, _ = sf.read(clean_ref)
        if c.ndim > 1:
            c = c.mean(axis=1)
        c = c.astype(np.float32)

        # base output for comparison
        _, y_base = istft(
            S_base,
            fs=sr,
            window="hann",
            nperseg=512,
            noverlap=384,
            nfft=512,
            input_onesided=True,
            boundary=True,
        )
        y_base = y_base[: len(x)].astype(np.float32)
        print(f"noisy_err_rms: {rms_err(x, c):.6f}")
        print(f"omlsa_mcra_err_rms: {rms_err(y_base, c):.6f}")
        print(f"chirp_targeted_err_rms: {rms_err(y, c):.6f}")


if __name__ == "__main__":
    main()
