from skyfield.api import load

# Load timescale
ts = load.timescale()
t = ts.now()

# Load ISS TLE data
satellites = load.tle_file(
    'https://celestrak.org/NORAD/elements/stations.txt'
)

# Find ISS
iss = next(s for s in satellites if 'ISS' in s.name)

# Get position at current time
pos = iss.at(t)

# Get speed (km/s)
speed_km_s = pos.speed().km_per_s


print(f"ISS speed: {speed_km_s:.2f} km/s")
