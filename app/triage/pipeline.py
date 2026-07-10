from app.ai.extractor import extract
from app.triage.engine import assess

# Care destinations for each urgency level.
DESTINATIONS = {
    1: "Emergency — seek emergency care or call for help immediately.",
    2: "Very urgent — seek care within a few hours.",
    3: "Urgent — see a doctor within roughly 24–48 hours.",
    4: "Standard — arrange a normal doctor's visit.",
    5: "Self-care — manage at home with monitoring. Seek care if it worsens.",
}


def triage(patient_text: str) -> dict:
    """
    Full pipeline: patient's free text -> urgency level and care destination.

    The AI only extracts codes. The rule engine makes the medical decision.
    """
    # 1. AI reads the language and extracts structured codes.
    extracted = extract(patient_text)

    complaint = extracted.get("complaint")
    group = extracted.get("group", "adult")
    signs = extracted.get("signs", [])

    # 2. Safety: if the AI could not identify a complaint, default to caution.
    if not complaint:
        return {
            "level": 3,
            "destination": DESTINATIONS[3],
            "complaint": None,
            "group": group,
            "signs": signs,
            "note": "Could not identify the complaint — defaulting to a doctor's visit.",
        }

    # 3. The rule engine decides the urgency level.
    result = assess(complaint, group, signs)
    level = result["level"]

    return {
        "level": level,
        "destination": DESTINATIONS.get(level, DESTINATIONS[3]),
        "complaint": result.get("complaint"),
        "group": group,
        "signs": signs,
        "matched_levels": result.get("matched", []),
    }