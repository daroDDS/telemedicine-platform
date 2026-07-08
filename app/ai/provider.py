import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# The active provider is set here in ONE place.

_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
_MODEL = "gemini-flash-lite-latest"


def ask(prompt: str) -> str:
    """
    Send a prompt to the LLM and return its raw text reply.
    This is the ONLY function that knows we're using Gemini.
    """
    response = _client.models.generate_content(
        model=_MODEL,
        contents=prompt,
    )
    return response.text