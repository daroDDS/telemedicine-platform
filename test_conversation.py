from app.triage.conversation import start_state, step

def run(messages):
    state = start_state()
    for msg in messages:
        print(f"\nPATIENT: {msg}")
        turn = step(state, msg)
        state = turn["state"]
        if "question" in turn:
            print(f"  ASK: {turn['question']}")
        else:
            r = turn["result"]
            print(f"  RESULT -> Level {r['level']} ({r.get('group')}): {r['destination']}")

print("=== Adult, led with symptom, then danger sign ===")
run([
    "j'ai mal à la tête",
    "30 ans",
    "un homme",
    "oui j'ai la nuque raide et de la fièvre",
])

print("\n=== Pregnant woman ===")
run([
    "j'ai mal au ventre",
    "28 ans",
    "une femme",
    "oui je suis enceinte",
    "non, pas de saignement ni de perte",
])