# Weather Data Pipeline

A production-style ETL/ELT data pipeline that extracts daily weather data for Lagos from the Open-Meteo API, transforms it, and loads it into a SQL database using a star schema — fully automated with Apache Airflow.

## Overview

This project was built as a Data Engineering capstone to demonstrate end-to-end pipeline design: API extraction, data validation, dimensional modeling, automated scheduling, logging, and testing.

## Architecture
Open-Meteo API → Extract → Transform → Load → SQLite (Star Schema)
↑
Orchestrated daily by Airflow

## Star Schema Design

**Fact Table**
- `fact_weather` — daily weather measurements (temperature, rainfall, wind, UV index, etc.), linked to dimensions via foreign keys.

**Dimension Tables**
- `dim_date` — calendar attributes (year, month, day of week, week number)
- `dim_location` — location metadata (name, latitude, longitude, timezone)
- `dim_weather_condition` — weather code descriptions (e.g. "Clear sky", "Thunderstorm")

The fact table holds quantitative measurements, while dimension tables provide descriptive context — enabling fast, flexible analytical queries (e.g. "average rainfall by month" or "temperature trends by day of week").

## Project Structure
weather_pipeline/
├── dags/                  # Airflow DAG
├── extract/               # API extraction logic
├── transform/             # Data cleaning & transformation
├── load/                  # Star schema loading logic
├── tests/                 # pytest unit tests
├── pipeline.py            # Class-based pipeline entry point
├── docker-compose.yaml    # Airflow infrastructure
└── requirements.txt

## Airflow DAG

The pipeline runs daily via Airflow with three sequential tasks:
extract_task → transform_task → load_task
Each task depends on the success of the previous one — if extraction fails, transformation and loading are skipped, preventing corrupted or partial data from reaching the database.

## Tech Stack

- **Python** — pandas, requests
- **SQLite** — star schema storage
- **Apache Airflow** — orchestration & daily scheduling
- **pytest** — unit testing
- **Docker** — Airflow infrastructure

## Running the Pipeline

**Standalone (without Airflow):**
```bash
pip install -r requirements.txt
python pipeline.py

** With Airflow (Docker):**

docker compose up airflow-init
docker compose up -d
pytest tests/
Author: Moses Adekuoroye
