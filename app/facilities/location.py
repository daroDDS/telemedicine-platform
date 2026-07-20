import json
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

CITIES_PATH = Path(__file__).parent / "cities.json"
try:
    with open(CITIES_PATH, "r", encoding="utf-8") as f:
        CITIES = json.load(f)
except FileNotFoundError:
    CITIES = []


def _normalize(text: str) -> str:
    """Lowercase, strip accents and punctuation, for forgiving matching."""
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "".join(c for c in text if c.isalnum() or c.isspace()).strip()


def resolve_city(user_text: str, threshold: float = 0.7):
    """
    Turn a user-typed place name into coordinates.

    Returns {"city","region","lat","lon","match_score"} or None if no
    confident match. Handles case, accents, and minor misspellings.
    """
    if not CITIES or not user_text:
        return None

    query = _normalize(user_text)
    best = None
    best_score = 0.0

    for c in CITIES:
        name = _normalize(c["city"])
        # Exact or substring match is strongest.
        if query == name:
            score = 1.0
        elif query in name or name in query:
            score = 0.9
        else:
            score = SequenceMatcher(None, query, name).ratio()

        if score > best_score:
            best_score = score
            best = c

    if best and best_score >= threshold:
        return {
            "city": best["city"],
            "region": best["region"],
            "lat": best["lat"],
            "lon": best["lon"],
            "match_score": round(best_score, 2),
        }
    return None