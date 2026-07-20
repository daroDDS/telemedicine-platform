from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.triage.conversation import step
from app.session_store import create_session, get_state, save_state

app = FastAPI(
    title="AI Telemedicine Triage API",
    description="Multi-turn triage and care-routing. Not a diagnostic tool.",
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None)
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Patient latitude (from browser GPS)")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="Patient longitude")


@app.get("/")
def read_root():
    return {"message": "Telemedicine platform is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    # New conversation if no session_id given.
    if request.session_id is None:
        session_id = create_session()
    else:
        session_id = request.session_id
        if get_state(session_id) is None:
            raise HTTPException(status_code=404, detail="Session not found.")

    state = get_state(session_id)

    # Advance the conversation by one turn.
    turn = step(state, request.message, lat=request.lat, lon=request.lon)
    save_state(session_id, turn["state"])

    # Build the response: either a follow-up question or a final result.
    response = {"session_id": session_id}
    if "question" in turn:
        response["type"] = "question"
        response["message"] = turn["question"]
    else:
        response["type"] = "result"
        response["result"] = turn["result"]

    return response