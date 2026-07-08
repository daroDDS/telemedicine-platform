from app.triage.engine import assess

# (description, complaint, group, signs, expected level)
# Expected values reflect the physician-reviewed rules (post-feedback).
scenarios = [
    # Chest pain
    ("Chest pain, adult, breathlessness",          "chest_pain", "adult", ["breathlessness"], 1),
    ("Chest pain, adult, no signs (floor 4)",      "chest_pain", "adult", [], 4),
    ("Chest pain, adult, left-arm spread",         "chest_pain", "adult", ["pain_spreading_left_arm"], 1),
    ("Chest pain, child, blue lips",               "chest_pain", "child", ["blue_lips"], 1),
    ("Chest pain, pregnant, vision changes",       "chest_pain", "pregnant", ["vision_changes"], 1),
    ("Chest pain, pregnant, no signs (floor 3)",   "chest_pain", "pregnant", [], 3),

    # Fever
    ("Fever, adult, stiff neck",                   "fever", "adult", ["stiff_neck"], 1),
    ("Fever, adult, mild short (self-care)",       "fever", "adult", ["mild_short_fever"], 5),
    ("Fever, pregnant, no signs (floor 4)",        "fever", "pregnant", [], 4),
    ("Fever, child, convulsion",                   "fever", "child", ["convulsion"], 1),

    # Cough / breathing
    ("Cough, adult, blue lips",                    "cough_breathing", "adult", ["blue_lips"], 1),
    ("Cough, adult, difficult inhalation",         "cough_breathing", "adult", ["difficult_inhalation"], 1),
    ("Cough, child, chest indrawing",              "cough_breathing", "child", ["chest_indrawing"], 1),
    ("Cough, adult, mild (self-care)",             "cough_breathing", "adult", ["mild_cough_normal_breathing"], 5),
    ("Cough, child, no L3 anymore (floor 4)",      "cough_breathing", "child", [], 4),

    # Headache
    ("Headache, adult, worst ever",                "headache", "adult", ["worst_ever_headache"], 1),
    ("Headache, child, drowsiness now L1",         "headache", "child", ["marked_drowsiness"], 1),
    ("Headache, pregnant, no signs (floor 4)",     "headache", "pregnant", [], 4),

    # Abdominal pain
    ("Abdo pain, adult, vomiting blood",           "abdominal_pain", "adult", ["vomiting_blood"], 1),
    ("Abdo pain, adult, belly swelling (new sign)","abdominal_pain", "adult", ["belly_swelling"], 1),
    ("Abdo pain, child, mild brief (L4)",          "abdominal_pain", "child", ["mild_brief_pain_playful"], 4),
    ("Abdo pain, pregnant, no signs (floor 4)",    "abdominal_pain", "pregnant", [], 4),
    ("Abdo pain, pregnant, fluid loss",            "abdominal_pain", "pregnant", ["vaginal_fluid_loss"], 1),

    # Diarrhea / vomiting
    ("Diarrhea, adult, severe dehydration",        "diarrhea_vomiting", "adult", ["severe_dehydration"], 1),
    ("Diarrhea, adult, flaccid skin (new sign)",   "diarrhea_vomiting", "adult", ["flaccid_skin"], 1),
    ("Diarrhea, child, infant won't feed",         "diarrhea_vomiting", "child", ["infant_wont_feed"], 1),

    # Injury / bleeding
    ("Injury, adult, heavy bleeding",              "injury_bleeding", "adult", ["heavy_bleeding_wont_stop"], 1),
    ("Injury, adult, shock (explicit sign)",       "injury_bleeding", "adult", ["shock_cold_clammy"], 1),
    ("Injury, adult, small cut now L5",            "injury_bleeding", "adult", ["small_cut_bruise"], 5),
    ("Injury, adult, no signs (floor 5)",          "injury_bleeding", "adult", [], 5),

    # Weakness / dizziness
    ("Weakness, adult, facial droop (stroke)",     "weakness_dizziness", "adult", ["facial_droop"], 1),
    ("Weakness, adult, cannot stand now L1",       "weakness_dizziness", "adult", ["severe_weakness_cannot_stand"], 1),
    ("Weakness, adult, mild dizziness now L5",     "weakness_dizziness", "adult", ["mild_dizziness_clear_cause"], 5),
    ("Weakness, child, very lethargic (L2)",       "weakness_dizziness", "child", ["very_lethargic_rousable"], 2),

    # Safety fallbacks
    ("Unknown complaint -> caution L2",            "broken_leg", "adult", [], 2),
    ("Multiple signs -> most urgent wins",         "chest_pain", "adult", ["mild_muscular_pain", "breathlessness"], 1),
]

passed = 0
print("\n--- Full triage engine test sweep (physician-reviewed rules) ---\n")
for description, complaint, group, signs, expected in scenarios:
    result = assess(complaint, group, signs)
    got = result["level"]
    ok = got == expected
    passed += ok
    print(f"[{'OK' if ok else 'WRONG'}] {description}  (expected L{expected}, got L{got})")

print(f"\n{passed}/{len(scenarios)} passed\n")