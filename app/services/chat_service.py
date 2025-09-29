import httpx
from typing import List
from ..models.chat import Message
from ..config import settings

class ChatService:
    def __init__(self):
        self.model = settings.mistral_model

    async def generate(self, messages: List[Message], max_tokens: int = 512, temperature: float = 0.7):
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.mistral_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [m.dict(exclude_none=True) for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            print("DEBUG STATUS:", r.status_code, r.text[:200])  # debug
            r.raise_for_status()
            data = r.json()

        reply = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return reply, usage