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

def ask_about(signs: list[str], language: str = "fr") -> str:
    """
    Given a list of red-flag sign codes, produce ONE natural-language
    question (in the patient's language) that asks whether the patient
    has any of them. The AI only phrases language — it decides nothing.
    """
    # Only ask about a few at a time, so the question stays digestible.
    batch = signs[:4]

    lang_name = {"fr": "French", "en": "English"}.get(language, "French")

    prompt = f"""You are a caring medical intake assistant. Ask the patient ONE short, clear question in {lang_name} to find out whether they have any of the following warning signs. Group them naturally into a single question. Use simple, reassuring words a worried person can understand. Do NOT diagnose. Do NOT mention the internal code names.

Warning signs (internal codes): {batch}

Reply with ONLY the question text, nothing else."""

    return ask(prompt).strip()

def interpret_answer(patient_reply: str, asked_signs: list[str]) -> dict:
    """
    Given the patient's reply and the exact signs we asked about,
    decide which are present and which are absent.

    Returns {"present": [...], "absent": [...]}.
    A sign is only 'absent' if the patient clearly denies it.
    Anything unclear is left out (stays unknown -> we may ask again).
    """
    prompt = f"""You are a medical intake assistant interpreting a patient's answer. You do NOT diagnose.

We asked the patient about these specific warning signs (internal codes):
{asked_signs}

The patient replied: "{patient_reply}"

For each sign in the list, decide:
- "present": the patient clearly indicates they HAVE it.
- "absent": the patient clearly indicates they do NOT have it.
- If unclear or not addressed, put it in NEITHER list.

Important: only use the exact codes from the list above. If the patient gives a blanket "no", mark ALL the asked signs as absent.

Reply with ONLY a JSON object in exactly this format:
{{"present": ["..."], "absent": ["..."]}}"""

    raw = ask(prompt)

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
        # Safety: only keep codes we actually asked about.
        present = [s for s in result.get("present", []) if s in asked_signs]
        absent = [s for s in result.get("absent", []) if s in asked_signs]
        return {"present": present, "absent": absent}
    except json.JSONDecodeError:
        # If we can't parse, treat nothing as resolved (we'll ask again).
        return {"present": [], "absent": []}