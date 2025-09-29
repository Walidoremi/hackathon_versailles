import asyncio
from app.services.chat_service import ChatService
from app.models.chat import Message

async def main():
    service = ChatService()

    # Ici tu mets ton "prompt system" pour définir le comportement du bot
    system_prompt = Message(role="system", content="Tu es un assistant très poli qui répond toujours en français.")

    # Ici tu mets ton message utilisateur
    user_message = Message(role="user", content="Donne-moi une blague courte sur les développeurs.")

    # Appel du service
    reply, usage = await service.generate([system_prompt, user_message])

    print("Réponse du chatbot :", reply)
    print("Usage :", usage)

if __name__ == "__main__":
    asyncio.run(main())