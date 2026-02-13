from skyfield.api import load
from astro_pi_orbit import ISS
from datetime import datetime, timezone
from calc import EARTH_RADIUS

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

    dt = datetime.fromtimestamp(time_s, tz=timezone.utc)
    
    pos = iss.at(ts.from_datetime(dt))
    height = pos.distance().m-EARTH_RADIUS
    return height
