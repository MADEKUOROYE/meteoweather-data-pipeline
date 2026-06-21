-- ============================================
-- Weather Data Pipeline: Star Schema
-- ============================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    date TEXT,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    day_of_week TEXT,
    week_number INTEGER
);

CREATE TABLE IF NOT EXISTS dim_location (
    location_id INTEGER PRIMARY KEY,
    location_name TEXT,
    latitude REAL,
    longitude REAL,
    timezone TEXT
);

CREATE TABLE IF NOT EXISTS dim_weather_condition (
    condition_id INTEGER PRIMARY KEY,
    weather_code INTEGER,
    condition_description TEXT
);

CREATE TABLE IF NOT EXISTS fact_weather (
    fact_id INTEGER PRIMARY KEY,
    date_id INTEGER,
    location_id INTEGER,
    condition_id INTEGER,
    temperature_2m_max REAL,
    temperature_2m_min REAL,
    apparent_temperature_max REAL,
    apparent_temperature_min REAL,
    precipitation_sum REAL,
    rain_sum REAL,
    wind_speed_10m_max REAL,
    wind_gusts_10m_max REAL,
    wind_direction_10m_dominant INTEGER,
    uv_index_max REAL,
    daylight_hours REAL,
    sunrise TEXT,
    sunset TEXT,
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY (condition_id) REFERENCES dim_weather_condition(condition_id)
);
