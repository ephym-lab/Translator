from abc import ABC, abstractmethod
from datetime import datetime

import httpx

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


# WMO Weather Interpretation Codes → human-readable condition strings
# https://open-meteo.com/en/docs#weathervariables
WMO_WEATHER_CODES: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "icy fog",
    51: "light drizzle",
    53: "drizzle",
    55: "heavy drizzle",
    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "light snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "light rain showers",
    81: "rain showers",
    82: "violent rain showers",
    85: "snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with hail",
    99: "severe thunderstorm with hail",
}


class BaseFunctionService(ABC):
    """Abstract base class for voice assistant function execution."""

    should_exit: bool = False

    @abstractmethod
    async def get_weather(self, location: str) -> dict:
        """
        Fetch current weather conditions for a given location.

        Args:
            location: City or region name

        Returns:
            dict: {'condition': str, 'temp': float, 'location': str}
        """
        ...

    @abstractmethod
    def get_time(self) -> str:
        """
        Return the current local time as a formatted string.

        Returns:
            str: Time formatted as "HH:MM AM/PM"
        """
        ...

    @abstractmethod
    def end_session(self) -> None:
        """Signal the pipeline to exit after the current cycle."""
        ...


class VoiceFunctionService(BaseFunctionService):
    """
    Executes core voice assistant functions.

    Weather:
        Uses open-meteo.com — free, no API key required.
        Two-step: geocode location name → lat/lon, then fetch weather.

    Time:
        Returns the system's current local time via datetime.now().

    End Session:
        Sets the `should_exit` flag which the pipeline loop checks each cycle.
    """

    def __init__(self):
        self.should_exit: bool = False

    async def get_weather(self, location: str) -> dict:
        """
        Fetch real-time weather for a location using open-meteo.com.

        Args:
            location: City name (e.g. "Nairobi", "London", "New York")

        Returns:
            dict with keys: condition (str), temp (float), location (str)
                  Returns fallback values if the location cannot be geocoded
                  or the API is unreachable.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # --- Step 1: Geocode the location name ---
                geo_resp = await client.get(
                    settings.GEOCODING_API_BASE,
                    params={
                        "name": location,
                        "count": 1,
                        "language": "en",
                        "format": "json",
                    },
                )
                geo_data = geo_resp.json()

                if not geo_data.get("results"):
                    logger.warning(f"Location not found: '{location}'. Using fallback.")
                    return {"condition": "unavailable", "temp": 0, "location": location}

                result = geo_data["results"][0]
                lat = result["latitude"]
                lon = result["longitude"]
                resolved_name = result.get("name", location)
                logger.info(f"Geocoded '{location}' → {resolved_name} ({lat}, {lon})")

                # --- Step 2: Fetch current weather ---
                wx_resp = await client.get(
                    settings.WEATHER_API_BASE,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current_weather": True,
                        "temperature_unit": "celsius",
                    },
                )
                wx_data = wx_resp.json()
                current = wx_data.get("current_weather", {})
                code = int(current.get("weathercode", 0))
                temp = round(current.get("temperature", 0), 1)
                condition = WMO_WEATHER_CODES.get(code, "unknown conditions")

                logger.info(f"Weather → {resolved_name}: {condition}, {temp}°C (WMO code: {code})")
                return {
                    "condition": condition,
                    "temp": temp,
                    "location": resolved_name,
                }

        except httpx.TimeoutException:
            logger.error("Weather API request timed out.")
            return {"condition": "unavailable", "temp": 0, "location": location}
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return {"condition": "unavailable", "temp": 0, "location": location}

    def get_time(self) -> str:
        """
        Return the current local time formatted for speech.

        Returns:
            str: e.g. "03:45 PM"
        """
        return datetime.now().strftime("%I:%M %p")

    def end_session(self) -> None:
        """Set the exit flag to terminate the pipeline loop."""
        logger.info("Exit signal received. Ending session.")
        self.should_exit = True
