from app.triage.engine import assess

# (description, complaint, group, signs, expected level)
scenarios = [
    # Chest pain
    ("Chest pain, adult, breathlessness",        "chest_pain", "adult", ["breathlessness"], 1),
    ("Chest pain, adult, no signs (floor 4)",    "chest_pain", "adult", [], 4),
    ("Chest pain, child, blue lips",             "chest_pain", "child", ["blue_lips"], 1),
    ("Chest pain, pregnant, vision changes",     "chest_pain", "pregnant", ["vision_changes"], 1),

    # Fever
    ("Fever, adult, stiff neck",                 "fever", "adult", ["stiff_neck"], 1),
    ("Fever, adult, mild short (self-care)",     "fever", "adult", ["mild_short_fever"], 5),
    ("Fever, pregnant, no signs (floor 2)",      "fever", "pregnant", [], 2),
    ("Fever, child, convulsion",                 "fever", "child", ["convulsion"], 1),

    # Cough / breathing
    ("Cough, adult, blue lips",                  "cough_breathing", "adult", ["blue_lips"], 1),
    ("Cough, child, chest indrawing",            "cough_breathing", "child", ["chest_indrawing"], 1),
    ("Cough, adult, mild (self-care)",           "cough_breathing", "adult", ["mild_cough_normal_breathing"], 5),

    # Headache
    ("Headache, adult, worst ever",              "headache", "adult", ["worst_ever_headache"], 1),
    ("Headache, child, marked drowsiness (L2)",  "headache", "child", ["marked_drowsiness"], 2),
    ("Headache, pregnant, no signs (floor 2)",   "headache", "pregnant", [], 2),

    # Abdominal pain
    ("Abdo pain, adult, vomiting blood",         "abdominal_pain", "adult", ["vomiting_blood"], 1),
    ("Abdo pain, child, mild brief (L4)",        "abdominal_pain", "child", ["mild_brief_pain_playful"], 4),
    ("Abdo pain, pregnant, no signs (floor 2)",  "abdominal_pain", "pregnant", [], 2),

    # Diarrhea / vomiting
    ("Diarrhea, adult, severe dehydration",      "diarrhea_vomiting", "adult", ["severe_dehydration"], 1),
    ("Diarrhea, child, infant won't feed",       "diarrhea_vomiting", "child", ["infant_wont_feed"], 1),

    # Injury / bleeding
    ("Injury, adult, heavy bleeding",            "injury_bleeding", "adult", ["heavy_bleeding_wont_stop"], 1),
    ("Injury, adult, small cut (floor 4, no L5)","injury_bleeding", "adult", ["small_cut_bruise"], 4),
    ("Injury, adult, no signs (floor 4)",        "injury_bleeding", "adult", [], 4),

    # Weakness / dizziness
    ("Weakness, adult, facial droop (stroke)",   "weakness_dizziness", "adult", ["facial_droop"], 1),
    ("Weakness, child, very lethargic (L2)",     "weakness_dizziness", "child", ["very_lethargic_rousable"], 2),

    # Safety fallbacks
    ("Unknown complaint -> caution L2",          "broken_leg", "adult", [], 2),
    ("Multiple signs -> most urgent wins",       "chest_pain", "adult", ["mild_muscular_pain", "breathlessness"], 1),
]

passed = 0
print("\n--- Full triage engine test sweep ---\n")
for description, complaint, group, signs, expected in scenarios:
    result = assess(complaint, group, signs)
    got = result["level"]
    ok = got == expected
    passed += ok
    print(f"[{'OK' if ok else 'WRONG'}] {description}  (expected L{expected}, got L{got})")

print(f"\n{passed}/{len(scenarios)} passed\n")