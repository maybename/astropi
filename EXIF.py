# exif.py
from exif import Image
from calc import calc_dist
from datetime import datetime
import cv2
import math
import argparse
from pathlib import Path
from statistics import median
from typing import List, Tuple, Optional, Literal
import calc

Point = Tuple[float, float]
Pair = Tuple[Point, Point]


def get_time(image_path: str) -> datetime:
    with open(image_path, "rb") as image_file:
        img = Image(image_file)
        time_str = img.get("datetime_original")
        if not time_str:
            raise ValueError(f"No datetime_original EXIF tag found in {image_path}")
        return datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")


def get_time_difference(image_1: str, image_2: str) -> float:
    time_1 = get_time(image_1)
    time_2 = get_time(image_2)
    return abs((time_2 - time_1).total_seconds())


def convert_to_cv(image_1: str, image_2: str):
    image_1_cv = cv2.imread(image_1, 0)
    image_2_cv = cv2.imread(image_2, 0)
    if image_1_cv is None:
        raise FileNotFoundError(f"OpenCV could not read {image_1}")
    if image_2_cv is None:
        raise FileNotFoundError(f"OpenCV could not read {image_2}")
    return image_1_cv, image_2_cv


def calculate_features(image_1_cv, image_2_cv, feature_number: int):
    orb = cv2.ORB_create(nfeatures=feature_number)
    keypoints_1, descriptors_1 = orb.detectAndCompute(image_1_cv, None)
    keypoints_2, descriptors_2 = orb.detectAndCompute(image_2_cv, None)

    if descriptors_1 is None or descriptors_2 is None:
        raise ValueError("Could not compute descriptors (images too blurry/dark?).")

    return keypoints_1, keypoints_2, descriptors_1, descriptors_2


def calculate_matches(descriptors_1, descriptors_2):
    brute_force = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = brute_force.match(descriptors_1, descriptors_2)
    return sorted(matches, key=lambda x: x.distance)


def find_matching_coordinates(keypoints_1, keypoints_2, matches):
    coordinates_1 = []
    coordinates_2 = []
    for match in matches:
        (x1, y1) = keypoints_1[match.queryIdx].pt
        (x2, y2) = keypoints_2[match.trainIdx].pt
        coordinates_1.append((x1, y1))
        coordinates_2.append((x2, y2))
    return coordinates_1, coordinates_2


import math
from statistics import median
from typing import List, Tuple

Point = Tuple[float, float]
Pair = Tuple[Point, Point]


def calculate_median_distance(
    coordinates_1: List[Point],
    coordinates_2: List[Point],
    *,
    time_seconds: float = 35.0,
    gsd_cm_per_pixel: float = 12648.0,  # centimeters / pixel
    min_speed_kmh: float = 6.0,
    max_speed_kmh: float = 9.0,
) -> Optional[Tuple[float, Pair]]:
    """
    Returns:
      (median_ground_distance_m, ((x1, y1), (x2, y2)))
    using ONLY pairs whose implied speed is within [min_speed_kmh, max_speed_kmh].

    If no pairs remain after filtering, returns None (does NOT raise).
    """
    if not coordinates_1 or not coordinates_2:
        return None

    n = min(len(coordinates_1), len(coordinates_2))
    if n == 0:
        return None

    if time_seconds <= 0 or gsd_cm_per_pixel <= 0:
        return None

    gsd_m_per_px = gsd_cm_per_pixel / 100.0

    # Keep only valid-speed pairs
    valid: List[Tuple[float, Pair]] = []
    for (x1, y1), (x2, y2) in zip(coordinates_1[:n], coordinates_2[:n]):
        d_px = math.hypot(x1 - x2, y1 - y2)
        d_m = d_px * gsd_m_per_px

        speed_kmh = (d_m / 1000.0) / (time_seconds / 3600.0)

        if min_speed_kmh <= speed_kmh <= max_speed_kmh:
            valid.append((d_m, ((x1, y1), (x2, y2))))

    if not valid:
        return None

    # Sort by distance so we can pick the median-distance pair
    valid.sort(key=lambda t: t[0])

    distances = [d for d, _ in valid]
    med_dist = median(distances)

    # choose the pair corresponding to the median (lower median for even count)
    m = len(valid)
    med_idx = m // 2 if (m % 2 == 1) else (m // 2 - 1)

    return med_dist, valid[med_idx][1]

def calculate_speed_in_kmps(feature_distance_px: float, gsd_cm_per_px: float, time_difference_s: float) -> float:
    # distance in km: px * (cm/px) -> cm, then /100000 -> km
    distance_km = feature_distance_px * gsd_cm_per_px / 100000.0
    return distance_km / time_difference_s


def save_matches_image(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches, out_path: str):
    match_img = cv2.drawMatches(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches[:100], None)
    cv2.imwrite(out_path, match_img)


def run(image_1: str, image_2: str, gsd_cm_per_px: float = 12648.0, nfeatures: int = 1000, save_matches: str | None = None) -> float:
    time_difference = get_time_difference(image_1, image_2)
    if time_difference <= 0:
        raise ValueError("Time difference is zero or negative (EXIF timestamps wrong?).")

    image_1_cv, image_2_cv = convert_to_cv(image_1, image_2)
    keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(image_1_cv, image_2_cv, nfeatures)
    matches = calculate_matches(descriptors_1, descriptors_2)

    if len(matches) < 10:
        raise ValueError(f"Too few matches ({len(matches)}). Try higher nfeatures or better images.")

    if save_matches:
        save_matches_image(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches, save_matches)

    coordinates_1, coordinates_2 = find_matching_coordinates(keypoints_1, keypoints_2, matches)
    average_feature_distance, (pos1, pos2) = calculate_median_distance(coordinates_1, coordinates_2)

    print(calc.calc_speed(pos1, pos2, time_difference))

    return calculate_speed_in_kmps(average_feature_distance, gsd_cm_per_px, time_difference), 


def _cli():
    p = argparse.ArgumentParser()
    p.add_argument("image1")
    p.add_argument("image2")
    p.add_argument("--gsd", type=float, default=12648.0, help="Ground sample distance (cm per pixel)")
    p.add_argument("--nfeatures", type=int, default=1000)
    p.add_argument("--save-matches", default=None, help="Write match image to this path (no GUI needed)")
    args = p.parse_args()

    speed = run(args.image1, args.image2, gsd_cm_per_px=args.gsd, nfeatures=args.nfeatures, save_matches=args.save_matches)
    print(speed)


if __name__ == "__main__":
    _cli()
