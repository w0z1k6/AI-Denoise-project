from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter
from scipy.signal import stft, istft


def rms_err(x: np.ndarray, y: np.ndarray) -> float:
    m = min(len(x), len(y))
    return float(np.sqrt(np.mean((x[:m] - y[:m]) ** 2) + 1e-12))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    x, sr = sf.read(root / "analysis" / "denoise_selection" / "scene02_deepfilternet_out.wav")
    c, _ = sf.read(root / "noisy_testset" / "clean_reference.wav")
    if x.ndim > 1:
        x = x.mean(axis=1)
    if c.ndim > 1:
        c = c.mean(axis=1)
    x = x.astype(np.float32)
    c = c.astype(np.float32)
    m = min(len(x), len(c))
    x = x[:m]
    c = c[:m]

    freqs, _, X = stft(
        x, fs=sr, window="hann", nperseg=512, noverlap=384, nfft=512, boundary="zeros", padded=True
    )
    mag = np.abs(X)
    phase = np.exp(1j * np.angle(X))
    power = mag**2
    eps = 1e-12

    best = (1e9, None, None, None)
    for alpha in [0.90, 0.94, 0.97]:
        noise = np.zeros_like(power)
        p_min = power[:, 0].copy()
        noise[:, 0] = p_min
        for t in range(1, power.shape[1]):
            p_min = np.minimum(power[:, t], alpha * p_min + (1.0 - alpha) * power[:, t])
            noise[:, t] = p_min

        gamma = power / (noise + eps)
        gain0 = np.clip((gamma - 1.0) / gamma, 0.7, 1.0)

        for hf_scale in [1.0, 0.99, 0.97, 0.95]:
            gain = gain0.copy()
            gain[freqs >= 3400.0, :] *= hf_scale
            gain = np.clip(uniform_filter(gain, size=(3, 3), mode="nearest"), 0.7, 1.0)
            _, y = istft(
                gain * mag * phase,
                fs=sr,
                window="hann",
                nperseg=512,
                noverlap=384,
                nfft=512,
                input_onesided=True,
                boundary=True,
            )
            y = y[:m].astype(np.float32)

            for lam in [0.0, 0.1, 0.2, 0.3, 0.4]:
                z = (1.0 - lam) * x + lam * y
                e = rms_err(z, c)
                if e < best[0]:
                    best = (e, alpha, hf_scale, lam)

    print("deepfilternet_err_rms:", rms_err(x, c))
    print("best_err_rms, alpha, hf_scale, lam:", best)


if __name__ == "__main__":
    main()
