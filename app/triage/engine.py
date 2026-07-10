import json
from pathlib import Path

RULES_PATH = Path(__file__).parent / "rules.json"
with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)

INFANT_MAX_LEVEL = 3  # infants never get a result less urgent than Level 3


def assess(complaint: str, group: str, reported_signs: list) -> dict:
    if complaint not in RULES:
        return {"level": 2, "reason": "Unknown complaint — defaulting to caution."}
    complaint_rules = RULES[complaint]

    # Infants use the child rule set, but with an upward safety bias.
    is_infant = (group == "infant")
    lookup_group = "child" if is_infant else group

    if lookup_group not in complaint_rules["groups"]:
        return {"level": 2, "reason": "Unknown patient group — defaulting to caution."}
    group_rules = complaint_rules["groups"][lookup_group]

    matched_levels = []
    for rule in group_rules:
        for sign in rule["signs"]:
            if sign in reported_signs:
                matched_levels.append(rule["level"])
                break

    if matched_levels:
        final_level = min(matched_levels)
    else:
        final_level = complaint_rules["floor"].get(lookup_group, 3)

    # Infant safety cap: never less urgent than Level 2.
    if is_infant and final_level > INFANT_MAX_LEVEL:
        final_level = INFANT_MAX_LEVEL

    return {
        "level": final_level,
        "complaint": complaint_rules["label"],
        "group": group,
        "matched": matched_levels,
    }


def compute_group(age_years, is_pregnant=False):
    if is_pregnant:
        return "pregnant"
    if age_years < 1:
        return "infant"
    if age_years <= 15:
        return "child"
    return "adult"


def unresolved_danger_signs(complaint, group, present, absent):
    if complaint not in RULES:
        return []
    complaint_rules = RULES[complaint]
    lookup_group = "child" if group == "infant" else group
    if lookup_group not in complaint_rules["groups"]:
        return []
    known = set(present) | set(absent)
    unresolved = []
    for rule in complaint_rules["groups"][lookup_group]:
        if rule["level"] in (1, 2):
            for sign in rule["signs"]:
                if sign not in known and sign not in unresolved:
                    unresolved.append(sign)
    return unresolved