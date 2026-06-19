
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_weather_data(latitude=6.4541, longitude=3.3947, past_days=7):
    """
    Extracts weather data from Open-Meteo API.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        past_days: Number of past days to fetch

    Returns:
        DataFrame of raw weather data or None if extraction fails
    """
    logger.info(f"Starting extraction for lat={latitude}, lon={longitude}")

    try:

        url = "https://api.open-meteo.com/v1/forecast?latitude=6.4541&longitude=3.3947&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,wind_speed_10m_max,uv_index_max,rain_sum,weather_code,precipitation_sum,wind_gusts_10m_max,wind_direction_10m_dominant,sunrise,sunset,daylight_duration&past_days=7"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            logger.error(f"API returned status code {response.status_code}")
            return None

        data = response.json()

        if "daily" not in data:
            logger.error("API response missing daily key")
            return None

        df_raw = pd.DataFrame(data["daily"])
        logger.info(f"Extraction successful! {len(df_raw)} rows retrieved.")
        return df_raw

    except requests.exceptions.ConnectionError:
        logger.error("Connection error - check your internet connection")
        return None
    except requests.exceptions.Timeout:
        logger.error("Request timed out - API took too long to respond")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        return None
