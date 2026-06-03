from pathlib import Path
import shutil
import subprocess
import sys


def resolve_cli() -> str:
    for name in ("deepFilter", "deep-filter"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError(
        "DeepFilterNet CLI not found. Install with `pip install deepfilternet` first."
    )


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    script_dir = Path(__file__).resolve().parent
    input_wav = project_root / "noisy_testset" / "scene02_white_snr5.wav"
    output_wav = script_dir / "scene02_deepfilternet_out.wav"

    cli = resolve_cli()
    cmd = [cli, str(input_wav), "-o", str(output_wav)]

    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd, check=False, text=True)
    if completed.returncode != 0:
        print("DeepFilterNet command failed.", file=sys.stderr)
        sys.exit(completed.returncode)

    print(f"Saved: {output_wav}")


if __name__ == "__main__":
    main()
