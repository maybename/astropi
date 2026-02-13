from skyfield.api import load
from astro_pi_orbit import ISS
from datetime import datetime, timezone
from datetime import timezone
EARTH_RADIUS = 6378000 # m

ts = load.timescale()

def get_speed_approx() -> float:
    t = ts.now()

    iss = ISS()
    pos = iss.at(t)

    # Speed (km/s)
    speed = pos.speed().km_per_s

    print(f"ISS speed: {speed:.3f} km/s")
    return speed

def get_height() -> float:
    iss = ISS()
    return iss.coordinates().elevation.m

def get_height_at(time_s: float):
    iss = ISS()
    ts = load.timescale()

# assuming `time` is a Python datetime
    if time_s.tzinfo is None:
        time_s = time_s.replace(tzinfo=timezone.utc)   # EXIF timestamps usually have no tz; treat as UTC
    else:
        time_s = time_s.astimezone(timezone.utc)
    time_sf = ts.from_datetime(time_s)   # Skyfield Time object
    pos = iss.at(time_sf)
    height = pos.distance().m-EARTH_RADIUS
    return height
