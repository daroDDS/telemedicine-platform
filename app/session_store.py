import uuid
from app.triage.conversation import start_state

# In-memory store: session_id -> state.
# NOTE: this resets when the server restarts. We'll swap to a database
# during the persistence phase. Fine for development and demos.
_SESSIONS = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _SESSIONS[session_id] = start_state()
    return session_id


def get_state(session_id: str):
    return _SESSIONS.get(session_id)


def save_state(session_id: str, state: dict):
    _SESSIONS[session_id] = state