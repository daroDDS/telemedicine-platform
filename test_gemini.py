import os
from dotenv import load_dotenv
from google import genai

# Load the key from .env into the environment
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("No API key found — check your .env file.")
    exit()

# Create the client (this is the connection to Gemini)
client = genai.Client(api_key=api_key)

# A simple test message
response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents="Say 'hello, the connection works' in French.",
)

print(response.text)