from skyfield.api import load
from astro_pi_orbit import ISS

# Load timescale
ts = load.timescale()

def get_height():
    iss = ISS()
    pos = iss.coordinates()
    help(pos)
    return pos.altitude()
    
def get_speed_aprox():
    iss = ISS()
    # Get position at current time
    t = ts.now()
    pos = iss.at(t)

    # Get speed (km/s)
    speed_km_s = pos.speed().km_per_s
    return speed_km_s

get_height()
