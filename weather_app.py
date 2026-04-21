import tkinter as tk
import requests

# Dependency: pip install requests (see requirements.txt)

# WMO Weather interpretation codes -> descriptions
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ slight hail", 99: "Thunderstorm w/ heavy hail",
}


def search_weather(city_name):
    """Fetch current weather for a city using Open-Meteo (free, no API key)."""
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city_name, "count": 1},
        timeout=10,
    )
    resp.raise_for_status()
    geo = resp.json()
    results = geo.get("results")
    if not results:
        raise ValueError(f"City '{city_name}' not found.")
    loc = results[0]

    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "current_weather": True,
            "hourly": "relative_humidity_2m",
            "timezone": "auto",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    weather = data["current_weather"]

    # Extract humidity for the current hour
    try:
        idx = data["hourly"]["time"].index(weather["time"])
        humidity = data["hourly"]["relative_humidity_2m"][idx]
    except (ValueError, KeyError, IndexError):
        humidity = None
    return {
        "city": f"{loc['name']}, {loc.get('country', '')}",
        "temp": weather["temperature"],
        "wind": weather["windspeed"],
        "code": weather["weathercode"],
        "humidity": humidity,
    }


def on_search(entry, label):
    city = entry.get().strip()[:100]  # Truncate to reasonable length
    if not city:
        return
    label.config(text="Searching...")
    label.update_idletasks()
    try:
        w = search_weather(city)
        desc = WMO_CODES.get(w["code"], "Unknown")
        hum = f"{w['humidity']} %" if w["humidity"] is not None else "N/A"
        label.config(
            text=f"{w['city']}\n\n"
                 f"{desc}\n"
                 f"🌡  {w['temp']} °C\n"
                 f"💨  {w['wind']} km/h\n"
                 f"💧  {hum}"
        )
    except ValueError as e:
        label.config(text=str(e))
    except requests.RequestException:
        label.config(text="Network error. Check your connection.")
    except Exception:
        label.config(text="Unexpected error. Please try again.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Weather App")
    root.resizable(False, False)
    root.minsize(400, 250)

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    entry = tk.Entry(frame, width=30, font=("Arial", 14))
    entry.pack(side=tk.LEFT, padx=(0, 8))
    entry.focus()

    btn = tk.Button(frame, text="Search", font=("Arial", 12),
                    command=lambda: on_search(entry, result))
    btn.pack(side=tk.LEFT)

    result = tk.Label(root, text="", font=("Arial", 16), pady=20)
    result.pack()

    entry.bind("<Return>", lambda e: on_search(entry, result))

    root.mainloop()
