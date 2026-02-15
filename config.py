from __future__ import annotations
import time

from orbit import get_height_at
from calc import get_GSD

INTERVAL_S: float = (600 - 5)/(42 - 1)    #42 photos in 10 minutes with five sec to process the last photo

def get_gsdnapix(time_s: float = time.time()) -> float:
    height_m = get_height_at(time_s)
    gsd_x_m, gsd_y_m = get_GSD(height_m)

    gsd_avg_m = (gsd_x_m + gsd_y_m) / 2.0
    return gsd_avg_m * 100.0 
