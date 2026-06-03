# Intelligent Audio Denoising Analysis Platform (Denoise Selection)

Course project: data-driven scene analysis, adaptive OM-LSA/MCRA denoising with scene-aware routing, optional TinyResidualRefiner distillation from DeepFilterNet3, and a FastAPI + React evaluation web app.

## Repository layout

| Path | Description |
|------|-------------|
| `noisy_testset/` | 15 benchmark noisy scenes + `clean_reference.wav` |
| `analysis/` | Scene analysis reports, metrics JSON, plots |
| `analysis/denoise_selection/` | Main pipeline, algorithms, router, distillation, webapp |
| `report/` | LaTeX project report (`report.pdf` after compile) |

## Quick start

```bash
# Routed denoise for all benchmark scenes
python analysis/denoise_selection/run_pipeline.py --all

# Train / infer student refiner (tag runD)
python analysis/denoise_selection/distill/train_student_distill.py --tag runD
python analysis/denoise_selection/distill/infer_student_refine.py \
  --checkpoint analysis/denoise_selection/distill/checkpoints/student_runD.pt

# Web backend (from webapp/backend, after pip install -r requirements.txt)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Web frontend (from webapp/frontend, after npm install)
npm run dev
```

See `analysis/denoise_selection/README.md` for detailed workflow notes.

## Report

Compile the PDF from `report/`:

```bash
cd report
pdflatex report.tex && biber report && pdflatex report.tex && pdflatex report.tex
```

## License

MIT License (see `LICENSE`).
