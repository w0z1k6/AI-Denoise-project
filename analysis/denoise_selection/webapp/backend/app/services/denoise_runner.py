from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.signal import wiener

from app.core.errors import ApiError
from app.services.deepfilter_backend import (
    DeepFilterNetError,
    resolve_model_dir,
    run_deepfilter,
)

PROJECT_DENOISE_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_DENOISE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_DENOISE_ROOT))

from algorithms import (  # noqa: E402
    adaptive_notch_bank,
    base_omlsa_mcra,
    chirp_notch,
    kalman_ar,
    nmf_denoise,
    subspace_denoise,
    wpe_omlsa,
)
from algorithms.common import load_audio_mono, save_audio  # noqa: E402
from router.rule_router import choose_route  # noqa: E402


METHODS: dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
    "base_omlsa_mcra": base_omlsa_mcra,
    "wpe_omlsa": wpe_omlsa,
    "nmf_denoise": nmf_denoise,
    "kalman_ar": kalman_ar,
    "subspace_denoise": subspace_denoise,
    "adaptive_notch_bank": adaptive_notch_bank,
    "chirp_notch": chirp_notch,
}


def _run_noisereduce(x: np.ndarray, sr: int, strength: float) -> np.ndarray:
    try:
        import noisereduce as nr
    except Exception:
        return base_omlsa_mcra(x, sr)
    return nr.reduce_noise(y=x, sr=sr, prop_decrease=float(np.clip(strength, 0.1, 1.0))).astype(np.float32)


def run_denoise(
    input_wav: Path,
    output_wav: Path,
    method: str,
    noisereduce_strength: float,
    deepfilter_model_dir: str | None = None,
) -> dict:
    x, sr = load_audio_mono(input_wav)

    if method == "noisereduce":
        y = _run_noisereduce(x, sr, noisereduce_strength)
        route = ["noisereduce"]
        reason = "explicit noisereduce"
    elif method == "wiener":
        y = wiener(x, mysize=15).astype(np.float32)
        route = ["wiener"]
        reason = "explicit scipy wiener"
    elif method == "deepfilter":
        try:
            model_dir = resolve_model_dir(PROJECT_DENOISE_ROOT, deepfilter_model_dir)
            engine = run_deepfilter(input_wav, output_wav, model_dir)
            y, _ = load_audio_mono(output_wav)
            route = ["deepfilter"]
            reason = f"DeepFilterNet3 via {engine} ({model_dir.name})"
        except DeepFilterNetError as exc:
            raise ApiError("deepfilter_failed", str(exc), 503) from exc
    elif method == "omlsa":
        y = base_omlsa_mcra(x, sr)
        route = ["base_omlsa_mcra"]
        reason = "explicit omlsa-like method"
    elif method == "auto":
        decision = choose_route(input_wav.name, PROJECT_DENOISE_ROOT.parent.parent, force_method=None)
        y = x
        for m in decision.chain:
            fn = METHODS.get(m)
            if fn is None:
                raise ApiError("unknown_method", f"Unknown routed method: {m}", 500)
            y = fn(y, sr)
        route = decision.chain
        reason = decision.reason
    elif method in METHODS:
        y = METHODS[method](x, sr)
        route = [method]
        reason = "explicit algorithm method"
    else:
        raise ApiError("bad_method", f"Unsupported method: {method}", 400)

    if method != "deepfilter":
        save_audio(output_wav, y, sr)
    residual = (x[: len(y)] - y[: len(x)]).astype(np.float32)
    return {
        "sample_rate": sr,
        "route": route,
        "reason": reason,
        "residual": residual,
        "original": x,
        "denoised": y,
    }

