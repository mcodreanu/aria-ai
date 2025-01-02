import os
from dotenv import load_dotenv

load_dotenv()

# User Configuration
USER = os.getenv("USER")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME")

# Email Configuration
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_URL = os.getenv("SMTP_URL")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_FETCH_API_KEY = os.getenv("NEWS_FETCH_API_KEY")
WEATHER_FETCH_API_KEY = os.getenv("WEATHER_FETCH_API_KEY")

# API URLs
IP_ADDR_API_URL = os.getenv("IP_ADDR_API_URL", "https://api.ipify.org")
NEWS_FETCH_API_URL = os.getenv("NEWS_FETCH_API_URL", "https://newsapi.org/v2/top-headlines")
WEATHER_FETCH_API_URL = os.getenv("WEATHER_FETCH_API_URL", "http://api.openweathermap.org/data/2.5/weather")

# Database Configuration
DB_PARAMS = {
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST", "localhost"),
    'port': os.getenv("DB_PORT", "5432")
}