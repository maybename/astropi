# fotak.py
from __future__ import annotations

import time
from pathlib import Path
from typing import List

try:
    # This is what you said you're using
    from picamzero import Camera
except ImportError as e:
    raise ImportError(
        "Could not import camerazero. Make sure it's installed and you're running on the target device."
    ) from e


def _next_index(prefix: str, directory: Path) -> int:
    """
    Finds the next available numeric index for files like prefix_012.jpg.
    """
    existing = sorted(directory.glob(f"{prefix}_*.jpg"))
    max_idx = 0
    for p in existing:
        # Expecting something like atlas_photo_012.jpg
        stem = p.stem  # atlas_photo_012
        try:
            idx_str = stem.split("_")[-1]
            idx = int(idx_str)
            max_idx = max(max_idx, idx)
        except Exception:
            # Ignore weirdly named files
            pass
    return max_idx + 1


def take_three_photos(
    prefix: str = "atlas_photo",
    directory: str | Path = ".",
    interval_s: float = 35.0,
) -> List[Path]:
    """
    Takes 3 photos using camerazero at t=0, t=interval_s, t=2*interval_s.

    Returns: list of Path objects for the saved images in capture order.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    start_idx = _next_index(prefix, directory)

    camera = Camera()

    # Optional: set camera options if your camerazero supports them.
    # These names vary by implementation; comment out if they error.
    # camera.resolution = (1920, 1080)

    # Give camera a moment to settle
    time.sleep(2.0)

    paths: List[Path] = []
    t0 = time.monotonic()

    for i in range(3):
        # Schedule so spacing is as close as possible to 35s between *shots*
        target_time = t0 + i * interval_s
        now = time.monotonic()
        if now < target_time:
            time.sleep(target_time - now)

        filename = f"{prefix}_{start_idx + i:03d}.jpg"
        path = directory / filename

        # camerazero usually provides .take_photo("file.jpg") or similar
        camera.take_photo(str(path))

        paths.append(path)

    return paths

def take_photo(
    prefix: str = "atlas_photo",
    directory: str | Path = ".",
    camera = None
) -> Path:
    """
    Takes 3 photos using camerazero at t=0, t=interval_s, t=2*interval_s.

    Returns: list of Path objects for the saved images in capture order.
    """

    if camera is None:
        camera = Camera()

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    start_idx = _next_index(prefix, directory)

    filename = f"{prefix}_{start_idx + time.time():.03f}.jpg"
    path = directory / filename

    # camerazero usually provides .take_photo("file.jpg") or similar
    camera.take_photo(str(path))

    return path

if __name__ == "__main__":
    photos = take_three_photos(prefix="atlas_photo", directory=".", interval_s=35.0)
    print("Captured:")
    for p in photos:
        print(" -", p)
