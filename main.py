from picamzero import Camera
from pathlib import Path
import time, math
import EXIF  # EXIF.py -> module name EXIF
from config import INTERVAL_S
from exif import Image
from fotak import take_photo
from orbit import get_speed_approx
import traceback
from datetime import datetime
import calc

TOLERANCE = 1 # in km/s
RUNTIME = 10*60     # 10 Minutes, in second
INTERVAL = INTERVAL_S     # in seconds


def photo_and_process(cam, last_photo=None) -> tuple[str, float | None, list[float]]:
    photo = take_photo('image', 'images/', cam)
    if last_photo is not None:
        try:
            speed, speeds = EXIF.run(last_photo, photo)
        except Exception as e:
            print(f"EXIF failed for {last_photo} -> {photo}: {e}")
            traceback.print_exc()
            speed = None
            speeds = []
    else:
        speed = None
        speeds = []
    return (str(photo), speed, speeds)

def main() -> int:
    num_of_photos = 0
    last_photo: str | None = None
    speeds: list[float] = []
    start_time = time.time()
    camera = Camera()

    while start_time + RUNTIME > time.time() and num_of_photos < 42:
        timer_start = time.time()
        last_photo, speed, measured_all = photo_and_process(camera, last_photo)
        num_of_photos += 1
        print(last_photo, speed)
        if speed is not None: # and abs(speed - get_speed_approx()) < TOLERANCE:
            # speeds += measured_all
            speeds.append(speed)

            if len(speeds) > 1:
                avg_speed, std = calc.do_statistik(speeds)
            else:
                avg_speed = speed
                std = 0.0
            with open("result.txt", "w") as f:
                f.write(f"{avg_speed:.03f} km/s")
                print(f"{avg_speed} ± {std:.02f} km/s")
        
        while time.time() < timer_start + INTERVAL:
            time.sleep(0.3)

        
            
            
if __name__ == "__main__":
    raise SystemExit(main())
