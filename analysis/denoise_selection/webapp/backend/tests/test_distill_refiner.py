from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

from app.services.distill_refiner import (
    PROJECT_ROOT,
    refine_with_student,
    resolve_distill_checkpoint,
)

from train_student_distill import TinyResidualRefiner


def test_resolve_distill_checkpoint_runK() -> None:
    ckpt, scale = resolve_distill_checkpoint(PROJECT_ROOT)
    assert ckpt.name == "student_runK.pt"
    assert ckpt.exists()
    assert scale == 1.0


def test_runK_checkpoint_loads_new_architecture() -> None:
    ckpt_path, _ = resolve_distill_checkpoint(PROJECT_ROOT)
    ckpt = torch.load(ckpt_path, map_location="cpu")
    model = TinyResidualRefiner()
    model.load_state_dict(ckpt["model_state"])
    param_count = sum(p.numel() for p in model.parameters())
    assert param_count == 56129


def test_refine_with_student_produces_output() -> None:
    ckpt, scale = resolve_distill_checkpoint(PROJECT_ROOT)
    sr = 16000
    sec = 0.5
    t = np.linspace(0, sec, int(sr * sec), endpoint=False)
    routed = (0.15 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    noisy = routed + 0.05 * np.random.default_rng(0).standard_normal(len(routed)).astype(np.float32)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        routed_wav = tmp_path / "routed.wav"
        noisy_wav = tmp_path / "noisy.wav"
        out_wav = tmp_path / "refined.wav"
        sf.write(routed_wav, routed, sr)
        sf.write(noisy_wav, noisy, sr)

        ok = refine_with_student(
            input_wav=routed_wav,
            noisy_wav=noisy_wav,
            output_wav=out_wav,
            checkpoint=ckpt,
            residual_scale=scale,
        )
        assert ok is True
        assert out_wav.exists()
        y, out_sr = sf.read(out_wav)
        assert out_sr == sr
        assert len(y) == len(routed)
