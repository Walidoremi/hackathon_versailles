from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class Message(BaseModel):
    role: str = Field(examples=["user", "assistant", "system"])
    content: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    stream: bool = False

class ChatResponse(BaseModel):
    reply: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
