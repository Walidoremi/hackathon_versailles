from fastapi import APIRouter, Depends
from starlette.requests import Request
from ..models.chat import ChatRequest, ChatResponse
from ..services.chat_service import ChatService
from ..dependencies import enforce_api_key

router = APIRouter(dependencies=[Depends(enforce_api_key)])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, request: Request):
    service = ChatService()
    reply, usage = await service.generate(payload.messages, payload.max_tokens, payload.temperature)
    request_id = request.headers.get("x-request-id")
    return ChatResponse(reply=reply, model=service.model, usage=usage, request_id=request_id)
