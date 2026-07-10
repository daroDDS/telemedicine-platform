from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.triage.pipeline import triage

app = FastAPI(
    title="AI Telemedicine Triage API",
    description="Triage and care-routing. Not a diagnostic tool.",
)


class TriageRequest(BaseModel):
    """What the patient sends us."""
    message: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The patient's description of their symptoms.",
    )


@app.get("/")
def read_root():
    return {"message": "Telemedicine platform is running"}


@app.post("/triage")
def triage_endpoint(request: TriageRequest):
    """
    Take a patient's free-text symptom description and return
    an urgency level and care destination, in their language.
    """
    return triage(request.message)