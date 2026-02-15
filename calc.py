import math
from orbit import get_height_at, get_azimut, get_pos, get_height  # , get_speed_approx
import numpy as np
# set it correctly
CAM_RESOLUTION= (4056, 3040)
SENSOR_DIM = (0.006287, 0.004712)
EARTH_RADIUS = 6371008.8 # m
FOCUS_LENGTH = 0.005 # m
MIN_SPEED = 6000    # m/s
EARTH_HEIGHT = 6356752
EARTH_WIDTH = 6378137
EARTH_ROTATION_SPEED = 7.2921150e-5  # rad/s

Position = tuple[float, float]



def get_GSD(height: float) -> tuple[float, float]:
    return height*SENSOR_DIM[0]/CAM_RESOLUTION[0]/FOCUS_LENGTH, height*SENSOR_DIM[1]/CAM_RESOLUTION[1]/FOCUS_LENGTH


def minimum_pixel_diff(time_diff: float, height: float | None = None):
    if height is None:
        height = get_height()
    gsd = get_GSD(height)
    dist = math.sqrt(MIN_SPEED)/2 * time_diff
    return (dist/gsd[0], dist/gsd[1])
# 
# 
# def rotate_azimuth(length_to_rotate, beta):
#     """
#     Rotate point MX around center M by beta_deg clockwise
#     """
#     M = [0,0]
#     MX = [0, length_to_rotate]
#     # clockwise rotation matrix
#     R = np.array([[np.cos(beta),  np.sin(beta)],
#                   [-np.sin(beta), np.cos(beta)]])
#     
#     v = np.array(MX) - np.array(M)
#     v_rot = R @ v
#     return np.array(M) + v_rot
# 
# 
# 
def get_radius(lon: float, width: float, height: float):
    W = width
    H = height
    t = lon

    return (W*H) / (2*math.sqrt((H*math.cos(t))**2 + (W*math.sin(t))**2))

# def get_speed(pos1, pos2, time1, df):
#     lat, lon = get_pos(time1)
#     az = get_azimut(time1)
#     height = get_height_at(time1)
#     radius = get_radius(lon, EARTH_WIDTH, EARTH_HEIGHT)
# 
#     dx = pos1[0] - pos2[0]
#     dy = pos1[1] - pos2[1]
# 
#     sensor_dx = dx * SENSOR_DIM[0] / CAM_RESSOLUTION[0]
#     sensor_dy = dy * SENSOR_DIM[1] / CAM_RESSOLUTION[1]
# 
#     angle_x = np.arctan(sensor_dx / FOCUS_LENGTH)
#     angle_y = np.arctan(sensor_dy / FOCUS_LENGTH)
#     angular_disp = np.sqrt(angle_x**2 + angle_y**2)
#     ang_speed = angular_disp/df
#     
#     ang_speed_vect = rotate_azimuth(ang_speed, az)
#     earth_speed_vect = np.array([0.0, EARTH_ROTATION_SPEED*np.cos(lat)])
# 
#     speed_vect = ang_speed_vect + earth_speed_vect
#     total_ang_speed = np.linalg.norm(speed_vect)
#     speed = total_ang_speed*(radius+height)
#     # print(speed, 'm/s')
#     return speed/1000
# 



def do_statistik(data: list[float]):
    mean = np.mean(data)
    std = np.std(data)
    filtered: list[float] = [d for d in data if (d > mean - 2*std) & (d < mean + 2*std)]
    mean_filtered: float = np.mean(filtered)
    return mean_filtered, std

def rotate_azimuth(length, beta_rad):
    """
    Rotate a 2D vector [0, length] clockwise by beta_rad.
    X = North, Y = East
    """
    R = np.array([[np.cos(beta_rad), np.sin(beta_rad)],
                  [-np.sin(beta_rad), np.cos(beta_rad)]])
    v = np.array([0.0, length])
    return R @ v

def get_speed(pos1, pos2, time1, df, lat = None, lon = None, azimuth = None, height = None):
    """
    Compute total linear speed in km/s from two image positions.

    pos1, pos2 : pixel positions (x, y)
    time1      : timestamp of first image (s)
    df         : time difference between images (s)
    lat, lon   : radians
    azimuth    : radians
    height     : meters above Earth
    """
    if lat is None or lon is None:
        lat, lon = get_pos(time1)
    
    if azimuth is None:
        azimuth = get_azimut(time1)
    
    if height is None:
        height = get_height_at(time1)

    radius = get_radius(lon, EARTH_WIDTH, EARTH_HEIGHT)
    orbital_radius = radius + height  # meters

    # 1. Pixel displacement to sensor displacement
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    # print("dx, dy", dx, dy)
    sensor_dx = dx * SENSOR_DIM[0] / CAM_RESOLUTION[0]
    sensor_dy = dy * SENSOR_DIM[1] / CAM_RESOLUTION[1]

    # 2. Angular displacement in radians
    angle_x = np.arctan2(sensor_dx, FOCUS_LENGTH)
    angle_y = np.arctan2(sensor_dy, FOCUS_LENGTH)
    angular_disp_cam = np.sqrt(angle_x**2 + angle_y**2)
    ang_disp_earth = np.arcsin(np.sin(angular_disp_cam)*orbital_radius/radius) - angular_disp_cam
    ang_speed = ang_disp_earth / df  # rad/s
    # print('ang_speed', ang_speed)
    # 3. Rotate angular speed vector by azimuth into North/East frame
    ang_speed_vect = rotate_azimuth(ang_speed, azimuth)  # X = N, Y = E
    # print('speed vector', ang_speed_vect)
    # 4. Earth rotation contribution (rad/s) in East direction
    earth_ang_speed = EARTH_ROTATION_SPEED * np.cos(lat)
    earth_speed_vect = np.array([0.0, earth_ang_speed])  # X=N, Y=E
    # print('earth speed vector', earth_speed_vect)
    # 5. Total angular velocity vector
    total_ang_vect = ang_speed_vect + earth_speed_vect

    # 6. Convert to linear speed (v = omega * r)
    total_speed_m_s = np.linalg.norm(total_ang_vect) * orbital_radius
    # print('total speed', total_speed_m_s)
    # print('actuall speed', get_speed_approx(time1))
    return total_speed_m_s / 1000  # km/s
