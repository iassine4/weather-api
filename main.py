import os
from datetime import datetime, timedelta, timezone

import requests

from terminal_ui import display_city, display_error, display_footer, display_header


FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
CITIES = ["Mérignac,FR", "Saint-Geours-de-Maremne,FR", "Toulouse,FR"]


def get_forecasts(city, api_key):
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(FORECAST_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def group_daily_temperatures(forecasts, local_timezone):
    daily_temperatures = {}
    for forecast in forecasts:
        date = datetime.fromtimestamp(forecast["dt"], local_timezone).date()
        temp_min = forecast["main"]["temp_min"]
        temp_max = forecast["main"]["temp_max"]
        if date not in daily_temperatures:
            daily_temperatures[date] = {"temp_min": temp_min, "temp_max": temp_max}
        else:
            daily_temperatures[date]["temp_min"] = min(
                daily_temperatures[date]["temp_min"], temp_min
            )
            daily_temperatures[date]["temp_max"] = max(
                daily_temperatures[date]["temp_max"], temp_max
            )
    return daily_temperatures


def display_forecasts(city, data):
    # Décalage local fourni par l'API, en secondes par rapport à UTC.
    local_timezone = timezone(timedelta(seconds=data["city"]["timezone"]))
    today = datetime.now(local_timezone).date()
    daily_temperatures = group_daily_temperatures(data["list"], local_timezone)
    days = []
    for day_offset in range(1, 6):
        date = today + timedelta(days=day_offset)
        temperatures = daily_temperatures.get(date)
        days.append((date, temperatures))
    display_city(city, days)


def main():
    display_header()
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        display_error(
            "Clé météo manquante",
            "Configure la variable OPENWEATHER_API_KEY, puis relance le programme.",
        )
        return

    for city in CITIES:
        try:
            data = get_forecasts(city, api_key)
            display_forecasts(city, data)
        except requests.HTTPError as error:
            # L'URL de l'erreur contient la clé : ne pas l'afficher.
            status = error.response.status_code
            message = "Le service météo n'a pas pu répondre. Réessaie plus tard."
            if status == 401:
                message = "Vérifie que ta clé d'API est valide et activée."
            elif status == 404:
                message = "Ville introuvable."
            display_error(f"{city.split(',')[0]} / HTTP {status}", message)
        except requests.RequestException:
            display_error(city.split(",")[0], "Impossible de contacter le service météo.")
        except (KeyError, TypeError, ValueError):
            display_error(city.split(",")[0], "Réponse météo invalide ou incomplète.")
    display_footer()


if __name__ == "__main__":
    main()
