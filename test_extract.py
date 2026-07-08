from app.ai.extractor import extract

messages = [
    "j'ai une forte douleur à la poitrine et j'ai du mal à respirer",
    "mon bébé a de la fièvre et ne veut pas manger",
    "I have a mild headache that goes away when I rest",
]

for msg in messages:
    print(f"\nPatient: {msg}")
    print(f"Extracted: {extract(msg)}")