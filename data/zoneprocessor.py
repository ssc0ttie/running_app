# zone_processor.py
# import pandas as pd
# import numpy as np
# from typing import Dict, List, Optional
# from data.athlete_metrics import get_pace_zones, get_athlete_max_hr, get_athlete_threshold_pace


# def calculate_hr_zones_from_streams(streams, athlete_name=None):
#     """
#     Calculate 5-row HR zone distribution from streams using athlete's max HR.

#     Args:
#         streams: Stream data from Strava
#         athlete_name: Name of athlete (used to fetch their max HR)
#     """
#     if "heartrate" not in streams:
#         return None

#     heartrates = streams["heartrate"].data
#     times = streams["time"].data

#     if len(heartrates) < 2:
#         return None

#     # Calculate time differences
#     time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]

#     # Get max HR from athlete metrics, fallback to activity max HR
#     athlete_max_hr = None
#     if athlete_name:
#         athlete_max_hr = get_athlete_max_hr(athlete_name)

#     if athlete_max_hr is not None and athlete_max_hr > 0:
#         max_hr = athlete_max_hr
#     else:
#         # Fall back to max HR from this activity
#         max_hr = max(heartrates) if heartrates else 180
#         print(f"Warning: Using activity max HR ({max_hr}) for {athlete_name}")

#     # Define 5 zones based on % of max HR
#     zone_definitions = [
#         {"zone": "Z1", "name": "Endurance", "min_pct": 0.50, "max_pct": 0.60},
#         {"zone": "Z2", "name": "Moderate", "min_pct": 0.60, "max_pct": 0.70},
#         {"zone": "Z3", "name": "Tempo", "min_pct": 0.70, "max_pct": 0.80},
#         {"zone": "Z4", "name": "Threshold", "min_pct": 0.80, "max_pct": 0.90},
#         {"zone": "Z5", "name": "Anaerobic", "min_pct": 0.90, "max_pct": 1.00},
#     ]

#     # Calculate actual HR ranges and initialize time
#     zones = []
#     for zd in zone_definitions:
#         zones.append(
#             {
#                 "zone": zd["zone"],
#                 "zone_name": zd["name"],
#                 "min_hr": int(zd["min_pct"] * max_hr),
#                 "max_hr": int(zd["max_pct"] * max_hr),
#                 "time_seconds": 0,
#             }
#         )

#     # Calculate time in each zone
#     total_time = 0
#     for i, hr in enumerate(heartrates[:-1]):
#         for zone in zones:
#             if zone["min_hr"] <= hr < zone["max_hr"]:
#                 zone["time_seconds"] += time_diffs[i]
#                 total_time += time_diffs[i]
#                 break

#     # Calculate percentages and format
#     for zone in zones:
#         zone["percentage"] = (
#             round((zone["time_seconds"] / total_time * 100), 1) if total_time > 0 else 0
#         )
#         zone["time_formatted"] = format_time(zone["time_seconds"])

#     return zones


# def calculate_pace_zones_from_streams(streams, athlete_name=None):
#     """
#     Calculate 5-row pace zone distribution from streams using athlete's threshold pace.

#     Args:
#         streams: Stream data from Strava
#         athlete_name: Name of athlete (used to fetch their threshold pace)
#     """
#     if "velocity_smooth" not in streams:
#         return None

#     velocities = streams["velocity_smooth"].data
#     times = streams["time"].data

#     if len(velocities) < 2:
#         return None

#     time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]

#     # Convert velocity to pace (min/km)
#     paces = []
#     for v in velocities[:-1]:
#         if v > 0:
#             pace_min_km = (1 / v) * (1000 / 60)  # m/s to min/km
#             paces.append(pace_min_km)
#         else:
#             paces.append(None)

#     # Get threshold pace from athlete metrics
#     threshold_pace = None
#     if athlete_name:
#         threshold_pace = get_athlete_threshold_pace(athlete_name)

#     # Convert threshold pace from mm:ss to decimal if needed
#     if threshold_pace and isinstance(threshold_pace, str):
#         # Handle format like "4:30"
#         parts = threshold_pace.split(":")
#         if len(parts) == 2:
#             threshold_pace = int(parts[0]) + int(parts[1]) / 60

#     if threshold_pace and threshold_pace > 0:
#         # Use Daniels' Running Formula based on threshold pace
#         t = threshold_pace
#         zone_definitions = [
#             {
#                 "zone": "Z1",
#                 "name": "Easy",
#                 "min_pace": t * 1.25,
#                 "max_pace": float("inf"),
#             },
#             {
#                 "zone": "Z2",
#                 "name": "Endurance",
#                 "min_pace": t * 1.15,
#                 "max_pace": t * 1.25,
#             },
#             {"zone": "Z3", "name": "Tempo", "min_pace": t * 1.05, "max_pace": t * 1.15},
#             {
#                 "zone": "Z4",
#                 "name": "Threshold",
#                 "min_pace": t * 0.95,
#                 "max_pace": t * 1.05,
#             },
#             {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": t * 0.95},
#         ]
#     else:
#         # Fall back to standard pace zones based on observed paces
#         # Calculate average pace from activity to determine level
#         valid_paces = [p for p in paces if p is not None]
#         if valid_paces:
#             avg_pace = sum(valid_paces) / len(valid_paces)

#             # Determine fitness level based on average pace
#             if avg_pace < 4.30:
#                 level = "advanced"
#             elif avg_pace < 5.30:
#                 level = "intermediate"
#             else:
#                 level = "beginner"
#         else:
#             level = "intermediate"

#         zone_definitions = get_standard_pace_zones(level)

#     # Initialize zones
#     zones = []
#     for zd in zone_definitions:
#         zones.append(
#             {
#                 "zone": zd["zone"],
#                 "zone_name": zd["name"],
#                 "min_pace": zd["min_pace"],
#                 "max_pace": zd["max_pace"] if zd["max_pace"] != float("inf") else None,
#                 "time_seconds": 0,
#             }
#         )

#     # Calculate time in each zone
#     total_time = 0
#     for i, pace in enumerate(paces):
#         if pace is None:
#             continue
#         for zone in zones:
#             min_pace = zone["min_pace"]
#             max_pace = zone["max_pace"] if zone["max_pace"] else float("inf")
#             if min_pace <= pace < max_pace:
#                 zone["time_seconds"] += time_diffs[i]
#                 total_time += time_diffs[i]
#                 break

#     # Calculate percentages and format pace values
#     for zone in zones:
#         zone["percentage"] = (
#             round((zone["time_seconds"] / total_time * 100), 1) if total_time > 0 else 0
#         )
#         zone["time_formatted"] = format_time(zone["time_seconds"])
#         if zone["min_pace"] is not None and zone["min_pace"] != float("inf"):
#             zone["min_pace"] = format_pace(zone["min_pace"])
#         if zone["max_pace"] is not None and zone["max_pace"] != float("inf"):
#             zone["max_pace"] = format_pace(zone["max_pace"])

#     return zones


# def get_standard_pace_zones(level="intermediate"):
#     """Fallback pace zones based on fitness level (min/km)"""
#     zones = {
#         "beginner": [
#             {"zone": "Z1", "name": "Easy", "min_pace": 7.30, "max_pace": float("inf")},
#             {"zone": "Z2", "name": "Endurance", "min_pace": 6.30, "max_pace": 7.30},
#             {"zone": "Z3", "name": "Tempo", "min_pace": 5.45, "max_pace": 6.30},
#             {"zone": "Z4", "name": "Threshold", "min_pace": 5.15, "max_pace": 5.45},
#             {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": 5.15},
#         ],
#         "intermediate": [
#             {"zone": "Z1", "name": "Easy", "min_pace": 6.00, "max_pace": float("inf")},
#             {"zone": "Z2", "name": "Endurance", "min_pace": 5.30, "max_pace": 6.00},
#             {"zone": "Z3", "name": "Tempo", "min_pace": 4.50, "max_pace": 5.30},
#             {"zone": "Z4", "name": "Threshold", "min_pace": 4.20, "max_pace": 4.50},
#             {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": 4.20},
#         ],
#         "advanced": [
#             {"zone": "Z1", "name": "Easy", "min_pace": 5.00, "max_pace": float("inf")},
#             {"zone": "Z2", "name": "Endurance", "min_pace": 4.30, "max_pace": 5.00},
#             {"zone": "Z3", "name": "Tempo", "min_pace": 4.00, "max_pace": 4.30},
#             {"zone": "Z4", "name": "Threshold", "min_pace": 3.45, "max_pace": 4.00},
#             {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": 3.45},
#         ],
#     }
#     return zones.get(level, zones["intermediate"])


# def format_time(seconds):
#     """Convert seconds to mm:ss format"""
#     minutes = int(seconds // 60)
#     secs = int(seconds % 60)
#     return f"{minutes}:{secs:02d}"


# def format_pace(min_per_km):
#     """Convert min/km to mm:ss format"""
#     if min_per_km is None or min_per_km == float("inf"):
#         return None
#     minutes = int(min_per_km)
#     seconds = int((min_per_km - minutes) * 60)
#     return f"{minutes}:{seconds:02d}"





############ UPDATED #################



# zone_processor.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from data.athlete_metrics import get_pace_zones, get_athlete_max_hr, get_athlete_threshold_pace


def calculate_hr_zones_from_streams(streams, athlete_name=None):
    """
    Calculate 5-row HR zone distribution from streams using athlete's max HR.

    Args:
        streams: Stream data from Strava
        athlete_name: Name of athlete (used to fetch their max HR)
    """
    if "heartrate" not in streams:
        return None

    heartrates = streams["heartrate"].data
    times = streams["time"].data

    if len(heartrates) < 2:
        return None

    # Calculate time differences
    time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]

    # Get max HR from athlete metrics, fallback to activity max HR
    athlete_max_hr = None
    if athlete_name:
        athlete_max_hr = get_athlete_max_hr(athlete_name)

    if athlete_max_hr is not None and athlete_max_hr > 0:
        max_hr = athlete_max_hr
    else:
        # Fall back to max HR from this activity
        max_hr = max(heartrates) if heartrates else 180
        print(f"Warning: Using activity max HR ({max_hr}) for {athlete_name}")

    # Define 5 zones based on % of max HR
    zone_definitions = [
        {"zone": "Z1", "name": "Endurance", "min_pct": 0.50, "max_pct": 0.60},
        {"zone": "Z2", "name": "Moderate", "min_pct": 0.60, "max_pct": 0.70},
        {"zone": "Z3", "name": "Tempo", "min_pct": 0.70, "max_pct": 0.80},
        {"zone": "Z4", "name": "Threshold", "min_pct": 0.80, "max_pct": 0.90},
        {"zone": "Z5", "name": "Anaerobic", "min_pct": 0.90, "max_pct": 1.00},
    ]

    # Calculate actual HR ranges and initialize time
    zones = []
    for zd in zone_definitions:
        zones.append(
            {
                "zone": zd["zone"],
                "zone_name": zd["name"],
                "min_hr": int(zd["min_pct"] * max_hr),
                "max_hr": int(zd["max_pct"] * max_hr),
                "time_seconds": 0,
            }
        )

    # Calculate time in each zone
    total_time = 0
    for i, hr in enumerate(heartrates[:-1]):
        for zone in zones:
            if zone["min_hr"] <= hr < zone["max_hr"]:
                zone["time_seconds"] += time_diffs[i]
                total_time += time_diffs[i]
                break

    # Calculate percentages and format
    for zone in zones:
        zone["percentage"] = (
            round((zone["time_seconds"] / total_time * 100), 1) if total_time > 0 else 0
        )
        zone["time_formatted"] = format_time(zone["time_seconds"])

    return zones


def calculate_pace_zones_from_streams(streams, athlete_name=None):
    """
    Calculate 5-row pace zone distribution from streams using athlete's explicit pace zones.
    Uses the 5-zone Pfitzinger-style zones from athlete_metrics.py.
    """
    if "velocity_smooth" not in streams:
        return None

    velocities = streams["velocity_smooth"].data
    times = streams["time"].data

    if len(velocities) < 2:
        return None

    time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]

    # Convert velocity to pace (min/km)
    paces = []
    for v in velocities[:-1]:
        if v > 0:
            pace_min_km = (1 / v) * (1000 / 60)  # m/s to min/km
            paces.append(pace_min_km)
        else:
            paces.append(None)

    # Get explicit pace zones from athlete_metrics.py
    zone_definitions = get_pace_zones(athlete_name)

    # If no explicit zones found, generate fallback zones
    if not zone_definitions:
        threshold_pace = get_athlete_threshold_pace(athlete_name)
        
        if threshold_pace and threshold_pace > 0:
            # Convert threshold pace to seconds if needed
            if isinstance(threshold_pace, str) and ":" in threshold_pace:
                parts = threshold_pace.split(":")
                threshold_pace = int(parts[0]) + int(parts[1]) / 60
            
            t = threshold_pace
            zone_definitions = [
                {"zone": "Z1", "name": "Recovery", "min_pace": t * 1.35, "max_pace": float("inf")},
                {"zone": "Z2", "name": "General Aerobic", "min_pace": t * 1.20, "max_pace": t * 1.35},
                {"zone": "Z3", "name": "Marathon Pace", "min_pace": t * 1.05, "max_pace": t * 1.20},
                {"zone": "Z4", "name": "Lactate Threshold", "min_pace": t * 0.95, "max_pace": t * 1.05},
                {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": t * 0.95},
            ]
        else:
            # Very generic fallback
            zone_definitions = [
                {"zone": "Z1", "name": "Recovery", "min_pace": 7.50, "max_pace": float("inf")},
                {"zone": "Z2", "name": "General Aerobic", "min_pace": 6.75, "max_pace": 7.50},
                {"zone": "Z3", "name": "Marathon Pace", "min_pace": 6.00, "max_pace": 6.75},
                {"zone": "Z4", "name": "Lactate Threshold", "min_pace": 5.25, "max_pace": 6.00},
                {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": 5.25},
            ]

    # Initialize zones with time_seconds
    zones = []
    for zd in zone_definitions:
        zones.append(
            {
                "zone": zd["zone"],
                "zone_name": zd["name"],
                "min_pace": zd["min_pace"],
                "max_pace": zd["max_pace"] if zd["max_pace"] != float("inf") else None,
                "time_seconds": 0,
            }
        )

    # Calculate time in each zone
    total_time = 0
    for i, pace in enumerate(paces):
        if pace is None:
            continue
        for zone in zones:
            min_pace = zone["min_pace"]
            max_pace = zone["max_pace"] if zone["max_pace"] else float("inf")
            if min_pace <= pace < max_pace:
                zone["time_seconds"] += time_diffs[i]
                total_time += time_diffs[i]
                break

    # Calculate percentages and format pace values
    for zone in zones:
        zone["percentage"] = (
            round((zone["time_seconds"] / total_time * 100), 1) if total_time > 0 else 0
        )
        zone["time_formatted"] = format_time(zone["time_seconds"])
        if zone["min_pace"] is not None and zone["min_pace"] != float("inf"):
            zone["min_pace"] = format_pace(zone["min_pace"])
        if zone["max_pace"] is not None and zone["max_pace"] != float("inf"):
            zone["max_pace"] = format_pace(zone["max_pace"])

    return zones


def format_time(seconds):
    """Convert seconds to mm:ss format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def format_pace(min_per_km):
    """Convert min/km to mm:ss format"""
    if min_per_km is None or min_per_km == float("inf"):
        return None
    minutes = int(min_per_km)
    seconds = int((min_per_km - minutes) * 60)
    return f"{minutes}:{seconds:02d}"