from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ai
import queries

app = FastAPI(title="Road Monitoring GenAI API")

# Let the dashboard (any origin during development) call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str
    use_tools: bool = False  # True -> LLM tool calling (Step 18)


class PotholeIn(BaseModel):
    route: str
    confidence: float
    risk_level: str
    severity_score: float
    latitude: float
    longitude: float
    timestamp: Optional[str] = None  # "YYYY-MM-DD HH:MM:SS"; defaults to now


@app.get("/")
def home():
    return {"message": "Road Monitoring GenAI API"}


@app.post("/ask")
def ask(q: Question):
    text = q.question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Question is empty")
    answer = ai.answer_with_tools(text) if q.use_tools else ai.answer_question(text)
    return {"answer": answer}


@app.get("/statistics")
def statistics():
    return queries.get_statistics()


@app.get("/routes")
def routes():
    return queries.get_route_summary()


@app.get("/incidents")
def incidents(limit: int = 100):
    return queries.get_incidents(limit)


@app.post("/incidents")
def add_incident(p: PotholeIn):
    """Endpoint the YOLO pipeline can POST detections to."""
    if p.risk_level.upper() not in {"HIGH", "MEDIUM", "LOW"}:
        raise HTTPException(status_code=400, detail="risk_level must be HIGH, MEDIUM or LOW")
    new_id = queries.insert_pothole(
        p.route, p.confidence, p.risk_level, p.severity_score,
        p.latitude, p.longitude, p.timestamp,
    )
    return {"id": new_id}


@app.get("/priority")
def priority(limit: int = 5):
    return queries.get_priority_incidents(limit)


@app.get("/report")
def report():
    """AI-written report for today's inspection."""
    return {
        "statistics": queries.get_daily_summary(),
        "report": ai.answer_daily_summary(),
    }
