# chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.multi_agent_service import MultiAgentService
from app.services.embeddings import mistral_embedding

router = APIRouter(tags=["Evaluation"])

class EvalChatRequest(BaseModel):
    question: str
    date: str | None = None

@router.post("/chat")
async def eval_chat(req: EvalChatRequest):
    service = MultiAgentService()
    date = req.date or "2025-09-30"

    response = await service.run(
        user_input=req.question,
        date=date,
        weather_csv="data/weather_forecast.csv",
        events_csv="data/versailles_events.csv",
        billetterie_csv="data/billeterie.csv",
        hotels_csv="data/logement.csv",
        embedding_fn=mistral_embedding,
    )

    return {"question": req.question, "response": response}