from pathlib import Path
import zipfile

import requests


def main() -> None:
    model_url = "https://github.com/Rikorose/DeepFilterNet/raw/main/models/DeepFilterNet3.zip"
    out_dir = Path(__file__).resolve().parent / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "DeepFilterNet3.zip"

    with requests.get(model_url, stream=True, timeout=120, verify=False) as r:
        r.raise_for_status()
        with zip_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)

    print(f"Downloaded: {zip_path}")
    print(f"Extracted to: {out_dir}")


if __name__ == "__main__":
    main()
