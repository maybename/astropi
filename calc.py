import math
from orbit import get_height
# set it correctly
CAM_ANGLE_X = 56        /180*math.pi
CAM_ANGLE_Y = 60        /180*math.pi
CAM_RATIO = (4056, 3040)
EARTH_RADIUS = 6378 # km

Position = tuple[float, float]

def _calc_dist_from_mid(pixel: Position, height: float):
    # height: float      - height in m
    height = height / 1000
    p_x = pixel[0] - CAM_RATIO[0] if pixel[0] > CAM_RATIO[0] else CAM_RATIO[0] - pixel[0]
    p_y = pixel[1] - CAM_RATIO[1] if pixel[1] > CAM_RATIO[1] else CAM_RATIO[1] - pixel[1]
    
    beta_x = math.sin(math.asin(CAM_ANGLE_X/2)/CAM_RATIO[0]*2*p_x)
    beta_y = math.sin(math.asin(CAM_ANGLE_Y/2)/CAM_RATIO[1]*2*p_y)
    
    alpha_x = math.asin(math.sin(beta_x)*(1+height/EARTH_RADIUS))
    alpha_y = math.asin(math.sin(beta_y)*(1+height/EARTH_RADIUS))

    return alpha_x, alpha_y

def calc_dist(pos1: Position, pos2: Position, height: float):
    x1, y1 = _calc_dist_from_mid(pos1, height)
    x2, y2 = _calc_dist_from_mid(pos2, height)
    
    return math.sqrt(pow(x1-x2, 2) + pow(y1 - y2, 2)) * math.pi * EARTH_RADIUS

def calc_speed(point1: Position, point2: Position, time_diff: float) -> float:
    print(point1, point2,time_diff)
    height = get_height()
    s = calc_dist(point1, point2, height)
    speed = s/time_diff
    print(speed)
    return speed