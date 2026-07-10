import json
from pathlib import Path

from app.ai.extractor import extract
from app.triage.engine import assess

MESSAGES_PATH = Path(__file__).parent / "messages.json"
with open(MESSAGES_PATH, "r", encoding="utf-8") as f:
    MESSAGES = json.load(f)

DEFAULT_LANGUAGE = "fr"


def _messages_for(language: str) -> dict:
    """Return the message set for a language, falling back to French."""
    return MESSAGES.get(language, MESSAGES[DEFAULT_LANGUAGE])


def triage(patient_text: str) -> dict:
    """
    Full pipeline: patient's free text -> urgency level and care destination,
    replied in the patient's own language.

    The AI only extracts codes and detects language.
    The rule engine makes the medical decision.
    """
    extracted = extract(patient_text)

    complaint = extracted.get("complaint")
    group = extracted.get("group", "adult")
    signs = extracted.get("signs", [])
    language = extracted.get("language", DEFAULT_LANGUAGE)

    texts = _messages_for(language)

    # Safety: no complaint identified -> cautious default, in their language.
    if not complaint:
        return {
            "level": 3,
            "destination": texts["unknown"],
            "disclaimer": texts["disclaimer"],
            "complaint": None,
            "group": group,
            "signs": signs,
            "language": language,
        }

    result = assess(complaint, group, signs)
    level = result["level"]

    return {
        "level": level,
        "destination": texts[str(level)],
        "disclaimer": texts["disclaimer"],
        "complaint": result.get("complaint"),
        "group": group,
        "signs": signs,
        "language": language,
        "matched_levels": result.get("matched", []),
    }