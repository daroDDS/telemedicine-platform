import time
from app.triage.conversation import start_state, step

state = start_state()
msgs = ["j'ai mal à la tête", "30 ans", "un homme", "oui j'ai la nuque raide et de la fièvre"]

for msg in msgs:
    print(f"\nPATIENT: {msg}")
    turn = step(state, msg, lat=14.6690, lon=-17.4390)
    state = turn["state"]
    if "question" in turn:
        print(f"  ASK: {turn['question']}")
    else:
        r = turn["result"]
        print(f"  RESULT -> Level {r['level']}: {r['destination']}")
        if r.get("facilities"):
            print("  Nearest facilities:")
            for f in r["facilities"]["recommended"]:
                print(f"     • {f['name']} ({f['type']}) — {f['distance_km']} km")
            if r["facilities"].get("far"):
                print("     (nearest is far; interim option provided)")
    time.sleep(4)   # stay under the free-tier rate limit