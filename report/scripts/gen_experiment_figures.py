"""Generate experiment figures for Chapter 9."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.signal import stft

ROOT = Path(__file__).resolve().parents[2]  # project root (DEMO)
FIGDIR = ROOT / "report" / "figures" / "experiments"
FIGDIR.mkdir(parents=True, exist_ok=True)


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float32), int(sr)


def spec_db(x: np.ndarray, sr: int, n_fft: int = 512, hop: int = 128):
    f, t, z = stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft - hop, nfft=n_fft, window="hann")
    return f, t, 20 * np.log10(np.abs(z) + 1e-8)


def save_quad(scene_key: str, title: str) -> None:
    clean, _ = load_mono(ROOT / "noisy_testset" / "clean_reference.wav")
    noisy, _ = load_mono(ROOT / "noisy_testset" / scene_key)
    stem = scene_key.replace(".wav", "")
    routed_p = ROOT / "analysis/denoise_selection/outputs/routed" / f"{stem}_routed.wav"
    refined_p = ROOT / "analysis/denoise_selection/outputs/distill_refined_runK" / f"{stem}_distill_refined.wav"
    if not refined_p.exists():
        refined_p = ROOT / "analysis/denoise_selection/outputs/distill_refined" / f"{stem}_distill_refined.wav"

    n = min(len(clean), len(noisy))
    if routed_p.exists():
        r, _ = load_mono(routed_p)
        n = min(n, len(r))
    else:
        r = noisy[:n]
    if refined_p.exists():
        rf, _ = load_mono(refined_p)
        n = min(n, len(rf))
    else:
        rf = r[:n]

    clean, noisy, r, rf = [a[:n] for a in (clean, noisy, r, rf)]
    panels = [
        ("Noisy mixture", noisy),
        ("Routed (override)", r),
        ("runK distill refined", rf),
        ("Clean reference", clean),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True, sharey=True)
    for ax, (name, sig) in zip(axes.ravel(), panels):
        f, t, S = spec_db(sig, 16000)
        ax.pcolormesh(t, f, S, shading="auto", cmap="magma", vmin=-80, vmax=0)
        ax.set_title(name, fontsize=10)
        ax.set_ylabel("Hz")
    axes[1, 0].set_xlabel("Time (s)")
    axes[1, 1].set_xlabel("Time (s)")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    out = FIGDIR / f"spectrogram_{stem}.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {out}")


def main() -> None:
    for sk, title in [
        ("scene02_white_snr5.wav", "Scene02: White noise 5 dB"),
        ("scene09_chirp_interference_snr8.wav", "Scene09: Chirp interference 8 dB"),
        ("scene12_babble_like_snr5.wav", "Scene12: Babble-like 5 dB"),
        ("scene15_reverb_plus_hiss_snr10.wav", "Scene15: Reverb + hiss 10 dB"),
    ]:
        save_quad(sk, title)

    distill = json.loads((ROOT / "analysis/denoise_selection/distill/distill_eval.json").read_text(encoding="utf-8"))
    best = json.loads((ROOT / "analysis/denoise_selection/eval/best_method_search.json").read_text(encoding="utf-8"))
    scenes = sorted(distill["scenes"].keys())

    imp = [distill["scenes"][s]["improve_vs_routed_rms"] for s in scenes]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(range(len(imp)), imp, color="#003366")
    ax.set_xticks(range(len(imp)))
    ax.set_xticklabels([s.replace("scene", "S").split("_")[0] for s in scenes], fontsize=8)
    ax.set_ylabel("RMS improvement vs routed")
    ax.set_title("Per-scene runK distill refinement gain (15 scenes)")
    ax.axhline(np.mean(imp), color="crimson", ls="--", label=f"mean={np.mean(imp):.4f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGDIR / "rms_improvement_bar.png", dpi=160)
    plt.close(fig)

    base, routed, refined = [], [], []
    for s in scenes:
        wav = s + ".wav"
        base.append(best[wav]["base_err_rms"])
        routed.append(distill["scenes"][s]["routed_err_rms"])
        refined.append(distill["scenes"][s]["distill_refined_err_rms"])

    fig, ax = plt.subplots(figsize=(11, 4))
    x = np.arange(len(scenes))
    w = 0.25
    ax.bar(x - w, base, w, label="base OM-LSA")
    ax.bar(x, routed, w, label="routed (override)")
    ax.bar(x + w, refined, w, label="+ runK distill refine")
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace("scene", "S").split("_")[0] for s in scenes], fontsize=8)
    ax.set_ylabel("RMS error vs clean")
    ax.set_title("Routing ablation: monolithic vs adaptive vs hybrid")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGDIR / "routing_ablation_rms.png", dpi=160)
    plt.close(fig)
    print("saved bar charts")


if __name__ == "__main__":
    main()
