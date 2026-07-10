import json
from pathlib import Path
from app.ai.provider import ask

RULES_PATH = Path(__file__).parent.parent / "triage" / "rules.json"
with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)


def get_valid_codes() -> dict:
    """
    Pull every valid complaint and sign code out of rules.json,
    so the AI is told exactly which codes it may use.
    """
    vocabulary = {}
    for complaint_key, complaint_data in RULES.items():
        signs = set()
        for group_rules in complaint_data["groups"].values():
            for rule in group_rules:
                for sign in rule["signs"]:
                    signs.add(sign)
        vocabulary[complaint_key] = sorted(signs)
    return vocabulary

def extract(patient_text: str) -> dict:
    """
    Turn a patient's free-text description into structured triage input.
    The AI ONLY identifies codes — it does NOT decide urgency.
    """
    vocabulary = get_valid_codes()

    prompt = f"""You are a medical intake assistant. Your ONLY job is to read a patient's message and identify structured codes. You do NOT diagnose or assess urgency.

From the patient message, identify:
1. "complaint": the single best-matching complaint key, or null if none fits.
2. "group": one of "adult", "pregnant", or "child". If unclear, use "adult".
3. "signs": a list of sign codes that the patient's message clearly indicates.
4. "language": the language the patient wrote in — "fr" for French, "en" for English. If unsure, use "fr".

You MUST only use codes from this exact list. Do not invent codes.

Valid complaints and their allowed signs:
{json.dumps(vocabulary, indent=2)}

Patient message: "{patient_text}"

Reply with ONLY a JSON object, no other text, in exactly this format:
{{"complaint": "...", "group": "...", "signs": ["..."], "language": "fr"}}"""

    raw = ask(prompt)

    # The AI sometimes wraps JSON in ```json ... ``` — clean that off.
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"complaint": None, "group": "adult", "signs": [], "language": "fr",
                "error": "Could not parse AI response", "raw": raw}

    return result