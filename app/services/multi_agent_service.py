from app.services.chat_service import ChatService
from app.models.chat import Message

class MultiAgentService:
    def __init__(self):
        self.base_service = ChatService()

    async def profiling_agent(self, user_input: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un expert en profiling touristique. "
                "Analyse le type de client (famille, couple, groupe scolaire, senior, etc.) "
                "en fonction des critères donnés."
            )
        )
        reply, _ = await self.base_service.generate([system_prompt, Message(role="user", content=user_input)])
        return reply

    async def constraints_agent(self, user_input: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un expert en gestion des contraintes touristiques. "
                "Analyse la météo, l’affluence attendue et les contraintes logistiques."
            )
        )
        reply, _ = await self.base_service.generate([system_prompt, Message(role="user", content=user_input)])
        return reply

    async def planner_agent(self, user_input: str, profile: str, constraints: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un planificateur d’itinéraires touristiques. "
                "En tenant compte du profil des clients et des contraintes, "
                "propose un itinéraire optimal clair et précis."
            )
        )
        combined_input = (
            f"Description client: {profile}\n"
            f"Contraintes: {constraints}\n"
            f"Demande utilisateur: {user_input}"
        )
        reply, _ = await self.base_service.generate([system_prompt, Message(role="user", content=combined_input)])
        return reply

    async def run(self, user_input: str) -> dict:
        profile = await self.profiling_agent(user_input)
        constraints = await self.constraints_agent(user_input)
        itinerary = await self.planner_agent(user_input, profile, constraints)

        return {
            "profiling": profile,
            "constraints": constraints,
            "itinerary": itinerary,
        }
