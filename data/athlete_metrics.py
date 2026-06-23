# athlete_metrics.py
import pandas as pd
import streamlit as st

# # Hardcoded athlete metrics (you can move to Google Sheets later)
# ATHLETE_METRICS = {
#     "Scott": {
#         "max_hr": 194,
#         "threshold_hr": 165,
#         "threshold_pace": 5.00,  # 5:00 min pace
#         "pace_5k": 4.00,
#         "pace_10k": 4.90,
#     },
#     "Chona": {
#         "max_hr": 195,
#         "threshold_hr": 171,
#         "threshold_pace": 6.5,  # 6:30 min pace
#         "pace_5k": 6.15,
#         "pace_10k": 6.8,
#     },
#         "Aiza": {
#         "max_hr": 192,
#         "threshold_hr": 165,
#         "threshold_pace": 6.25,  # 6:15 min pace
#         "pace_5k": 5.00,
#         "pace_10k": 5.75,
#     },
# }


# def get_athlete_metrics(athlete_name):
#     """Get metrics for a specific athlete"""
#     return ATHLETE_METRICS.get(athlete_name, {})


# def get_hr_zones(athlete_name):
#     """Calculate HR zones for an athlete"""
#     metrics = get_athlete_metrics(athlete_name)
#     max_hr = metrics.get("max_hr")

#     if not max_hr:
#         return None

#     zones = [
#         {
#             "zone": "Z1",
#             "name": "Endurance",
#             "min": int(max_hr * 0.50),
#             "max": int(max_hr * 0.60),
#         },
#         {
#             "zone": "Z2",
#             "name": "Moderate",
#             "min": int(max_hr * 0.60),
#             "max": int(max_hr * 0.70),
#         },
#         {
#             "zone": "Z3",
#             "name": "Tempo",
#             "min": int(max_hr * 0.70),
#             "max": int(max_hr * 0.80),
#         },
#         {
#             "zone": "Z4",
#             "name": "Threshold",
#             "min": int(max_hr * 0.80),
#             "max": int(max_hr * 0.90),
#         },
#         {"zone": "Z5", "name": "Anaerobic", "min": int(max_hr * 0.90), "max": max_hr},
#     ]
#     return zones


# def get_pace_zones(athlete_name):
#     """Calculate pace zones for an athlete based on threshold pace"""
#     metrics = get_athlete_metrics(athlete_name)
#     threshold_pace = metrics.get("threshold_pace")

#     if not threshold_pace:
#         return None

#     # Threshold pace in seconds per km (for easier calculation)
#     threshold_seconds = int(threshold_pace * 60)

#     zones = [
#         {
#             "zone": "Z1",
#             "name": "Easy",
#             "min": format_pace(threshold_seconds * 1.25),
#             "max": "∞",
#         },
#         {
#             "zone": "Z2",
#             "name": "Endurance",
#             "min": format_pace(threshold_seconds * 1.15),
#             "max": format_pace(threshold_seconds * 1.25),
#         },
#         {
#             "zone": "Z3",
#             "name": "Tempo",
#             "min": format_pace(threshold_seconds * 1.05),
#             "max": format_pace(threshold_seconds * 1.15),
#         },
#         {
#             "zone": "Z4",
#             "name": "Threshold",
#             "min": format_pace(threshold_seconds * 0.95),
#             "max": format_pace(threshold_seconds * 1.05),
#         },
#         {
#             "zone": "Z5",
#             "name": "VO2 Max",
#             "min": "0:00",
#             "max": format_pace(threshold_seconds * 0.95),
#         },
#     ]
#     return zones


# def format_pace(seconds):
#     """Convert seconds to mm:ss format"""
#     minutes = int(seconds // 60)
#     secs = int(seconds % 60)
#     return f"{minutes}:{secs:02d}"


# # For backward compatibility with existing zone processor
# def get_athlete_max_hr(athlete_name):
#     metrics = get_athlete_metrics(athlete_name)
#     return metrics.get("max_hr")


# def get_athlete_threshold_pace(athlete_name):
#     metrics = get_athlete_metrics(athlete_name)
#     return metrics.get("threshold_pace")






ATHLETE_METRICS = {
    "Scott": {
        "max_hr": 194,
        "threshold_hr": 165,
        "threshold_pace": 5.00,  # 5:00 min/km
        "pace_5k": 4.00,
        "pace_10k": 4.90,
        # 5-Zone Pfitzinger-style pace zones (min/km decimal)
        "pace_zones": [
            {"zone": "Z1", "name": "Recovery", "min": 6.75, "max": float("inf")},      # >6:45
            {"zone": "Z2", "name": "General Aerobic / Endurance", "min": 6.25, "max": 6.75},  # 6:15 - 6:45
            {"zone": "Z3", "name": "Marathon Pace", "min": 5.75, "max": 6.25},          # 5:45 - 6:15
            {"zone": "Z4", "name": "Lactate Threshold", "min": 5.25, "max": 5.75},      # 5:15 - 5:45
            {"zone": "Z5", "name": "VO2 Max", "min": 0, "max": 5.25},                  # <5:15
        ],
    },
    "Chona": {
        "max_hr": 175,
        "threshold_hr": 155,
        "threshold_pace": 7.00,  # 7:00 min/km
        "pace_5k": None,
        "pace_10k": None,
        # 5-Zone Pfitzinger-style pace zones (min/km decimal)
        "pace_zones": [
            {"zone": "Z1", "name": "Recovery", "min": 8.25, "max": float("inf")},      # >8:15
            {"zone": "Z2", "name": "General Aerobic / Endurance", "min": 7.75, "max": 8.25},  # 7:45 - 8:15
            {"zone": "Z3", "name": "Marathon Pace", "min": 7.50, "max": 7.75},          # 7:30 - 7:45
            {"zone": "Z4", "name": "Lactate Threshold", "min": 7.00, "max": 7.50},      # 7:00 - 7:30
            {"zone": "Z5", "name": "VO2 Max", "min": 0, "max": 7.00},                  # <7:00
        ],
    },
    "Aiza": {
        "max_hr": 180,
        "threshold_hr": 160,
        "threshold_pace": 5.45,  # 5:45 min/km
        "pace_5k": None,
        "pace_10k": None,
        # 5-Zone Pfitzinger-style pace zones (min/km decimal)
        "pace_zones": [
            {"zone": "Z1", "name": "Recovery", "min": 7.50, "max": float("inf")},      # >7:30
            {"zone": "Z2", "name": "General Aerobic / Endurance", "min": 7.00, "max": 7.50},  # 7:00 - 7:30
            {"zone": "Z3", "name": "Marathon Pace", "min": 6.50, "max": 7.00},          # 6:30 - 7:00
            {"zone": "Z4", "name": "Lactate Threshold", "min": 6.00, "max": 6.50},      # 6:00 - 6:30
            {"zone": "Z5", "name": "VO2 Max", "min": 0, "max": 6.00},                  # <6:00
        ],
    },
    # Default fallback for other athletes
    "Default": {
        "max_hr": 180,
        "threshold_hr": 160,
        "threshold_pace": 6.00,
        "pace_zones": [
            {"zone": "Z1", "name": "Recovery", "min": 7.50, "max": float("inf")},
            {"zone": "Z2", "name": "General Aerobic / Endurance", "min": 6.75, "max": 7.50},
            {"zone": "Z3", "name": "Marathon Pace", "min": 6.00, "max": 6.75},
            {"zone": "Z4", "name": "Lactate Threshold", "min": 5.25, "max": 6.00},
            {"zone": "Z5", "name": "VO2 Max", "min": 0, "max": 5.25},
        ],
    },
}


def get_athlete_metrics(athlete_name=None):
    """Get athlete metrics - works without Streamlit"""
    if athlete_name and athlete_name in ATHLETE_METRICS:
        return ATHLETE_METRICS[athlete_name]
    return ATHLETE_METRICS.get("Default", {})


def get_athlete_max_hr(athlete_name=None):
    """Get athlete's max HR"""
    metrics = get_athlete_metrics(athlete_name)
    return metrics.get("max_hr")


def get_athlete_threshold_pace(athlete_name=None):
    """Get athlete's threshold pace"""
    metrics = get_athlete_metrics(athlete_name)
    pace = metrics.get("threshold_pace")
    if isinstance(pace, str) and ":" in pace:
        parts = pace.split(":")
        return int(parts[0]) + int(parts[1]) / 60
    return pace


def get_pace_zones(athlete_name=None):
    """Get athlete's explicit pace zones (5-zone Pfitzinger style)"""
    metrics = get_athlete_metrics(athlete_name)
    
    if "pace_zones" in metrics:
        zones = []
        for zone in metrics["pace_zones"]:
            zones.append({
                "zone": zone["zone"],
                "name": zone["name"],
                "min_pace": zone["min"],
                "max_pace": zone["max"],
                "min": format_pace(zone["min"]) if zone["min"] != float("inf") else "∞",
                "max": format_pace(zone["max"]) if zone["max"] != float("inf") else "∞",
            })
        return zones
    
    # Fallback: generate from threshold pace
    threshold_pace = get_athlete_threshold_pace(athlete_name)
    if not threshold_pace:
        return None
    
    t = threshold_pace
    return [
        {"zone": "Z1", "name": "Recovery", "min_pace": t * 1.35, "max_pace": float("inf")},
        {"zone": "Z2", "name": "General Aerobic", "min_pace": t * 1.20, "max_pace": t * 1.35},
        {"zone": "Z3", "name": "Marathon Pace", "min_pace": t * 1.05, "max_pace": t * 1.20},
        {"zone": "Z4", "name": "Lactate Threshold", "min_pace": t * 0.95, "max_pace": t * 1.05},
        {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": t * 0.95},
    ]


def format_pace(min_per_km):
    """Convert min/km to mm:ss format"""
    if min_per_km is None or min_per_km == float("inf"):
        return "∞"
    minutes = int(min_per_km)
    seconds = int((min_per_km - minutes) * 60)
    return f"{minutes}:{seconds:02d}"