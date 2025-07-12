import datetime, json, requests, os
from caldav.davclient import get_davclient
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask


app = Flask(__name__)


def fetch_events(calendar_url: str) -> list[dict[str, str]]:
    client = get_davclient(check_config_file=False)
    shared_calendar = client.calendar(url=calendar_url)

    events = shared_calendar.search(
        event=True,
        start=datetime.now(),
        end=datetime.now() + relativedelta(months=6),
        expand=True,
    )

    results = []
    for event in events:
        for component in event.icalendar_instance.walk():
            if component.name != "VEVENT":
                continue

            results.append(format_event(component))

    return results


def format_event(component) -> dict[str, str]:
    event = {
        "summary": component.get("summary"),
        "start": component.start.strftime("%Y-%m-%d %H:%M"),
    }

    if component.end:
        event["end"] = component.end.strftime("%Y-%m-%d %H:%M")

    return event


def fetch_weather_data(apikey: str, latitude: str, longitude: str):
    url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid={apikey}&lang=en&units=standard&exclude=minutely,hourly"'
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(f"unexpected response status from OpenWeatherMap: {response.status_code}")
    
    return format_weather_data(response.json())


def format_weather_data(data):
    return {
        "current": {
            "sunrise": data["current"]["sunrise"],
            "sunset": data["current"]["sunset"],
            "temp": data["current"]["temp"],
            "feels_like": data["current"]["feels_like"],
            "pressure": data["current"]["pressure"],
            "humidity": data["current"]["humidity"],
            "dew_point": data["current"]["dew_point"],
            "clouds": data["current"]["clouds"],
            "uvi": data["current"]["uvi"],
            "visibility": data["current"]["visibility"],
            "wind_speed": data["current"].get("wind_speed", 0),
            "wind_gust": data["current"].get("wind_gust", 0),
            "wind_deg": data["current"].get("wind_deg", 0),
            "rain_1h": data["current"].get("rain_1h", 0),
            "snow_1h": data["current"].get("snow_1h", 0),
            "weather": data["current"]["weather"],
        },
        "daily": [
            {
                "dt": daily["dt"],
                "sunrise": daily["sunrise"],
                "sunset": daily["sunset"],
                "moonrise": daily["moonrise"],
                "moonset": daily["moonset"],
                "moon_phase": daily["moon_phase"],
                "temp": daily["temp"],
                "feels_like": daily["feels_like"],
                "pressure": daily["pressure"],
                "humidity": daily["humidity"],
                "dew_point": daily["dew_point"],
                "clouds": daily["clouds"],
                "uvi": daily["uvi"],
                "visibility": daily.get("visibility", 0),
                "wind_speed": daily.get("wind_speed", 0),
                "wind_gust": daily.get("wind_gust", 0),
                "wind_deg": daily.get("wind_deg", 0),
                "pop": daily.get("pop", 0),
                "rain": daily.get("rain", 0),
                "snow": daily.get("snow", 0),
                "weather": daily["weather"],
            } for daily in data["daily"]
        ],
        "alerts": data.get("alerts", []),
    }


def require_env_str(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"{name} environment variable missing")
    
    return value


@app.get("/api/combined")
def api_combined():
    events = []
    weather_data = {}

    try:
        events = fetch_events("kevin/kevin-shared")
    except Exception as e:
        app.logger.warning("could not fetch calendar events: %s", e)

    try:
        weather_data = fetch_weather_data(
            apikey=require_env_str("OWM_API_KEY"),
            latitude=require_env_str("LATITUDE"),
            longitude=require_env_str("LONGITUDE"),
        )
    except Exception as e:
        app.logger.warning("could not fetch weather data: %s", e)

    return {
        "events": events,
        "weather_data": weather_data,
    }


#def main():
#    events = fetch_events("kevin/kevin-shared")
#    print(json.dumps(events, indent=2))
#
#    weather_data = fetch_weather_data(
#        apikey=require_env_str("OWM_API_KEY"),
#        latitude=require_env_str("LATITUDE"),
#        longitude=require_env_str("LONGITUDE"),
#    )
#    print(json.dumps(weather_data, indent=2))
#
#
#if __name__ == "__main__":
#    main()
