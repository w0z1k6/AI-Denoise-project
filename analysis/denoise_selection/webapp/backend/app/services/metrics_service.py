from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import spectrogram, stft, welch
from scipy.stats import kurtosis, skew


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-12))


def _frame(x: np.ndarray, frame: int, hop: int) -> np.ndarray:
    if len(x) < frame:
        out = np.zeros((1, frame), dtype=np.float32)
        out[0, : len(x)] = x
        return out
    n = 1 + (len(x) - frame) // hop
    return np.stack([x[i * hop : i * hop + frame] for i in range(n)], axis=0)


def _energy_curve(x: np.ndarray, frame: int = 512, hop: int = 128) -> np.ndarray:
    f = _frame(x, frame, hop)
    return np.mean(f**2, axis=1)


def _zcr_curve(x: np.ndarray, frame: int = 512, hop: int = 128) -> np.ndarray:
    f = _frame(x, frame, hop)
    signs = np.sign(f)
    return np.mean(np.abs(np.diff(signs, axis=1)), axis=1) * 0.5


def _stft_mag_db(x: np.ndarray, sr: int, n_fft: int = 512, hop: int = 128) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    freqs, times, z = stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft - hop, nfft=n_fft, window="hann")
    mag_db = 20 * np.log10(np.abs(z) + 1e-8)
    return freqs, times, mag_db


def _band_energy(x: np.ndarray, sr: int) -> tuple[list[str], list[float]]:
    freqs, pxx = welch(x, fs=sr, nperseg=512)
    bands = [(0, 200), (200, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000)]
    vals = []
    labels = []
    for lo, hi in bands:
        m = (freqs >= lo) & (freqs < hi)
        vals.append(float(np.mean(pxx[m]) if np.any(m) else 0.0))
        labels.append(f"{lo}-{hi}Hz")
    return labels, vals


def _centroid_bandwidth_rolloff(x: np.ndarray, sr: int, n_fft: int = 512, hop: int = 128) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    freqs, _, z = stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft - hop, nfft=n_fft, window="hann")
    mag = np.abs(z) + 1e-12
    p = mag / np.sum(mag, axis=0, keepdims=True)
    centroid = np.sum(freqs[:, None] * p, axis=0)
    bandwidth = np.sqrt(np.sum(((freqs[:, None] - centroid[None, :]) ** 2) * p, axis=0))
    cdf = np.cumsum(p, axis=0)
    roll_idx = np.argmax(cdf >= 0.85, axis=0)
    rolloff = freqs[roll_idx]
    return centroid, bandwidth, rolloff


def _snr_from_noise_prefix(x: np.ndarray, noise_sec: float, sr: int) -> float:
    n = max(1, int(noise_sec * sr))
    noise = x[:n]
    signal = x[n:] if len(x) > n else x
    return float(10 * np.log10((np.mean(signal**2) + 1e-12) / (np.mean(noise**2) + 1e-12)))


def _figure_line(x: list[float], y: list[float], name: str, title: str, xname: str, yname: str) -> dict[str, Any]:
    return {
        "data": [{"type": "scatter", "mode": "lines", "x": x, "y": y, "name": name}],
        "layout": {"title": title, "xaxis": {"title": xname}, "yaxis": {"title": yname}},
    }


def _figure_multi_line(lines: list[dict[str, Any]], title: str, xname: str, yname: str) -> dict[str, Any]:
    return {"data": lines, "layout": {"title": title, "xaxis": {"title": xname}, "yaxis": {"title": yname}}}


def _heatmap(z: np.ndarray, x: list[float], y: list[float], title: str, xname: str, yname: str) -> dict[str, Any]:
    return {
        "data": [{"type": "heatmap", "z": z.tolist(), "x": x, "y": y, "colorscale": "Viridis"}],
        "layout": {"title": title, "xaxis": {"title": xname}, "yaxis": {"title": yname}},
    }


def build_metrics_and_plots(
    original: np.ndarray,
    denoised: np.ndarray,
    residual: np.ndarray,
    sr: int,
    route: list[str],
    method: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    n = min(len(original), len(denoised), len(residual))
    original = original[:n]
    denoised = denoised[:n]
    residual = residual[:n]
    t = np.arange(n) / float(sr)

    en_o = _energy_curve(original)
    en_d = _energy_curve(denoised)
    en_r = _energy_curve(residual)
    zcr_o = _zcr_curve(original)
    zcr_d = _zcr_curve(denoised)
    zcr_r = _zcr_curve(residual)
    tf = (np.arange(len(en_o)) * 128) / float(sr)

    f_o, p_o = welch(original, fs=sr, nperseg=512)
    f_d, p_d = welch(denoised, fs=sr, nperseg=512)
    f_r, p_r = welch(residual, fs=sr, nperseg=512)

    labels, band_o = _band_energy(original, sr)
    _, band_d = _band_energy(denoised, sr)
    _, band_r = _band_energy(residual, sr)

    cen_o, bw_o, ro_o = _centroid_bandwidth_rolloff(original, sr)
    cen_d, bw_d, ro_d = _centroid_bandwidth_rolloff(denoised, sr)

    fs_o, ts_o, stft_o = _stft_mag_db(original, sr)
    fs_d, ts_d, stft_d = _stft_mag_db(denoised, sr)
    fs_r, ts_r, stft_r = _stft_mag_db(residual, sr)

    snr_in = _snr_from_noise_prefix(original, 0.5, sr)
    snr_out = _snr_from_noise_prefix(denoised, 0.5, sr)
    snr_delta = snr_out - snr_in

    frame = _frame(residual, 512, 128)
    frame_rms = np.sqrt(np.mean(frame**2, axis=1) + 1e-12)

    metrics = {
        "sample_rate": sr,
        "length_sec": float(n / sr),
        "method": method,
        "route": route,
        "rms": {"original": _rms(original), "denoised": _rms(denoised), "residual": _rms(residual)},
        "snr_db": {"input_est": snr_in, "output_est": snr_out, "delta": snr_delta},
        "residual_stats": {
            "kurtosis": float(kurtosis(residual, fisher=False, bias=False)),
            "skewness": float(skew(residual, bias=False)),
        },
    }

    plots: dict[str, Any] = {"groups": []}

    # A. Time-domain (5)
    time_group = {
        "group": "time_domain",
        "title": "Time Domain",
        "plots": [
            {"id": "waveform_compare", "title": "Original vs Denoised Waveform", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": t.tolist(), "y": original.tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": t.tolist(), "y": denoised.tolist(), "name": "denoised"},
            ], "Waveform Compare", "Time(s)", "Amplitude")},
            {"id": "waveform_zoom", "title": "Zoomed Waveform (first 2s)", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": t[t <= 2.0].tolist(), "y": original[t <= 2.0].tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": t[t <= 2.0].tolist(), "y": denoised[t <= 2.0].tolist(), "name": "denoised"},
            ], "Zoomed Waveform", "Time(s)", "Amplitude")},
            {"id": "energy_envelope", "title": "Energy Envelope", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": tf.tolist(), "y": en_o.tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": tf.tolist(), "y": en_d.tolist(), "name": "denoised"},
                {"type": "scatter", "mode": "lines", "x": tf.tolist(), "y": en_r.tolist(), "name": "residual"},
            ], "Energy Envelope", "Time(s)", "Energy")},
            {"id": "short_time_energy", "title": "Short-time Energy", "figure": _figure_line(tf.tolist(), en_d.tolist(), "denoised", "Short-time Energy", "Time(s)", "Energy")},
            {"id": "zcr_curve", "title": "ZCR Curves", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": tf.tolist(), "y": zcr_o.tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": tf.tolist(), "y": zcr_d.tolist(), "name": "denoised"},
                {"type": "scatter", "mode": "lines", "x": tf.tolist(), "y": zcr_r.tolist(), "name": "residual"},
            ], "Zero-crossing Rate", "Time(s)", "ZCR")},
        ],
    }
    plots["groups"].append(time_group)

    # B. Frequency-domain (5)
    freq_group = {
        "group": "frequency_domain",
        "title": "Frequency Domain",
        "plots": [
            {"id": "amplitude_spectrum", "title": "Amplitude Spectrum Compare", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": f_o.tolist(), "y": np.sqrt(p_o).tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": f_d.tolist(), "y": np.sqrt(p_d).tolist(), "name": "denoised"},
            ], "Amplitude Spectrum", "Frequency(Hz)", "Amplitude")},
            {"id": "psd_compare", "title": "PSD Compare", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": f_o.tolist(), "y": (10 * np.log10(p_o + 1e-12)).tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": f_d.tolist(), "y": (10 * np.log10(p_d + 1e-12)).tolist(), "name": "denoised"},
                {"type": "scatter", "mode": "lines", "x": f_r.tolist(), "y": (10 * np.log10(p_r + 1e-12)).tolist(), "name": "residual"},
            ], "Power Spectral Density", "Frequency(Hz)", "PSD(dB)")},
            {"id": "third_octave_energy", "title": "1/3 Octave-like Band Energy", "figure": {
                "data": [{"type": "bar", "x": labels, "y": band_o, "name": "original"}, {"type": "bar", "x": labels, "y": band_d, "name": "denoised"}],
                "layout": {"title": "Band Energy", "barmode": "group", "xaxis": {"title": "Band"}, "yaxis": {"title": "Energy"}},
            }},
            {"id": "band_energy_bar", "title": "Band Energy Residual", "figure": {
                "data": [{"type": "bar", "x": labels, "y": band_r, "name": "residual"}],
                "layout": {"title": "Residual Band Energy", "xaxis": {"title": "Band"}, "yaxis": {"title": "Energy"}},
            }},
            {"id": "centroid_bandwidth_rolloff", "title": "Centroid/Bandwidth/Rolloff", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": tf[: len(cen_o)].tolist(), "y": cen_o.tolist(), "name": "centroid_original"},
                {"type": "scatter", "mode": "lines", "x": tf[: len(cen_d)].tolist(), "y": cen_d.tolist(), "name": "centroid_denoised"},
                {"type": "scatter", "mode": "lines", "x": tf[: len(bw_o)].tolist(), "y": bw_o.tolist(), "name": "bandwidth_original"},
                {"type": "scatter", "mode": "lines", "x": tf[: len(ro_o)].tolist(), "y": ro_o.tolist(), "name": "rolloff_original"},
                {"type": "scatter", "mode": "lines", "x": tf[: len(ro_d)].tolist(), "y": ro_d.tolist(), "name": "rolloff_denoised"},
            ], "Spectral Features", "Time(s)", "Hz")},
        ],
    }
    plots["groups"].append(freq_group)

    # C. Time-frequency (6)
    tf_group = {
        "group": "time_frequency",
        "title": "Time-Frequency",
        "plots": [
            {"id": "mel_original", "title": "Original Mel-like Spectrogram", "figure": _heatmap(stft_o, ts_o.tolist(), fs_o.tolist(), "Original STFT dB", "Time(s)", "Frequency(Hz)")},
            {"id": "mel_denoised", "title": "Denoised Mel-like Spectrogram", "figure": _heatmap(stft_d, ts_d.tolist(), fs_d.tolist(), "Denoised STFT dB", "Time(s)", "Frequency(Hz)")},
            {"id": "mel_residual", "title": "Residual Mel-like Spectrogram", "figure": _heatmap(stft_r, ts_r.tolist(), fs_r.tolist(), "Residual STFT dB", "Time(s)", "Frequency(Hz)")},
            {"id": "stft_original", "title": "Original STFT", "figure": _heatmap(stft_o, ts_o.tolist(), fs_o.tolist(), "Original STFT", "Time(s)", "Frequency(Hz)")},
            {"id": "stft_denoised", "title": "Denoised STFT", "figure": _heatmap(stft_d, ts_d.tolist(), fs_d.tolist(), "Denoised STFT", "Time(s)", "Frequency(Hz)")},
            {"id": "stft_residual", "title": "Residual STFT", "figure": _heatmap(stft_r, ts_r.tolist(), fs_r.tolist(), "Residual STFT", "Time(s)", "Frequency(Hz)")},
        ],
    }
    plots["groups"].append(tf_group)

    # D. Quality/error (8)
    local_snr = 10 * np.log10((en_d + 1e-12) / (en_r[: len(en_d)] + 1e-12))
    q_group = {
        "group": "quality_error",
        "title": "Quality and Error",
        "plots": [
            {"id": "global_snr_compare", "title": "Global SNR Compare", "figure": {
                "data": [{"type": "bar", "x": ["Input", "Output"], "y": [snr_in, snr_out]}],
                "layout": {"title": "Global SNR(dB)"},
            }},
            {"id": "frame_snr_curve", "title": "Frame SNR Curve", "figure": _figure_line(tf[: len(local_snr)].tolist(), local_snr.tolist(), "frame_snr", "Frame SNR", "Time(s)", "SNR(dB)")},
            {"id": "band_snr_heatmap", "title": "Band SNR Heatmap", "figure": _heatmap(np.array([band_d, band_r]), labels, ["denoised", "residual"], "Band Energy Heatmap", "Band", "Signal")},
            {"id": "residual_rms_hist", "title": "Residual RMS Histogram", "figure": {"data": [{"type": "histogram", "x": frame_rms.tolist()}], "layout": {"title": "Residual Frame RMS"}}},
            {"id": "residual_kurtosis_skew", "title": "Residual Kurtosis/Skewness", "figure": {"data": [{"type": "bar", "x": ["kurtosis", "skewness"], "y": [metrics['residual_stats']['kurtosis'], metrics['residual_stats']['skewness']]}], "layout": {"title": "Residual Statistics"}}},
            {"id": "flatness_compare", "title": "Spectral Flatness Compare", "figure": {"data": [{"type": "bar", "x": ["original", "denoised", "residual"], "y": [float(np.exp(np.mean(np.log(np.abs(original) + 1e-12))) / (np.mean(np.abs(original)) + 1e-12)), float(np.exp(np.mean(np.log(np.abs(denoised) + 1e-12))) / (np.mean(np.abs(denoised)) + 1e-12)), float(np.exp(np.mean(np.log(np.abs(residual) + 1e-12))) / (np.mean(np.abs(residual)) + 1e-12))]}], "layout": {"title": "Spectral Flatness"}}},
            {"id": "delta_snr", "title": "Delta SNR", "figure": {"data": [{"type": "bar", "x": ["Delta SNR"], "y": [snr_delta]}], "layout": {"title": "SNR Improvement(dB)"}}},
            {"id": "algorithm_radar", "title": "Algorithm Radar", "figure": {
                "data": [{"type": "scatterpolar", "r": [max(snr_out, 0), max(snr_delta + 5, 0), max(1 - metrics["rms"]["residual"], 0), max(2 - abs(metrics["residual_stats"]["skewness"]), 0)], "theta": ["OutputSNR", "DeltaSNR+5", "1-ResidualRMS", "2-AbsSkew"], "fill": "toself", "name": "score"}],
                "layout": {"title": f"Radar ({'+'.join(route)})"},
            }},
        ],
    }
    plots["groups"].append(q_group)

    # E. Statistical distribution (4)
    s_group = {
        "group": "stat_distribution",
        "title": "Statistical Distribution",
        "plots": [
            {"id": "amp_hist_compare", "title": "Amplitude Histogram", "figure": {
                "data": [
                    {"type": "histogram", "x": original.tolist(), "name": "original", "opacity": 0.5},
                    {"type": "histogram", "x": denoised.tolist(), "name": "denoised", "opacity": 0.5},
                    {"type": "histogram", "x": residual.tolist(), "name": "residual", "opacity": 0.5},
                ],
                "layout": {"title": "Amplitude Distribution", "barmode": "overlay"},
            }},
            {"id": "frame_rms_box", "title": "Frame RMS Boxplot", "figure": {
                "data": [{"type": "box", "y": _frame(original, 512, 128).var(axis=1).tolist(), "name": "original"},
                         {"type": "box", "y": _frame(denoised, 512, 128).var(axis=1).tolist(), "name": "denoised"},
                         {"type": "box", "y": frame_rms.tolist(), "name": "residual"}],
                "layout": {"title": "Frame RMS Boxplot"},
            }},
            {"id": "cdf_compare", "title": "CDF Compare", "figure": _figure_multi_line([
                {"type": "scatter", "mode": "lines", "x": np.sort(original).tolist(), "y": np.linspace(0, 1, len(original)).tolist(), "name": "original"},
                {"type": "scatter", "mode": "lines", "x": np.sort(denoised).tolist(), "y": np.linspace(0, 1, len(denoised)).tolist(), "name": "denoised"},
            ], "CDF", "Amplitude", "CDF")},
            {"id": "energy_flatness_scatter", "title": "Energy vs Flatness Scatter", "figure": {
                "data": [{"type": "scatter", "mode": "markers", "x": en_d.tolist(), "y": zcr_d.tolist(), "name": "denoised"}],
                "layout": {"title": "Energy vs ZCR", "xaxis": {"title": "Energy"}, "yaxis": {"title": "ZCR"}},
            }},
        ],
    }
    plots["groups"].append(s_group)

    return metrics, plots


def save_metrics_and_plots(metrics: dict[str, Any], plots: dict[str, Any], metrics_path: Path, plots_path: Path) -> None:
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    plots_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    plots_path.write_text(json.dumps(plots, ensure_ascii=False, indent=2), encoding="utf-8")

