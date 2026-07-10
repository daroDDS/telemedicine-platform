import json
from pathlib import Path

# Load the rules file once, when this module starts.
RULES_PATH = Path(__file__).parent / "rules.json"
with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)


def assess(complaint: str, group: str, reported_signs: list[str]) -> dict:
    """
    Decide the urgency level for one complaint.

    complaint: e.g. "chest_pain"
    group: "adult", "pregnant", or "child"
    reported_signs: list of sign codes the patient has, e.g. ["breathlessness"]
    """

    # 1. Safety: if we don't know this complaint or group, be cautious.
    if complaint not in RULES:
        return {"level": 2, "reason": "Unknown complaint — defaulting to caution."}
    complaint_rules = RULES[complaint]

    if group not in complaint_rules["groups"]:
        return {"level": 2, "reason": "Unknown patient group — defaulting to caution."}
    group_rules = complaint_rules["groups"][group]

    # 2. Find every level whose signs match what the patient reported.
    matched_levels = []
    for rule in group_rules:
        for sign in rule["signs"]:
            if sign in reported_signs:
                matched_levels.append(rule["level"])
                break  # one match in this level is enough

    # 3. Highest level wins = the most urgent = the LOWEST number.
    if matched_levels:
        final_level = min(matched_levels)
    else:
        # No red flag matched. Fall back to the safe floor for this group.
        final_level = complaint_rules["floor"].get(group, 3)

    return {
        "level": final_level,
        "complaint": complaint_rules["label"],
        "group": group,
        "matched": matched_levels,
    }

def unresolved_danger_signs(complaint: str, group: str,
                            present: list[str], absent: list[str]) -> list[str]:
    """
    Return the L1/L2 red-flag signs for this complaint+group that have
    NOT yet been confirmed present or absent. These are the dangerous
    signs we must ask about before giving any reassuring result.
    """
    if complaint not in RULES:
        return []
    complaint_rules = RULES[complaint]
    if group not in complaint_rules["groups"]:
        return []

    known = set(present) | set(absent)
    unresolved = []

    for rule in complaint_rules["groups"][group]:
        if rule["level"] in (1, 2):          # only the dangerous levels
            for sign in rule["signs"]:
                if sign not in known and sign not in unresolved:
                    unresolved.append(sign)

    return unresolved