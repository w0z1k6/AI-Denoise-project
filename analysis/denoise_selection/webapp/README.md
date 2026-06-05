# Denoise Web App (Frontend + Backend)

Separated web architecture for audio denoising analysis.

## Stack

- Backend: FastAPI (`webapp/backend`)
- Frontend: React + Vite + TypeScript (`webapp/frontend`)
- Processing: existing `analysis/denoise_selection` algorithms + optional distill refiner

## Project Tree

```text
webapp/
  backend/
    app/
      core/
      routers/
      schemas/
      services/
      main.py
    tests/
    requirements.txt
  frontend/
    src/
      app/
      components/
      pages/
      lib/
      types/
      i18n/
  docker/
    backend.Dockerfile
    frontend.Dockerfile
  data/
    uploads/
    processed/
    plots/
    tasks/
  docker-compose.yml
  .env.example
```

## Run Locally

### One-click (recommended)

**Windows** — double-click or in PowerShell:

```powershell
cd analysis/denoise_selection/webapp
.\start-webapp.ps1
# first time / after clone:
.\start-webapp.ps1 -InstallDeps
# stop services on ports 8000 & 5173:
.\start-webapp.ps1 -Stop
```

Or double-click `start-webapp.bat`.

**Linux / macOS / Git Bash:**

```bash
cd analysis/denoise_selection/webapp
chmod +x start-webapp.sh
./start-webapp.sh
./start-webapp.sh --install   # pip + npm install
./start-webapp.sh --stop
```

Opens two terminal windows (Windows) or background jobs (Unix). Frontend: `http://localhost:5173` · API docs: `http://127.0.0.1:8000/docs`

The script sets `DEEPFILTER_CONDA_ENV=dfnet311` from `.env` (copied from `.env.example` if missing) and runs the backend from the **repository root** so data/model/distill paths resolve correctly.

### Manual start

#### 1) Backend

```bash
# from repository root (DEMO/)
export DEEPFILTER_CONDA_ENV=dfnet311
export APP_DATA_DIR=analysis/denoise_selection/webapp/data
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir analysis/denoise_selection/webapp/backend
```

#### 2) Frontend

```bash
cd analysis/denoise_selection/webapp/frontend
npm install
npm run dev
```

## Docker

```bash
cd analysis/denoise_selection/webapp
copy .env.example .env
docker compose up --build
```

## API Summary

- `POST /api/upload`
- `POST /api/process`
- `GET /api/task/{task_id}`
- `GET /api/result/{task_id}/metrics`
- `GET /api/result/{task_id}/plots`
- `GET /api/result/{task_id}/audio/original`
- `GET /api/result/{task_id}/audio/denoised`
- `GET /api/result/{task_id}/audio/residual`
- `GET /api/history`
- `DELETE /api/history/{task_id}`
- `POST /api/abx/{task_id}/record`
- `GET /api/abx/{task_id}/stats`

## Example Requests

### Upload

```bash
curl -X POST http://127.0.0.1:8000/api/upload -F "file=@demo.wav"
```

Response:

```json
{
  "ok": true,
  "task_id": "8adf921ec9bc",
  "filename": "demo.wav",
  "status": "uploaded"
}
```

### Process

```bash
curl -X POST http://127.0.0.1:8000/api/process \
  -H "Content-Type: application/json" \
  -d "{\"task_id\":\"8adf921ec9bc\",\"method\":\"auto\",\"run_distill_refine\":true,\"noisereduce_strength\":0.8}"
```

### Poll Task

```bash
curl http://127.0.0.1:8000/api/task/8adf921ec9bc
```

## Test

Backend:

```bash
cd analysis/denoise_selection/webapp/backend
pytest
```

Frontend:

```bash
cd analysis/denoise_selection/webapp/frontend
npm test
```

## Notes

- If `.mp3` conversion fails, install `ffmpeg`.
- `deepfilter` mode runs **DeepFilterNet3** via CLI (`deepFilter`). Set `DEEPFILTER_CONDA_ENV=dfnet311` (or `DEEPFILTER_CLI`) so the backend uses the same environment as local tests. If CLI/model fails, the task returns **503** with an error message (no silent OM-LSA fallback).
- Large files are persisted in `webapp/data/`.

