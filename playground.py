import asyncio
from app.services.multi_agent_service import MultiAgentService

async def main():
    service = MultiAgentService()

    user_input = "Nous voulons visiter Versailles demain."
    date = "2025-09-29"
    affluence_info = "Affluence très forte le matin, plus calme après 15h."

    result = await service.run(
        user_input=user_input,
        date=date,
        weather_csv="weather_forecast.csv",
        events_csv="versailles_events.csv",
        affluence=affluence_info
    )

    print("\n=== Profiling ===\n", result["profiling"])
    print("\n=== Contraintes ===\n", result["constraints"])
    print("\n=== Itinéraire ===\n", result["itinerary"])

if __name__ == "__main__":
    asyncio.run(main())