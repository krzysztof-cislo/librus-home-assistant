"""Constants for the Librus integration."""

from datetime import timedelta

DOMAIN = "librus"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Homework sensor
SENSOR_HOMEWORK_KEY = "homework"
SENSOR_HOMEWORK_NAME = "Librus Homework"

# Update interval for homework data refresh
DEFAULT_UPDATE_INTERVAL = timedelta(hours=1)

# Date filtering window
HOMEWORK_PAST_DAYS = 7
HOMEWORK_FUTURE_DAYS = 14

# Service names
SERVICE_REFRESH_HOMEWORK = "refresh_homework"

# Platforms
PLATFORMS = ["sensor"]
