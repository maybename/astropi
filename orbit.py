from skyfield.api import load, wgs84
from skyfield.framelib import ICRS
from skyfield.positionlib import Geocentric
from astro_pi_orbit import ISS
import numpy as np
from datetime import timezone, datetime

EARTH_RADIUS = 6378000 # m

ts = load.timescale()

def get_time(time_s: float | None | datetime):
    if time_s is None:
        return ts.now()
    
    if isinstance(time_s, float):
        time_s = datetime.fromtimestamp(time_s)
    
    if time_s.tzinfo is None:
        time_s = time_s.replace(tzinfo=timezone.utc)   # EXIF timestamps usually have no tz; treat as UTC
    else:
        time_s = time_s.astimezone(timezone.utc)

    return ts.from_datetime(time_s)   # Skyfield Time object

def position_matrix_ecef(time_s: float | None | datetime = None):
    iss = ISS()
    geocentric = iss.at(get_time(time_s))
    x, y, z = geocentric.frame_xyz(ICRS).m  # meters in rotating frame
    return np.array([x, y, z])


def position_matrix(time_s: float | None | datetime = None):
    iss = ISS()
    geocentric = iss.at(get_time(time_s))
    x, y, z = geocentric.position.m  # meters in ICRS / inertial frame
    return np.array([x, y, z])

def get_speed_approx(time_s: float | None | datetime = None) -> float:
    iss = ISS()

    
    pos = iss.at(get_time(time_s))


    # Speed (km/s)
    speed = pos.speed().km_per_s

    print(f"ISS speed: {speed:.3f} km/s")
    return speed


def get_height() -> float:
    input("pozor")
    iss = ISS()
    return iss.coordinates().elevation.m

def get_height_at(time_s: float | None | datetime):
    iss = ISS()

    pos = iss.at(get_time(time_s))
    height = pos.distance().m-EARTH_RADIUS
    return height

def get_azimut(time_s: float | None | datetime = None):
    iss = ISS()
    guy = wgs84.latlon(0, 90)
    diff = iss - guy

    _, az, _ = diff.at(get_time(time_s)).altaz()
    return az.radians

def get_pos(time_s: float | None | datetime = None):
    iss = ISS()
    coordinates = iss.at(get_time(time_s)).subpoint()
    # print(coordinates)
    return coordinates.latitude.radians, coordinates.longitude.radians