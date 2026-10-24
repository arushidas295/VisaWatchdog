import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./visa_watchdog.db")
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-env")