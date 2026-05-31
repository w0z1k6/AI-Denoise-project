from pathlib import Path

import noisereduce as nr
import soundfile as sf


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    input_wav = project_root / "noisy_testset" / "scene02_white_snr5.wav"
    output_wav = Path(__file__).resolve().parent / "scene02_noisereduce_out.wav"

    audio, sr = sf.read(input_wav)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    reduced = nr.reduce_noise(
        y=audio,
        sr=sr,
        stationary=False,
        prop_decrease=0.9,
    )
    sf.write(output_wav, reduced, sr)
    print(f"Saved: {output_wav}")


if __name__ == "__main__":
    main()
