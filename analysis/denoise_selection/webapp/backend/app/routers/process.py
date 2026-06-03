from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
import soundfile as sf

from app.core.errors import ApiError
from app.schemas.models import ProcessRequest, ProcessResponse
from app.services.denoise_runner import run_denoise, save_audio
from app.services.distill_refiner import refine_with_student
from app.services.file_store import FILE_STORE
from app.services.metrics_service import build_metrics_and_plots, save_metrics_and_plots
from app.services.task_store import TASK_STORE

router = APIRouter(prefix="/api", tags=["process"])


def _do_process(req: ProcessRequest) -> None:
    payload = TASK_STORE.patch(
        req.task_id,
        {"status": "processing", "progress": 0.1, "message": "running denoise", "settings": req.model_dump()},
    )
    in_wav = Path(payload["paths"]["original_wav"])
    den_wav, res_wav = FILE_STORE.output_wavs(req.task_id)
    metrics_json, plots_json = FILE_STORE.output_jsons(req.task_id)

    try:
        result = run_denoise(
            input_wav=in_wav,
            output_wav=den_wav,
            method=req.method,
            noisereduce_strength=req.noisereduce_strength,
            deepfilter_model_dir=req.deepfilter_model_dir,
        )
        TASK_STORE.patch(req.task_id, {"progress": 0.55, "message": "building metrics and plots"})

        if req.run_distill_refine:
            ckpt = Path("analysis/denoise_selection/distill/checkpoints/student_runD.pt")
            refine_with_student(
                input_wav=den_wav,
                noisy_wav=in_wav,
                output_wav=den_wav,
                checkpoint=ckpt.resolve(),
                residual_scale=1.0,
            )
            # refresh denoised from refined output
            y, _ = sf.read(den_wav)
            if getattr(y, "ndim", 1) > 1:
                y = y.mean(axis=1)
            result["denoised"] = y.astype("float32")
            result["residual"] = result["original"][: len(result["denoised"])] - result["denoised"][: len(result["original"])]

        save_audio(res_wav, result["residual"], result["sample_rate"])
        metrics, plots = build_metrics_and_plots(
            original=result["original"],
            denoised=result["denoised"],
            residual=result["residual"],
            sr=result["sample_rate"],
            route=result["route"],
            method=req.method,
            reason=result.get("reason", ""),
        )
        TASK_STORE.patch(
            req.task_id,
            {
                "progress": 0.9,
                "message": result.get("reason", "completed"),
                "route": result["route"],
                "reason": result.get("reason", ""),
            },
        )
        save_metrics_and_plots(metrics, plots, metrics_json, plots_json)

        TASK_STORE.patch(
            req.task_id,
            {
                "status": "completed",
                "progress": 1.0,
                "message": "completed",
                "paths": {
                    "denoised_wav": str(den_wav),
                    "residual_wav": str(res_wav),
                    "metrics_json": str(metrics_json),
                    "plots_json": str(plots_json),
                },
            },
        )
    except Exception as exc:
        TASK_STORE.patch(req.task_id, {"status": "failed", "progress": 1.0, "error": str(exc), "message": "failed"})


@router.post("/process", response_model=ProcessResponse)
def process_audio(req: ProcessRequest, background_tasks: BackgroundTasks) -> ProcessResponse:
    payload = TASK_STORE.get(req.task_id)
    if payload["status"] not in {"uploaded", "failed", "completed"}:
        raise ApiError("task_busy", f"Task in status {payload['status']}", 409)
    background_tasks.add_task(_do_process, req)
    TASK_STORE.patch(req.task_id, {"status": "queued", "progress": 0.0, "message": "queued"})
    return ProcessResponse(task_id=req.task_id, status="queued", message="Task queued")

