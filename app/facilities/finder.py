import json
from math import radians, sin, cos, asin, sqrt
from pathlib import Path

FACILITIES_PATH = Path(__file__).parent / "facilities.json"
with open(FACILITIES_PATH, "r", encoding="utf-8") as f:
    FACILITIES = json.load(f)

# Which facility types are appropriate for each urgency level, best first.
LEVEL_TYPES = {
    1: ["hopital"],
    2: ["hopital", "centre de sante"],
    3: ["centre de sante", "poste de sante"],
    4: ["poste de sante", "centre de sante"],
    5: ["poste de sante", "case de sante"],
}

# Beyond this distance (km), the recommended facility is considered far,
# and we also suggest a closer interim option.
FAR_THRESHOLD_KM = 30.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in kilometres."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def _nearest_of_types(lat, lon, types, limit=3):
    """Nearest facilities matching any of the given types."""
    matches = [f for f in FACILITIES if f["type"] in types]
    for f in matches:
        f = f  # noqa
    scored = [
        {**f, "distance_km": round(haversine_km(lat, lon, f["lat"], f["lon"]), 1)}
        for f in matches
    ]
    scored.sort(key=lambda x: x["distance_km"])
    return scored[:limit]


def recommend(level: int, lat: float, lon: float) -> dict:
    """
    Recommend facilities for a given urgency level and patient location.

    Returns the nearest appropriate facilities, and if the nearest one is
    far, also a closer interim option that could stabilise or refer.
    """
    types = LEVEL_TYPES.get(level, LEVEL_TYPES[3])
    primary = _nearest_of_types(lat, lon, types, limit=3)

    result = {"level": level, "recommended": primary, "interim": None, "far": False}

    if not primary:
        result["note"] = "no_facility_found"
        return result

    nearest_km = primary[0]["distance_km"]
    if nearest_km > FAR_THRESHOLD_KM:
        result["far"] = True
        # Find any closer facility of a lower tier that could help meanwhile.
        all_types = ["hopital", "centre de sante", "poste de sante", "case de sante"]
        closer = _nearest_of_types(lat, lon, all_types, limit=1)
        if closer and closer[0]["distance_km"] < nearest_km:
            result["interim"] = closer[0]

    return result