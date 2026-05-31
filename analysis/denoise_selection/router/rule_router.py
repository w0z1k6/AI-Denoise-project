from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RouteDecision:
    route_name: str
    chain: list[str]
    reason: str


def _read_scene_metrics(scene_name: str, project_root: Path) -> dict[str, Any]:
    stem = scene_name.replace(".wav", "")
    p = project_root / "analysis" / "scene_details" / f"{stem}_metrics.json"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_overrides(project_root: Path) -> dict[str, str]:
    p = project_root / "analysis" / "denoise_selection" / "config" / "scene_method_overrides.json"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if isinstance(obj, dict):
        return {str(k): str(v) for k, v in obj.items()}
    return {}


def choose_route(scene_name: str, project_root: Path, force_method: str | None = None) -> RouteDecision:
    if force_method:
        return RouteDecision(
            route_name=f"force_{force_method}",
            chain=[force_method],
            reason="forced by CLI argument",
        )
    overrides = _read_overrides(project_root)
    if scene_name in overrides:
        method = overrides[scene_name]
        return RouteDecision(
            route_name=f"override_{method}",
            chain=[method],
            reason="scene override from config",
        )

    metrics = _read_scene_metrics(scene_name, project_root)
    low = float(metrics.get("frequency", {}).get("band_snr_db", {}).get("low", 0.0))
    mid = float(metrics.get("frequency", {}).get("band_snr_db", {}).get("mid", 0.0))
    high = float(metrics.get("frequency", {}).get("band_snr_db", {}).get("high", 0.0))
    ratio_lt0 = float(metrics.get("time_frequency", {}).get("local_snr", {}).get("ratio_lt0", 0.0))
    noise_type = str(metrics.get("noise_type", "")).lower()
    scene = scene_name.lower()

    if "reverb_plus_hiss" in scene or "reverb" in noise_type:
        return RouteDecision("wpe_chain", ["wpe_omlsa"], "reverb-like scene")
    if any(k in scene for k in ("hum50", "hum60", "office_fan")):
        return RouteDecision("hum_stationary_chain", ["adaptive_notch_bank", "nmf_denoise"], "tonal stationary hum/fan")
    if "chirp_interference" in scene:
        return RouteDecision("chirp_chain", ["subspace_denoise", "chirp_notch"], "chirp narrowband interference")
    if "highfreq_hiss" in scene or high < -5.0:
        return RouteDecision("hiss_chain", ["subspace_denoise", "base_omlsa_mcra"], "high-frequency hiss heavy")
    if ratio_lt0 > 0.75 and low < 8.0 and mid < 8.0:
        return RouteDecision("low_snr_chain", ["kalman_ar"], "very low local SNR")
    if any(k in scene for k in ("street_combo", "babble_like")):
        return RouteDecision("nonstationary_chain", ["kalman_ar", "base_omlsa_mcra"], "speech-like nonstationary noise")

    return RouteDecision("base_chain", ["base_omlsa_mcra"], "default fallback")
