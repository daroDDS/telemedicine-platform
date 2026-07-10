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
            print(f"  RESULT -> Level {r['level']}: {r['destination']}")

print("=== Scenario 1: vague headache, then all clear ===")
run([
    "j'ai mal à la tête",
    "non, rien de tout ça, juste un mal de tête léger",
])

print("\n=== Scenario 2: vague headache, then a danger sign ===")
run([
    "j'ai mal à la tête",
    "oui j'ai la nuque raide et de la fièvre",
])