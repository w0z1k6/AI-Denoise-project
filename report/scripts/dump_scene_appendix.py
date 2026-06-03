import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
ov = json.loads(
    (
        root / "analysis/denoise_selection/config/scene_method_overrides.json"
    ).read_text(encoding="utf-8")
)
details = root / "analysis/scene_details"
for p in sorted(details.glob("scene*_metrics.json")):
    m = json.loads(p.read_text(encoding="utf-8"))
    fn = p.name.replace("_metrics.json", ".wav")
    b = m.get("frequency", {}).get("band_snr_db", {})
    r = m.get("time_frequency", {}).get("local_snr", {}).get("ratio_lt0")
    br = m.get("baseline_residual", {})
    k = br.get("kurtosis") if br else None
    print(
        f"{fn}|{b.get('low')}|{b.get('mid')}|{b.get('high')}|{r}|{k}|{ov.get(fn)}"
    )
