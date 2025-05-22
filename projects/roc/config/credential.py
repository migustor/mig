import os
from dotenv import load_dotenv

load_dotenv()  # Если у вас есть .env, откуда берутся переменные окружения

CREDENTIALS = {
    "ar": {
        "username": os.getenv("AR_USERNAME", "alexandru.rabdau@mteam.md"),
        "password": os.getenv("AR_PASSWORD", "12")
    },
    "ml": {
        "username": os.getenv("ML_USERNAME", "maxim.lupan@mteam.md"),
        "password": os.getenv("ML_PASSWORD", "12")
    },
    "vb": {
        "username": os.getenv("VB_USERNAME", "valeriu.bistritchi@mteam.md"),
        "password": os.getenv("VB_PASSWORD", "12")
    },
    "vm": {
        "username": os.getenv("VM_USERNAME", "victor.moisei@mteam.md"),
        "password": os.getenv("VM_PASSWORD", "12")
    },
    "dd": {
        "username": os.getenv("DD_USERNAME", "dmitri.dubkovetki@mteam.md"),
        "password": os.getenv("DD_PASSWORD", "12")
    }
}