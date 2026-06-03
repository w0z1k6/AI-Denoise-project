from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import istft, stft
from scipy.special import exp1


def omlsa_gain(prior_snr: np.ndarray, post_snr: np.ndarray, gain_floor: float) -> np.ndarray:
    """
    OMLSA-like gain:
    G_H1 = xi/(1+xi) * exp(0.5 * E1(v)), v = gamma*xi/(1+xi)
    Final gain blends speech-presence and floor for robustness.
    """
    eps = 1e-12
    xi = np.maximum(prior_snr, 0.0)
    gamma = np.maximum(post_snr, 1e-6)
    v = gamma * xi / (1.0 + xi + eps)
    gh1 = (xi / (1.0 + xi + eps)) * np.exp(0.5 * exp1(np.maximum(v, 1e-12)))
    gh1 = np.clip(gh1, gain_floor, 1.0)
    return gh1


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out_dir = Path(__file__).resolve().parent

    in_wav = root / "noisy_testset" / "scene02_white_snr5.wav"
    out_wav = out_dir / "scene02_omlsa_mcra_out.wav"

    x, sr = sf.read(in_wav)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)

    n_fft = 512
    hop = 128
    win = "hann"
    _, _, X = stft(
        x,
        fs=sr,
        window=win,
        nperseg=n_fft,
        noverlap=n_fft - hop,
        nfft=n_fft,
        boundary="zeros",
        padded=True,
    )

    Y = X
    power = np.abs(Y) ** 2
    n_freq, n_time = power.shape
    eps = 1e-12

    # Initial noise PSD from first frames (fallback for unknown VAD)
    init_frames = min(12, n_time)
    noise_psd = np.mean(power[:, :init_frames], axis=1, keepdims=True).repeat(n_time, axis=1)

    # MCRA-like minima tracking and adaptive update
    p_smooth = power[:, 0].copy()
    p_min = p_smooth.copy()
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
        gamma = p / (noise_prev + eps)
        gamma = np.maximum(gamma, 1e-6)

        # Decision-directed prior SNR
        if t == 0:
            xi = np.maximum(gamma - 1.0, 0.0)
        else:
            xi = alpha_dd * prev_gain2 * prev_gamma + (1.0 - alpha_dd) * np.maximum(gamma - 1.0, 0.0)
        xi = np.maximum(xi, 0.0)

        v = gamma * xi / (1.0 + xi + eps)
        # Speech presence probability (smaller -> likely noise-only)
        p_h1 = 1.0 / (1.0 + np.exp(-(v - 1.0)))
        p_noise = 1.0 - p_h1

        # MCRA-like adaptive noise update:
        # more update in likely noise bins, less update in speech bins
        alpha_t = alpha_noise + 0.06 * p_h1
        noise_new = alpha_t * noise_prev + (1.0 - alpha_t) * (
            p_noise * p + (1.0 - p_noise) * p_min
        )
        noise_new = np.maximum(noise_new, eps)
        noise_psd[:, t] = noise_new

        gamma = p / (noise_new + eps)
        gh1 = omlsa_gain(xi, gamma, gain_floor=gain_floor)
        # OMLSA blend with gain floor via speech presence probability
        g = np.power(gh1, p_h1) * np.power(gain_floor, 1.0 - p_h1)
        g = np.clip(g, gain_floor, 1.0)
        gain[:, t] = g.astype(np.float32)

        prev_gain2 = g**2
        prev_gamma = gamma

    S_hat = gain * Y
    _, y = istft(
        S_hat,
        fs=sr,
        window=win,
        nperseg=n_fft,
        noverlap=n_fft - hop,
        nfft=n_fft,
        input_onesided=True,
        boundary=True,
    )
    y = y[: len(x)].astype(np.float32)
    peak = float(np.max(np.abs(y)) + 1e-12)
    if peak > 0.99:
        y = y * (0.99 / peak)

    sf.write(out_wav, y, sr)
    print(f"Input : {in_wav}")
    print(f"Output: {out_wav}")


if __name__ == "__main__":
    main()
