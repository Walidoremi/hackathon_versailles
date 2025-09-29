import pandas as pd
from app.services.chat_service import ChatService
from app.models.chat import Message

class MultiAgentService:
    def __init__(self):
        self.base_service = ChatService()

    # --- Lecture des données externes ---
    def load_weather(self, csv_path: str, date: str) -> str:
        """Charge la météo du CSV pour une date donnée."""
        df = pd.read_csv("C:/Users/CJ6028/Downloads/llm_chat_api/data/weather_forecast.csv", parse_dates=["datetime"])
        df_day = df[df["datetime"].dt.date.astype(str) == date]

        if df_day.empty:
            return f"Aucune donnée météo disponible pour {date}."

        # Résumé simple
        rows = []
        for _, row in df_day.iterrows():
            rows.append(f"{row['datetime']}: {row['weather']}, {row['temperature']}°C")
        return "\n".join(rows)

    def load_events(self, csv_path: str, date: str) -> str:
        """Charge les événements du CSV pour une date donnée."""
        df = pd.read_csv("C:/Users/CJ6028/Downloads/llm_chat_api/data/versailles_events.csv", parse_dates=["date"])
        df_day = df[df["date"].dt.date.astype(str) == date]

        if df_day.empty:
            return f"Aucun événement particulier pour {date}."

        rows = []
        for _, row in df_day.iterrows():
            rows.append(f"{row['time']} - {row['event']} ({row['location']})")
        return "\n".join(rows)

    # --- Agents ---
    async def profiling_agent(self, user_input: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un expert en profiling touristique au Château de Versailles. "
                "Analyse le type de client : famille, couple, groupe scolaire, senior, etc. "
                "⚠️ Si l’utilisateur ne donne pas assez d’informations, fais une hypothèse "
                "et considère un visiteur adulte générique."
            )
        )
        reply, _ = await self.base_service.generate([
            system_prompt,
            Message(role="user", content=user_input)
        ])
        return reply

    async def constraints_agent(self, persona: str, weather: str, affluence: str, events: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un expert en gestion des contraintes touristiques pour Versailles. "
                "Analyse la météo, l’affluence attendue et les événements pratiques (fermetures, concerts, etc.). "
                "Fais une synthèse des contraintes pour optimiser la visite."
            )
        )

        combined_input = (
            f"Profil client: {persona}\n\n"
            f"Météo: {weather}\n\n"
            f"Affluence: {affluence}\n\n"
            f"Événements: {events}"
        )

        reply, _ = await self.base_service.generate([
            system_prompt,
            Message(role="user", content=combined_input)
        ])
        return reply

    async def planner_agent(self, user_input: str, profile: str, constraints: str) -> str:
        system_prompt = Message(
            role="system",
            content=(
                "Tu es un planificateur expert du Château de Versailles. "
                "En tenant compte du profil des visiteurs et des contraintes, "
                "propose un itinéraire optimal et détaillé de visite pour la journée."
            )
        )

        combined_input = (
            f"Profil client: {profile}\n\n"
            f"Contraintes: {constraints}\n\n"
            f"Demande utilisateur: {user_input}"
        )

        reply, _ = await self.base_service.generate([
            system_prompt,
            Message(role="user", content=combined_input)
        ])
        return reply

    # --- Orchestration ---
    async def run(self, user_input: str, date: str, weather_csv: str, events_csv: str, affluence: str) -> dict:
        # Charger les données externes
        weather_info = self.load_weather(weather_csv, date)
        events_info = self.load_events(events_csv, date)

        # Étape 1 : Profil
        profile = await self.profiling_agent(user_input)

        # Étape 2 : Contraintes
        constraints = await self.constraints_agent(profile, weather_info, affluence, events_info)

        # Étape 3 : Itinéraire
        itinerary = await self.planner_agent(user_input, profile, constraints)

        return {
            "profiling": profile,
            "constraints": constraints,
            "itinerary": itinerary,
        }