import os
from dotenv import load_dotenv
from google import genai
import time
from google.genai import errors

load_dotenv()

# The active provider is set here in ONE place.

_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
_MODEL = "gemini-flash-lite-latest"


def ask(prompt: str, _retries: int = 2) -> str:
    """
    Send a prompt to the LLM and return its raw text reply.
    Retries briefly on rate-limit (429), then gives up gracefully.
    """
    for attempt in range(_retries + 1):
        try:
            response = _client.models.generate_content(
                model=_MODEL,
                contents=prompt,
            )
            return response.text
        except errors.ClientError as e:
            # 429 = rate limited. Wait and retry a couple of times.
            if getattr(e, "status_code", None) == 429 and attempt < _retries:
                time.sleep(5)
                continue
            raise