from app.triage.pipeline import triage

messages = [
    "j'ai une forte douleur à la poitrine et j'ai du mal à respirer",
    "mon bébé a de la fièvre et ne veut pas manger",
    "I have a mild headache that goes away when I rest",
    "je suis enceinte et j'ai des pertes de liquide avec des douleurs au ventre",
]

for msg in messages:
    result = triage(msg)
    print(f"\nPatient: {msg}")
    print(f"  Complaint : {result['complaint']}")
    print(f"  Group     : {result['group']}")
    print(f"  Signs     : {result['signs']}")
    print(f"  → LEVEL {result['level']}: {result['destination']}")