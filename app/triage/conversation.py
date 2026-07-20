from app.ai.extractor import (
    extract, ask_about, interpret_answer,
    interpret_age, interpret_gender, interpret_yes_no,
)
from app.triage.engine import assess, unresolved_danger_signs
from app.triage.intake import next_intake_step
from app.triage.pipeline import _messages_for, DEFAULT_LANGUAGE
from app.facilities.finder import recommend

# Intake question wording, per language.
INTAKE_QUESTIONS = {
    "fr": {
        "age": "Pour commencer, quel âge avez-vous ?",
        "gender": "Êtes-vous un homme ou une femme ?",
        "pregnancy": "Êtes-vous actuellement enceinte ?",
        "symptoms": "Merci. Décrivez maintenant ce que vous ressentez.",
    },
    "en": {
        "age": "To start, how old are you?",
        "gender": "Are you male or female?",
        "pregnancy": "Are you currently pregnant?",
        "symptoms": "Thank you. Now please describe what you are feeling.",
    },
}


def start_state() -> dict:
    return {
        "phase": "intake",
        "language": DEFAULT_LANGUAGE,
        "facts": {},
        "group": None,
        "pending_intake": None,
        "complaint": None,
        "present": [],
        "absent": [],
        "asked": [],
        "first_message": None,
        "lat": None,
        "lon": None,
    }


def _q(language, key):
    return INTAKE_QUESTIONS.get(language, INTAKE_QUESTIONS[DEFAULT_LANGUAGE])[key]


def step(state: dict, patient_message: str, lat: float = None, lon: float = None) -> dict:
    # Remember the patient's location if the browser provided it.
    if lat is not None and lon is not None:
        state["lat"] = lat
        state["lon"] = lon
    # Detect language from the very first message, and capture any symptom text.
    if state["language"] == DEFAULT_LANGUAGE and state["phase"] == "intake" and state["pending_intake"] is None:
        extracted = extract(patient_message)
        state["language"] = extracted.get("language", DEFAULT_LANGUAGE)
        # Keep the symptom for later if the patient led with one.
        if extracted.get("complaint"):
            state["first_message"] = patient_message
            state["complaint"] = extracted.get("complaint")
            state["present"] = list(extracted.get("signs", []))

    # ---------- PHASE 1: INTAKE ----------
    if state["phase"] == "intake":
        # If we just asked an intake question, interpret the answer.
        if state["pending_intake"] == "age":
            state["facts"]["age"] = interpret_age(patient_message)
        elif state["pending_intake"] == "gender":
            state["facts"]["gender"] = interpret_gender(patient_message)
        elif state["pending_intake"] == "pregnancy":
            state["facts"]["is_pregnant"] = interpret_yes_no(patient_message)
        state["pending_intake"] = None

        # What intake info is still needed?
        nxt = next_intake_step(state["facts"])
        if "need" in nxt:
            state["pending_intake"] = nxt["need"]
            return {"state": state, "question": _q(state["language"], nxt["need"])}

        # Intake complete — group is now known from facts.
        state["group"] = nxt["group"]
        state["phase"] = "symptoms"
        # If patient already gave symptoms, skip straight to the dialogue phase.
        if state["complaint"]:
            state["phase"] = "dialogue"
        else:
            return {"state": state, "question": _q(state["language"], "symptoms")}

    # ---------- PHASE 2: SYMPTOMS ----------
    if state["phase"] == "symptoms":
        extracted = extract(patient_message)
        state["complaint"] = extracted.get("complaint")
        for s in extracted.get("signs", []):
            if s not in state["present"]:
                state["present"].append(s)
        state["phase"] = "dialogue"

    # ---------- PHASE 3: DANGER-SIGN DIALOGUE ----------
    if state["phase"] == "dialogue":
        # Interpret an answer to a previous danger-sign question, if any.
        if state["asked"]:
            update = interpret_answer(patient_message, state["asked"])
            for s in update["present"]:
                if s not in state["present"]:
                    state["present"].append(s)
            for s in update["absent"]:
                if s not in state["absent"]:
                    state["absent"].append(s)
            state["asked"] = []

        texts = _messages_for(state["language"])

        if not state["complaint"]:
            state["phase"] = "done"
            return {"state": state, "result": {
                "level": 3, "destination": texts["unknown"],
                "disclaimer": texts["disclaimer"], "complaint": None,
                "group": state["group"], "language": state["language"],
            }}

        unresolved = unresolved_danger_signs(
            state["complaint"], state["group"], state["present"], state["absent"])
        all_danger = unresolved_danger_signs(
            state["complaint"], state["group"], present=[], absent=[])
        danger_present = any(s in state["present"] for s in all_danger)

        if unresolved and not danger_present:
            state["asked"] = unresolved[:4]
            return {"state": state, "question": ask_about(state["asked"], state["language"])}

        # Safe to triage.
        state["phase"] = "done"
        result = assess(state["complaint"], state["group"], state["present"])
        level = result["level"]

        final = {
            "level": level,
            "destination": texts[str(level)],
            "disclaimer": texts["disclaimer"],
            "complaint": result.get("complaint"),
            "group": state["group"],
            "language": state["language"],
            "signs": state["present"],
        }

        # Enrich with facility recommendation if we know where they are.
        if state.get("lat") is not None and state.get("lon") is not None:
            final["facilities"] = recommend(level, state["lat"], state["lon"])
        else:
            final["facilities"] = None
            final["facilities_note"] = "no_location"

        return {"state": state, "final_result": final} if False else {"state": state, "result": final}