# Denoise Selection Project

This folder is organized for course-project delivery and reproducibility.

## Main Workflow

- `run_pipeline.py`: main pure-math routed denoise entrypoint.
- `distill/`: lightweight teacher-student distillation pipeline.
- `outputs/`: generated routed and distill-refined outputs.
- `eval/`: batch evaluation scripts and reports.

## Directory Structure

- `algorithms/`: reusable math denoise modules.
- `router/`: scene-aware routing logic.
- `config/`: pipeline configs and scene overrides.
- `tests/`: smoke tests.
- `distill/`: distillation scripts, pair index, checkpoints, AB reports.
- `outputs/`
  - `routed/`: outputs from rule-based math pipeline.
  - `distill_refined/`: student-refined outputs.
  - `logs/`: routing logs.
- `experiments/legacy/`: one-off prototype scripts kept for reference.
- `artifacts/legacy_trials/`: archived old trial wav outputs.
- `artifacts/legacy_logs/`: archived old logs and non-selected run logs.
- `docs/`: selection notes and tutorial docs.

## Suggested Commands

- Run routed pipeline for all scenes:
  - `conda run -n dfnet311 python analysis/denoise_selection/run_pipeline.py --all`
- Train student:
  - `conda run -n dfnet311 python analysis/denoise_selection/distill/train_student_distill.py --tag runD --lr-scale 0.7`
- Refine and evaluate:
  - `conda run -n dfnet311 python analysis/denoise_selection/distill/infer_student_refine.py --checkpoint analysis/denoise_selection/distill/checkpoints/student_runD.pt --residual-scale 1.0`
  - `conda run -n dfnet311 python analysis/denoise_selection/distill/eval_distill_ab.py`
