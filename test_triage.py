from app.triage.engine import assess

# A few scenarios: (description, complaint, group, signs, expected level)
scenarios = [
    ("Adult, chest pain + breathlessness", "chest_pain", "adult", ["breathlessness"], 1),
    ("Adult, mild muscular chest pain",    "chest_pain", "adult", ["mild_muscular_pain"], 4),
    ("Adult, chest pain, no red flags",    "chest_pain", "adult", [], 4),  # floor
    ("Child, chest pain + blue lips",      "chest_pain", "child", ["blue_lips"], 1),
    ("Pregnant, chest pain + vision changes", "chest_pain", "pregnant", ["vision_changes"], 1),
    ("Adult, severe + breathlessness (2 signs)", "chest_pain", "adult", ["severe_pain", "breathlessness"], 1),
]

print("\n--- Triage engine test ---\n")
for description, complaint, group, signs, expected in scenarios:
    result = assess(complaint, group, signs)
    got = result["level"]
    status = "OK" if got == expected else "WRONG"
    print(f"[{status}] {description}")
    print(f"       expected L{expected}, got L{got}\n")