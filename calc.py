import math
from orbit import get_height
# set it correctly
CAM_RESSOLUTION = (4056, 3040)
SENSOR_DIM = (0.006287, 0.004712)
EARTH_RADIUS = 6378000 # m
FOCUS_LENGTH = 0.005 # m
MIN_SPEED = 5000    # m/s

Position = tuple[float, float]

def get_GSD(height: float) -> tuple[float, float]:
    return height*SENSOR_DIM[0]/CAM_RESSOLUTION[0]/FOCUS_LENGTH, height*SENSOR_DIM[1]/CAM_RESSOLUTION[1]/FOCUS_LENGTH

from config import get_gsdnapix


def _calc_angle_from_mid(pixel: Position, height: float):
    # Convert pixels to ground distance using GSD
    GSD_x, GSD_y = get_GSD(height)
    ground_x = (pixel[0] - CAM_RESSOLUTION[0]/2) * GSD_x  # meters
    ground_y = (pixel[1] - CAM_RESSOLUTION[1]/2) * GSD_y  # meters
    
    # Convert ground distance to arc angle
    alpha_x = math.atan(ground_x / (EARTH_RADIUS + height))  # simpler for small angles
    alpha_y = math.atan(ground_y / (EARTH_RADIUS + height))
    
    return alpha_x, alpha_y

def calc_dist(pos1: Position, pos2: Position, height: float):
    x1, y1 = _calc_angle_from_mid(pos1, height)
    print(x1, y1)
    x2, y2 = _calc_angle_from_mid(pos2, height)
    print(x2, y2)
    return math.sqrt(pow(x1-x2, 2) + pow(y1 - y2, 2)) * EARTH_RADIUS

def minimum_pixel_diff(time_diff: float):
    height = get_height()
    gsd = get_GSD(height)
    dist = math.sqrt(MIN_SPEED)/2 * time_diff
    return (dist/gsd[0], dist/gsd[1])

def calc_speed(point1: Position, point2: Position, time_diff: float) -> float:
    print(point1, point2,time_diff)
    height = get_height()
    distance = calc_dist(point1, point2, height)
    print(distance)
    s = distance/1000
    speed = s/time_diff
    
    print(f"  calc_dist={distance:.2f} m, time_diff={time_diff} s")
    print(f"  → {s:.2f} km / {time_diff} s = {speed:.3f} km/s")
    
    
    return speed

if __name__ == "__main__":
    print(minimum_pixel_diff(60))
