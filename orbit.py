from astro_pi_orbit import ISS
from skyfield.api import load

def get_speed_approx() -> float:
    ts = load.timescale()
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

