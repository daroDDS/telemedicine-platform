from app.triage.engine import unresolved_danger_signs

# Headache, adult. Nothing known yet -> should list all L1/L2 headache signs.
print("Nothing known yet:")
print(unresolved_danger_signs("headache", "adult", present=[], absent=[]))

# Patient confirmed 'worst_ever_headache' is PRESENT -> it's a danger sign,
# but still list the OTHER unresolved dangerous ones.
print("\nWorst-ever headache present:")
print(unresolved_danger_signs("headache", "adult",
                              present=["worst_ever_headache"], absent=[]))

# Patient ruled out several -> those drop off the list.
print("\nSome ruled out:")
print(unresolved_danger_signs("headache", "adult",
                              present=[],
                              absent=["worst_ever_headache", "stiff_neck_fever_rash",
                                      "confusion", "vision_changes"]))

from app.ai.extractor import ask_about
from app.triage.engine import unresolved_danger_signs

print("\n--- Question generation ---")

signs_fr = unresolved_danger_signs("headache", "adult", present=[], absent=[])
print("\nFrench question about headache danger signs:")
print(ask_about(signs_fr, language="fr"))

print("\nEnglish question about the same:")
print(ask_about(signs_fr, language="en"))

from app.ai.extractor import interpret_answer

print("\n--- Answer interpretation ---")

asked = ["worst_ever_headache", "stiff_neck_fever_rash", "confusion", "weakness_one_side"]

tests = [
    "non, juste un mal de tête normal",
    "oui j'ai la nuque très raide et de la fièvre",
    "no sudden headache but I do feel confused",
    "I don't know",
]

for reply in tests:
    print(f"\nPatient reply: {reply}")
    print(f"  -> {interpret_answer(reply, asked)}")