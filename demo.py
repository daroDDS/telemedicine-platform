"""Demo script — runs scripted triage conversations with readable output."""
from app.triage.conversation import start_state, step
from app.facilities.finder import recommend

LINE = "─" * 70

def run_conversation(title, messages, location=None):
    print(f"\n{LINE}\n  {title}\n{LINE}")
    state = start_state()
    for msg in messages:
        print(f"\n  PATIENT : {msg}")
        turn = step(state, msg)
        state = turn["state"]
        if "question" in turn:
            print(f"  SYSTÈME : {turn['question']}")
        else:
            r = turn["result"]
            print(f"\n  ┌─ RÉSULTAT ─────────────────────────────────")
            print(f"  │ Groupe   : {r.get('group')}")
            print(f"  │ Motif    : {r.get('complaint')}")
            print(f"  │ Signes   : {', '.join(r.get('signs', [])) or '—'}")
            print(f"  │ NIVEAU {r['level']}")
            print(f"  │ {r['destination']}")
            print(f"  └────────────────────────────────────────────")
            if location:
                show_facilities(r["level"], *location)
            return

def show_facilities(level, lat, lon, place=""):
    rec = recommend(level, lat, lon)
    print(f"\n  ORIENTATION {place}:")
    for f in rec["recommended"][:3]:
        print(f"    • {f['name']} ({f['type']}, {f['region']}) — {f['distance_km']} km")
    if rec["far"]:
        print(f"    ⚠  L'établissement le plus proche est loin.")
        if rec["interim"]:
            i = rec["interim"]
            print(f"    → En attendant : {i['name']} ({i['type']}) — {i['distance_km']} km")


if __name__ == "__main__":
    # DEMO 1: the danger the dialogue catches
    run_conversation(
        "DEMO 1 — Vague symptom, dialogue uncovers an emergency",
        ["j'ai mal à la tête", "30 ans", "un homme",
         "oui j'ai la nuque raide et de la fièvre"],
        location=(14.6690, -17.4390),  # Dakar
    )

    # DEMO 2: same start, safe outcome
    run_conversation(
        "DEMO 2 — Same opening, but no danger signs → self-care",
        ["j'ai mal à la tête", "30 ans", "un homme",
         "non, rien de tout ça", "non, aucun de ces signes"],
        location=(14.6690, -17.4390),
    )

    # DEMO 3: the access gap
    print(f"\n{LINE}\n  DEMO 3 — The access gap: same emergency, two regions\n{LINE}")
    show_facilities(1, 14.6690, -17.4390, "— Patient à Dakar")
    show_facilities(1, 12.5500, -12.1800, "— Patient à Kédougou")