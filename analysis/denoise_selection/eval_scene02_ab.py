import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import soundfile as sf
from scipy.signal import welch
from scipy.stats import kurtosis


def to_mono(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        return x
    return x.mean(axis=1)


def align(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n = min(len(a), len(b))
    return a[:n], b[:n]


def band_power(x: np.ndarray, sr: int, f0: float, f1: float) -> float:
    freqs, psd = welch(x, fs=sr, nperseg=1024)
    mask = (freqs >= f0) & (freqs < f1)
    if not np.any(mask):
        return 1e-12
    return float(np.trapz(psd[mask], freqs[mask]) + 1e-12)


def band_snr(clean: np.ndarray, test: np.ndarray, sr: int, f0: float, f1: float) -> float:
    clean, test = align(clean, test)
    noise = test - clean
    p_sig = band_power(clean, sr, f0, f1)
    p_noise = band_power(noise, sr, f0, f1)
    return 10.0 * np.log10(p_sig / p_noise)


def evaluate(clean: np.ndarray, noisy: np.ndarray, denoised: np.ndarray, sr: int) -> Dict[str, float]:
    clean, noisy = align(clean, noisy)
    clean, denoised = align(clean, denoised)
    noisy, denoised = align(noisy, denoised)

    err = denoised - clean
    out = {
        "high_band_snr_db": band_snr(clean, denoised, sr, 3400, 8000),
        "high_band_snr_gain_vs_noisy_db": band_snr(clean, denoised, sr, 3400, 8000)
        - band_snr(clean, noisy, sr, 3400, 8000),
        "residual_rms": float(np.sqrt(np.mean(err**2))),
        "residual_kurtosis": float(kurtosis(err, fisher=False, bias=False)),
    }
    return out


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parents[1]

    clean_path = project_root / "noisy_testset" / "clean_reference.wav"
    noisy_path = project_root / "noisy_testset" / "scene02_white_snr5.wav"
    baseline_metrics = project_root / "analysis" / "scene_details" / "scene02_white_snr5_metrics.json"
    noisereduce_out = script_dir / "scene02_noisereduce_out.wav"
    deepfilternet_out = script_dir / "scene02_deepfilternet_out.wav"

    if not clean_path.exists():
        raise FileNotFoundError(
            f"Missing clean reference: {clean_path}. Cannot compute supervised AB metrics."
        )
    if not noisereduce_out.exists() or not deepfilternet_out.exists():
        raise FileNotFoundError("Run both denoise scripts before evaluation.")

    clean, sr_clean = sf.read(clean_path)
    noisy, sr_noisy = sf.read(noisy_path)
    nr_out, sr_nr = sf.read(noisereduce_out)
    df_out, sr_df = sf.read(deepfilternet_out)

    clean = to_mono(clean)
    noisy = to_mono(noisy)
    nr_out = to_mono(nr_out)
    df_out = to_mono(df_out)

    if len({sr_clean, sr_noisy, sr_nr, sr_df}) != 1:
        raise ValueError("Sample rates differ across files, please resample before AB evaluation.")
    sr = sr_clean

    with baseline_metrics.open("r", encoding="utf-8") as f:
        baseline = json.load(f)
    baseline_residual_rms = baseline["baseline_residual"]["rms"]
    baseline_residual_kurtosis = baseline["baseline_residual"]["kurtosis"]

    nr_metrics = evaluate(clean, noisy, nr_out, sr)
    df_metrics = evaluate(clean, noisy, df_out, sr)

    report = {
        "baseline_thresholds": {
            "residual_rms_upper": baseline_residual_rms,
            "residual_kurtosis_upper": baseline_residual_kurtosis,
        },
        "noisereduce": nr_metrics,
        "deepfilternet": df_metrics,
        "decision_rule": {
            "prefer_higher_high_band_snr_gain": True,
            "require_residual_rms_below_baseline": True,
            "prefer_residual_kurtosis_not_worse_than_baseline": True,
        },
    }

    out_json = script_dir / "scene02_ab_eval_report.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_json}")


if __name__ == "__main__":
    main()
