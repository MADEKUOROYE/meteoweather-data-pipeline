
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from extract.extractor import extract_weather_data
from transform.transformer import transform_weather_data
from load.loader import load_weather_data

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class WeatherPipeline:
    """
    A reusable class-based ETL pipeline for weather data.
    """

    def __init__(self, latitude, longitude, location_name,
                 timezone, db_path="weather_analytics.db", past_days=7):
        self.latitude = latitude
        self.longitude = longitude
        self.location = location_name
        self.timezone = timezone
        self.db_path = db_path
        self.past_days = past_days

    def run(self):
        """Runs the full ETL pipeline."""
        logger.info("========== PIPELINE STARTED ==========")

        # Step 1: Extract
        raw_df = extract_weather_data(
            self.latitude, self.longitude, self.past_days
        )
        if raw_df is None:
            logger.error("Extraction failed - pipeline stopped")
            return False

        # Step 2: Transform
        transformed_df = transform_weather_data(
            raw_df, self.location,
            self.latitude, self.longitude, self.timezone
        )
        if transformed_df is None:
            logger.error("Transformation failed - pipeline stopped")
            return False

        # Step 3: Load
        success = load_weather_data(transformed_df, self.db_path)
        if not success:
            logger.error("Load failed - pipeline stopped")
            return False

        logger.info("========== PIPELINE COMPLETED ==========")
        return True


if __name__ == "__main__":
    pipeline = WeatherPipeline(
        latitude=6.45,
        longitude=3.40,
        location_name="Lagos",
        timezone="Africa/Lagos",
        db_path="weather_analytics.db",
        past_days=7
    )
    pipeline.run()
