from app.triage.engine import compute_group

# Age at/above which pregnancy is relevant to ask about.
PREGNANCY_AGE_MIN = 12


def next_intake_step(facts: dict) -> dict:
    """
    Decide what intake information is still needed.

    facts may contain: "age" (number), "gender" ("male"/"female"),
    "is_pregnant" (bool).

    Returns one of:
      {"need": "age"}                  -> must ask age
      {"need": "gender"}               -> must ask gender
      {"need": "pregnancy"}            -> must ask pregnancy status
      {"complete": True, "group": ...} -> intake done, group computed
    """
    age = facts.get("age")
    gender = facts.get("gender")
    is_pregnant = facts.get("is_pregnant")

    # 1. Age is always required.
    if age is None:
        return {"need": "age"}

    # 2. Gender is required (used to decide whether pregnancy applies).
    if gender is None:
        return {"need": "gender"}

    # 3. Pregnancy: ask only if it could apply and we don't know yet.
    pregnancy_could_apply = (gender == "female" and age >= PREGNANCY_AGE_MIN)
    if pregnancy_could_apply and is_pregnant is None:
        return {"need": "pregnancy"}

    # 4. Enough to compute the group.
    pregnant = bool(is_pregnant) if pregnancy_could_apply else False
    group = compute_group(age, pregnant)
    return {"complete": True, "group": group}