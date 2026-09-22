import requests
import os

forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
api_key = os.getenv("OPENWEATHER_API_KEY")

print("Clé chargée :", api_key is not None)
print("Longueur de la clé :", len(api_key) if api_key else 0)

city = "Mérignac,FR"

params = {
    "q": city,
    "appid": api_key,
    "units": "metric"
}

response = requests.get(forecast_url, params=params)
print(response.status_code)