from app.triage.pipeline import triage

messages = [
    "j'ai une forte douleur à la poitrine et j'ai du mal à respirer",
    "mon bébé a de la fièvre et ne veut pas manger",
    "I have a mild headache that goes away when I rest",
    "je suis enceinte et j'ai des pertes de liquide avec des douleurs au ventre",
    "I fell and I have a small cut on my knee",
]

for msg in messages:
    r = triage(msg)
    print(f"\nPatient: {msg}")
    print(f"  Lang  : {r['language']}  | Group: {r['group']}  | Signs: {r['signs']}")
    print(f"  → NIVEAU/LEVEL {r['level']}: {r['destination']}")
    print(f"  {r['disclaimer']}")