# main.py
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

from fotak import take_three_photos


def run_exif_as_module(photo_a: Path, photo_b: Path):
    """
    If EXIF.py exposes a function, use it here.
    Example: EXIF.calculate(photo_a, photo_b)
    """
    import EXIF  # EXIF.py -> module name EXIF

    # ---- ADAPT THIS PART ----
    # I don't know your EXIF.py API, so pick ONE pattern:

    # Pattern A: function named "calculate"
    if hasattr(EXIF, "calculate"):
        return EXIF.calculate(str(photo_a), str(photo_b))

    # Pattern B: function named "main" that takes args
    if hasattr(EXIF, "main"):
        return EXIF.main(str(photo_a), str(photo_b))

    raise AttributeError(
        "EXIF.py imported, but no known callable found. "
        "Add a function like calculate(file1, file2) or adjust main.py to match EXIF.py."
    )


def run_exif_as_script(photo_a: Path, photo_b: Path):
    """
    If EXIF.py is meant to be run as a script: python3 EXIF.py a.jpg b.jpg
    Returns stdout text.
    """
    cmd = [sys.executable, "EXIF.py", str(photo_a), str(photo_b)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"EXIF.py failed (code {result.returncode}).\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout.strip()


def run_exif(photo_a: Path, photo_b: Path):
    """
    Try module-style first; if that doesn't work, fall back to script-style.
    """
    try:
        return run_exif_as_module(photo_a, photo_b)
    except Exception:
        # fallback: run as CLI script
        return run_exif_as_script(photo_a, photo_b)


def main() -> int:
    photos = take_three_photos(prefix="atlas_photo", directory=".", interval_s=35.0)

    # Primary pair: 35s apart
    pairs = [(photos[0], photos[1]), (photos[1], photos[2])]

    last_error = None
    for a, b in pairs:
        try:
            output = run_exif(a, b)
            print(f"EXIF result using: {a.name} and {b.name}")
            print(output)

            # Optional: save result to a file
            Path("result.txt").write_text(f"{a.name} {b.name}\n{output}\n", encoding="utf-8")
            return 0
        except Exception as e:
            last_error = e
            print(f"Failed EXIF on pair {a.name}, {b.name}: {e}", file=sys.stderr)

    print(f"All EXIF attempts failed. Last error: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
