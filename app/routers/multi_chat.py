from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.multi_agent_service import MultiAgentService
from app.services.embeddings import mistral_embedding
from app.dependencies import enforce_api_key

router = APIRouter()

class MultiChatRequest(BaseModel):
    user_input: str
    date: str
    weather_csv: str
    events_csv: str

@router.post("/multi-chat", dependencies=[Depends(enforce_api_key)])
async def multi_chat(req: MultiChatRequest):
    service = MultiAgentService()
    result = await service.run(
        user_input=req.user_input,
        date=req.date,
        weather_csv=req.weather_csv,
        events_csv=req.events_csv,
        embedding_fn=mistral_embedding  # ici on connecte Qdrant
    )
    return result