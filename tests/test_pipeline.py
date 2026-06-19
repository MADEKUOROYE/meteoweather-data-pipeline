
import sys
import os
import pandas as pd
import sqlite3
import pytest

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from transform.transformer import transform_weather_data
from load.loader import load_weather_data


def sample_raw_df():
    """Creates a small sample DataFrame mimicking API output."""
    return pd.DataFrame({
        "time": ["2026-06-10", "2026-06-11", "2026-06-12"],
        "temperature_2m_max": [31.2, 30.5, 29.8],
        "temperature_2m_min": [24.1, 23.8, 24.5],
        "apparent_temperature_max": [35.0, 34.2, 33.8],
        "apparent_temperature_min": [26.0, 25.5, 26.2],
        "wind_speed_10m_max": [15.2, 12.8, 14.5],
        "uv_index_max": [10.0, 9.5, 11.0],
        "rain_sum": [0.0, 2.5, 0.0],
        "weather_code": [1, 61, 1],
        "precipitation_sum": [0.0, 2.5, 0.0],
        "wind_gusts_10m_max": [28.0, 25.0, 27.0],
        "wind_direction_10m_dominant": [180, 200, 190],
        "sunrise": ["2026-06-10T06:30", "2026-06-11T06:31", "2026-06-12T06:31"],
        "sunset": ["2026-06-10T18:45", "2026-06-11T18:44", "2026-06-12T18:44"],
        "daylight_duration": [43800.0, 43740.0, 43740.0]
    })


# =========================================
# TRANSFORM TESTS
# =========================================

def test_transform_returns_dataframe():
    df = transform_weather_data(
        sample_raw_df(), "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    assert isinstance(df, pd.DataFrame)


def test_transform_time_is_datetime():
    df = transform_weather_data(
        sample_raw_df(), "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    assert pd.api.types.is_datetime64_any_dtype(df["time"])


def test_transform_derived_columns_exist():
    df = transform_weather_data(
        sample_raw_df(), "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    for col in ["year", "month", "month_name", "day_of_week",
                "week_number", "daylight_hours"]:
        assert col in df.columns


def test_transform_location_metadata_added():
    df = transform_weather_data(
        sample_raw_df(), "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    assert df["location_name"].iloc[0] == "Lagos"
    assert df["latitude"].iloc[0] == 6.45


def test_transform_removes_duplicates():
    raw = sample_raw_df()
    raw_dup = pd.concat([raw, raw]).reset_index(drop=True)
    df = transform_weather_data(
        raw_dup, "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    assert len(df) == len(raw)


def test_transform_returns_none_for_bad_input():
    bad_df = pd.DataFrame({"time": ["2026-06-10"], "junk": [1]})
    result = transform_weather_data(
        bad_df, "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    assert result is None


# =========================================
# LOAD TESTS
# =========================================

def test_load_creates_all_tables(tmp_path):
    df = transform_weather_data(
        sample_raw_df(), "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    db_file = tmp_path / "test.db"
    load_weather_data(df, db_path=str(db_file))

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    for table in ["dim_date", "dim_location",
                  "dim_weather_condition", "fact_weather"]:
        assert table in tables


def test_load_fact_table_row_count(tmp_path):
    df = transform_weather_data(
        sample_raw_df(), "Lagos", 6.45, 3.40, "Africa/Lagos"
    )
    db_file = tmp_path / "test2.db"
    load_weather_data(df, db_path=str(db_file))

    conn = sqlite3.connect(str(db_file))
    count = pd.read_sql("SELECT COUNT(*) as n FROM fact_weather", conn)
    conn.close()

    assert count["n"][0] == 3
