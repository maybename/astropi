from __future__ import annotations

from orbit import get_height
from calc import get_GSD

INTERVAL_S: float = 10.0

def get_gsdnapix() -> float:
    height_m = get_height()
    gsd_x_m, gsd_y_m = get_GSD(height_m)

    gsd_avg_m = (gsd_x_m + gsd_y_m) / 2.0
    return gsd_avg_m * 100.0 
