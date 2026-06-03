from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter
from scipy.signal import stft, istft


def estimate_noise_psd_min_stat(power: np.ndarray, alpha: float = 0.82) -> np.ndarray:
    """
    Minimum-statistics-like recursive noise PSD estimate.
    power shape: [freq, time]
    """
    n_freq, n_time = power.shape
    noise_psd = np.zeros_like(power)
    p_min = power[:, 0].copy()
    noise_psd[:, 0] = p_min
    for t in range(1, n_time):
        p_min = np.minimum(power[:, t], alpha * p_min + (1.0 - alpha) * power[:, t])
        noise_psd[:, t] = p_min
    return noise_psd


def dd_wiener_gain(power: np.ndarray, noise_psd: np.ndarray) -> np.ndarray:
    """
    Decision-directed Wiener filtering gain.
    """
    eps = 1e-12
    gamma = power / (noise_psd + eps)  # a posteriori SNR

    gain = np.zeros_like(power)
    prev_gain2 = np.ones(power.shape[0], dtype=np.float32)
    alpha_dd = 0.98
    min_gain = 0.05

    for t in range(power.shape[1]):
        if t == 0:
            xi = np.maximum(gamma[:, t] - 1.0, 0.0)
        else:
            xi = alpha_dd * prev_gain2 * gamma[:, t - 1] + (1.0 - alpha_dd) * np.maximum(
                gamma[:, t] - 1.0, 0.0
            )
        g = xi / (1.0 + xi)
        g = np.clip(g, min_gain, 1.0)
        gain[:, t] = g
        prev_gain2 = g**2
    return gain


def apply_high_freq_extra_suppression(gain: np.ndarray, freqs: np.ndarray) -> np.ndarray:
    """
    Extra suppression in high-frequency band where residual hiss is common.
    """
    hf = freqs >= 3400.0
    g = gain.copy()
    if np.any(hf):
        g[hf, :] *= 0.92
    return np.clip(g, 0.04, 1.0)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    work_dir = Path(__file__).resolve().parent

    in_wav = work_dir / "scene02_deepfilternet_out.wav"
    out_wav = work_dir / "scene02_deepfilternet_mathboost_out.wav"

    if not in_wav.exists():
        # fallback for earlier naming
        alt = work_dir / "scene02_white_snr5.wav"
        if alt.exists():
            in_wav = alt
        else:
            raise FileNotFoundError(f"Input file not found: {in_wav}")

    x, sr = sf.read(in_wav)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)

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

    mag = np.abs(X)
    phase = np.exp(1j * np.angle(X))
    power = mag**2

    noise_psd = estimate_noise_psd_min_stat(power, alpha=0.82)
    gain = dd_wiener_gain(power, noise_psd)
    gain = apply_high_freq_extra_suppression(gain, freqs)

    # Mild 2D smoothing to suppress musical-noise granularity
    gain = uniform_filter(gain, size=(3, 3), mode="nearest")
    gain = np.clip(gain, 0.04, 1.0)

    Y = gain * mag * phase
    _, y = istft(
        Y,
        fs=sr,
        window=win,
        nperseg=n_fft,
        noverlap=n_fft - hop,
        nfft=n_fft,
        input_onesided=True,
        boundary=True,
    )

    y = y[: len(x)]
    peak = np.max(np.abs(y)) + 1e-12
    if peak > 0.99:
        y = y * (0.99 / peak)

    sf.write(out_wav, y.astype(np.float32), sr)
    print(f"Input : {in_wav}")
    print(f"Output: {out_wav}")


if __name__ == "__main__":
    main()
