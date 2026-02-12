from picamzero import Camera
from pathlib import Path
import time, math
import EXIF  # EXIF.py -> module name EXIF
from config import INTERVAL_S

from fotak import take_photo
from orbit import get_speed_approx

TOLERANCE = 1 # in km/s
RUNTIME = 10*60     # 10 Minutes, in second
INTERVAL = INTERVAL_S     # in seconds
def run_exif(photo_a: Path, photo_b: Path):
    """
    Try module-style first; if that doesn't work, fall back to script-style.
    """
    try:
        return (photo_a, photo_b)
    except Exception:
        # fallback: run as CLI script
        return 


def photo_and_process(cam, last_photo = None) -> tuple[str, float | None]:
    photo = take_photo('image', 'images/', cam)
    if last_photo is not None:
        speed = EXIF.run(last_photo, photo)[0]
    else:
        speed = None
    return (str(photo), speed)

 
def get_stan_dev(measurements: list[float]) -> float | None:
    if len(measurements) <= 0:
        return None
    average: float = sum(measurements)/len(measurements)
    total = 0
    for m in measurements:
        total += (m - average)**2

    return math.sqrt(1/len(measurements)*total)

def main() -> int:
    last_photo: str | None = None
    speeds: list[float] = []
    start_time = time.time()
    camera = Camera()

    while start_time + RUNTIME > time.time():
        timer_start = time.time()
        last_photo, speed = photo_and_process(camera, last_photo)
        print(last_photo, speed)
        if speed is not None: # and abs(speed - get_speed_approx()) < TOLERANCE:
            speeds.append(speed)
            with open("result.txt", "w") as f:
                f.write(f"{sum(speeds)/len(speeds):.03f} km/s")
                print(f"{sum(speeds)/len(speeds)} ± {get_stan_dev(speeds):.02f} km/s")
        
        while timer_start + INTERVAL < time.time():
            time.sleep(0.3)
        
            
            
if __name__ == "__main__":
    raise SystemExit(main())
