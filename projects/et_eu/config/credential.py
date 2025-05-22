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
    },
    "ecommerce_sales": {
        "username": os.getenv("ECOMMERCE_SALES_USERNAME", "user144269@mteam.test"),
        "password": os.getenv("ECOMMERCE_SALES_PASSWORD", "12")
    },
    "ecommerce_manager": {
        "username": os.getenv("ECOMMERCE_MANAGER_USERNAME", "user139937@mteam.test"),
        "password": os.getenv("ECOMMERCE_MANAGER_PASSWORD", "12")
    }
}