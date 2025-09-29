import httpx
import pandas as pd
from datetime import datetime

API_KEY = "4748f8be03f278fefe157583854052f8"
ZIP_CODE = "78000,FR"

BASE_URL = "https://api.openweathermap.org/data/2.5"

async def fetch_weather():
    async with httpx.AsyncClient(verify=False) as client:
        # Météo actuelle
        current = await client.get(f"{BASE_URL}/weather?zip={ZIP_CODE}&appid={API_KEY}&units=metric&lang=fr")
        current_data = current.json()

        # Prévisions sur 5 jours (pas de 3h)
        forecast = await client.get(f"{BASE_URL}/forecast?zip={ZIP_CODE}&appid={API_KEY}&units=metric&lang=fr")
        forecast_data = forecast.json()
    print("DEBUG current_data:", current_data)

    # Extraire la météo actuelle
    # Extraire la météo actuelle en vérifiant la validité
    if "dt" in current_data and "main" in current_data:
        current_weather = {
            "datetime": datetime.utcfromtimestamp(current_data["dt"]),
            "type": "current",
            "temperature": current_data["main"]["temp"],
            "feels_like": current_data["main"]["feels_like"],
            "humidity": current_data["main"]["humidity"],
            "weather": current_data["weather"][0]["description"].capitalize()
        }
    else:
        print("⚠️ Erreur API météo (current):", current_data)
        current_weather = None


    # Extraire les prévisions
    if "list" in forecast_data:
        forecast_weather = []
        for entry in forecast_data["list"]:
            forecast_weather.append({
                "datetime": datetime.utcfromtimestamp(entry["dt"]),
                "type": "forecast",
                "temperature": entry["main"]["temp"],
                "feels_like": entry["main"]["feels_like"],
                "humidity": entry["main"]["humidity"],
                "weather": entry["weather"][0]["description"].capitalize()
            })
    else:
        print("⚠️ Erreur API météo (forecast):", forecast_data)
        forecast_weather = []


    # Construire le DataFrame
    df = pd.DataFrame([current_weather] + forecast_weather)
    df.to_csv("weather_forecast.csv", index=False, encoding="utf-8")
    print("✅ Données météo sauvegardées dans weather_forecast.csv")

# Exemple d’utilisation
if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_weather())
