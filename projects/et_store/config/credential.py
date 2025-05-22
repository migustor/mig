import os
from dotenv import load_dotenv

load_dotenv()  # Если у вас есть .env, откуда берутся переменные окружения

CREDENTIALS = {
    "e2e": {
        "username": os.getenv("ET_STORE_USERNAME", "e2e@mteam.md"),
        "password": os.getenv("ET_STORE_PASSWORD", "1NA0VRFE%Dgk6z*R")
    }
}