
import pandas as pd
import logging

logger = logging.getLogger(__name__)

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail"
}

def transform_weather_data(df_raw, location_name, latitude, longitude, timezone):
    """
    Cleans and transforms raw weather data.

    Args:
        df_raw: Raw DataFrame from extraction
        location_name: Name of the location
        latitude: Location latitude
        longitude: Location longitude
        timezone: Timezone string

    Returns:
        Transformed DataFrame or None if transformation fails
    """
    logger.info("Starting transformation...")

    try:
        df = df_raw.copy()

        # Fix datetime columns
        df["time"] = pd.to_datetime(df["time"])
        df["sunrise"] = pd.to_datetime(df["sunrise"])
        df["sunset"] = pd.to_datetime(df["sunset"])

        # Add derived columns
        df["date"] = df["time"].dt.date
        df["year"] = df["time"].dt.year
        df["month"] = df["time"].dt.month
        df["month_name"] = df["time"].dt.month_name()
        df["day_of_week"] = df["time"].dt.day_name()
        df["week_number"] = df["time"].dt.isocalendar().week.astype(int)
        df["daylight_hours"] = (df["daylight_duration"] / 3600).round(2)

        # Add location metadata
        df["location_name"] = location_name
        df["latitude"] = latitude
        df["longitude"] = longitude
        df["timezone"] = timezone

        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {before - len(df)} duplicate rows")

        # Validate required columns
        required_columns = [
            "time", "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "wind_speed_10m_max"
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            logger.error(f"Missing required columns: {missing}")
            return None

        # Validate temperature range
        if df["temperature_2m_max"].max() > 60 or df["temperature_2m_min"].min() < -50:
            logger.warning("Temperature values outside expected range!")

        logger.info(f"Transformation successful! {len(df)} rows ready.")
        return df

    except Exception as e:
        logger.error(f"Unexpected error during transformation: {e}")
        return None
