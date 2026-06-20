import sys
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add your project folder to Python's path so we can import your modules
sys.path.insert(0, "/opt/airflow/project")

from extract.extractor import extract_weather_data
from transform.transformer import transform_weather_data
from load.loader import load_weather_data


def run_extract(**context):
    df = extract_weather_data(latitude=6.45, longitude=3.40, past_days=7)
    if df is None:
        raise Exception("Extraction failed")
    # Push the data to XCom as JSON so the next task can use it
    context["ti"].xcom_push(key="raw_data", value=df.to_json())


def run_transform(**context):
    import pandas as pd
    raw_json = context["ti"].xcom_pull(key="raw_data", task_ids="extract_task")
    df_raw = pd.read_json(raw_json)

    df_transformed = transform_weather_data(
        df_raw,
        location_name="Lagos",
        latitude=6.45,
        longitude=3.40,
        timezone="Africa/Lagos"
    )
    if df_transformed is None:
        raise Exception("Transformation failed")

    context["ti"].xcom_push(key="transformed_data", value=df_transformed.to_json())


def run_load(**context):
    import pandas as pd
    transformed_json = context["ti"].xcom_pull(
        key="transformed_data", task_ids="transform_task"
    )
    df_transformed = pd.read_json(transformed_json)

    success = load_weather_data(
        df_transformed, db_path="/opt/airflow/project/weather_analytics.db"
    )
    if not success:
        raise Exception("Load failed")


default_args = {
    "owner": "moses",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_etl_pipeline",
    default_args=default_args,
    description="Daily ETL pipeline for Lagos weather data",
    schedule_interval="@daily",
    start_date=datetime(2026, 6, 1),
    catchup=False,
    tags=["weather", "etl", "capstone"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_task",
        python_callable=run_extract,
    )

    transform_task = PythonOperator(
        task_id="transform_task",
        python_callable=run_transform,
    )

    load_task = PythonOperator(
        task_id="load_task",
        python_callable=run_load,
    )

    extract_task >> transform_task >> load_task