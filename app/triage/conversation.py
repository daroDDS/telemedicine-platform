from app.ai.extractor import extract, ask_about, interpret_answer
from app.triage.engine import assess, unresolved_danger_signs
from app.triage.pipeline import _messages_for, DEFAULT_LANGUAGE


def start_state() -> dict:
    """The empty memory of a new conversation."""
    return {
        "complaint": None,
        "group": "adult",
        "language": DEFAULT_LANGUAGE,
        "present": [],
        "absent": [],
        "asked": [],          # signs we asked about most recently
        "status": "new",       # new -> asking -> done
    }


def step(state: dict, patient_message: str) -> dict:
    """
    Advance the conversation by one turn.

    Returns the updated state plus either:
      - "question": text to ask the patient next, or
      - "result": the final triage outcome.
    """

    # --- Turn 1: first message, extract the basics ---
    if state["status"] == "new":
        extracted = extract(patient_message)
        state["complaint"] = extracted.get("complaint")
        state["group"] = extracted.get("group", "adult")
        state["language"] = extracted.get("language", DEFAULT_LANGUAGE)
        state["present"] = list(extracted.get("signs", []))

    # --- Follow-up turns: interpret the answer to what we asked ---
    else:
        if state["asked"]:
            update = interpret_answer(patient_message, state["asked"])
            for s in update["present"]:
                if s not in state["present"]:
                    state["present"].append(s)
            for s in update["absent"]:
                if s not in state["absent"]:
                    state["absent"].append(s)

    texts = _messages_for(state["language"])

    # --- Safety: no complaint identified -> cautious result ---
    if not state["complaint"]:
        state["status"] = "done"
        return {
            "state": state,
            "result": {
                "level": 3,
                "destination": texts["unknown"],
                "disclaimer": texts["disclaimer"],
                "complaint": None,
                "group": state["group"],
                "language": state["language"],
            },
        }

    # --- The core decision: any dangerous signs still unknown? ---
    unresolved = unresolved_danger_signs(
        state["complaint"], state["group"],
        state["present"], state["absent"],
    )

    # All L1/L2 danger signs for this complaint+group (ignoring what's known yet).
    all_danger = unresolved_danger_signs(
        state["complaint"], state["group"], present=[], absent=[]
    )
    # Is any danger sign already confirmed present? Then triage now.
    danger_present = any(s in state["present"] for s in all_danger)

    if unresolved and not danger_present:
        # Still dangerous unknowns -> ask about them.
        state["asked"] = unresolved[:4]
        state["status"] = "asking"
        question = ask_about(state["asked"], state["language"])
        return {"state": state, "question": question}

    # --- Safe to triage ---
    state["status"] = "done"
    result = assess(state["complaint"], state["group"], state["present"])
    level = result["level"]
    return {
        "state": state,
        "result": {
            "level": level,
            "destination": texts[str(level)],
            "disclaimer": texts["disclaimer"],
            "complaint": result.get("complaint"),
            "group": state["group"],
            "language": state["language"],
            "signs": state["present"],
        },
    }