import sys
import urllib.parse
import urllib.request
import json

API_KEY = "YOUR_API_KEY_HERE"  # Replace with your OpenWeatherMap API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    url = f"{BASE_URL}?q={urllib.parse.quote(city)}&appid={API_KEY}&units=metric"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"City '{city}' not found.")
        elif e.code == 401:
            print("Invalid API key. Please update API_KEY in weather.py")
        else:
            print(f"API error: {e.code}")
    except urllib.error.URLError:
        print("Network error. Check your internet connection.")
    except json.JSONDecodeError:
        print("Invalid response from API.")
    return None


def main():
    city = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Enter city: ").strip()

    if city in ("--help", "-h"):
        print("Usage: python weather.py [city]")
        return

    if not city or len(city) > 100:
        print("Invalid city name.")
        sys.exit(1)

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your API key in weather.py (replace YOUR_API_KEY_HERE).")
        sys.exit(1)

    data = get_weather(city)
    if not data:
        sys.exit(1)

    try:
        print(f"\nWeather in {data['name']}, {data['sys']['country']}:")
        print(f"  Temperature: {data['main']['temp']}°C")
        print(f"  Condition:   {data['weather'][0]['description'].capitalize()}")
        print(f"  Humidity:    {data['main']['humidity']}%")
    except (KeyError, IndexError, TypeError):
        print("Unexpected response format from API.")
        sys.exit(1)


if __name__ == "__main__":
    main()
