
import sqlite3
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

def load_weather_data(df, db_path="weather_analytics.db"):
    """
    Loads transformed data into SQLite star schema.

    Args:
        df: Transformed DataFrame
        db_path: Path to SQLite database file

    Returns:
        True if load succeeded, False otherwise
    """
    logger.info(f"Starting load into database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)

        # Build dim_date
        dim_date = df[[
            "time", "year", "month", "month_name",
            "day_of_week", "week_number", "date"
        ]].drop_duplicates().reset_index(drop=True)
        dim_date.insert(0, "date_id", range(1, len(dim_date) + 1))

        # Build dim_location
        dim_location = df[[
            "location_name", "latitude", "longitude", "timezone"
        ]].drop_duplicates().reset_index(drop=True)
        dim_location.insert(0, "location_id", range(1, len(dim_location) + 1))

        # Build dim_weather_condition
        dim_weather_condition = df[["weather_code"]].drop_duplicates().reset_index(drop=True)
        dim_weather_condition["condition_description"] = (
            dim_weather_condition["weather_code"]
            .map(WEATHER_CODE_MAP).fillna("Unknown")
        )
        dim_weather_condition.insert(0, "condition_id",
                                     range(1, len(dim_weather_condition) + 1))

        # Build fact_weather
        fact_weather = df.merge(
            dim_date[["date_id", "date"]], on="date", how="left"
        )
        fact_weather["location_id"] = 1
        fact_weather = fact_weather.merge(
            dim_weather_condition[["condition_id", "weather_code"]],
            on="weather_code", how="left"
        )
        fact_weather = fact_weather[[
            "date_id", "location_id", "condition_id",
            "temperature_2m_max", "temperature_2m_min",
            "apparent_temperature_max", "apparent_temperature_min",
            "precipitation_sum", "rain_sum",
            "wind_speed_10m_max", "wind_gusts_10m_max",
            "wind_direction_10m_dominant", "uv_index_max",
            "daylight_hours", "sunrise", "sunset"
        ]].copy()
        fact_weather.insert(0, "fact_id", range(1, len(fact_weather) + 1))

        # Load all tables
        dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        dim_location.to_sql("dim_location", conn, if_exists="replace", index=False)
        dim_weather_condition.to_sql("dim_weather_condition", conn,
                                     if_exists="replace", index=False)
        fact_weather.to_sql("fact_weather", conn, if_exists="replace", index=False)

        conn.commit()
        conn.close()

        logger.info("All tables loaded successfully!")
        return True

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during load: {e}")
        return False
