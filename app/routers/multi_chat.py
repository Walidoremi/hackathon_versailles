from fastapi import APIRouter
from pydantic import BaseModel
from app.services.multi_agent_service import MultiAgentService

router = APIRouter()

class MultiAgentRequest(BaseModel):
    query: str

@router.post("/multi-chat")
async def multi_chat(req: MultiAgentRequest):
    service = MultiAgentService()
    result = await service.run(req.query)
    return result