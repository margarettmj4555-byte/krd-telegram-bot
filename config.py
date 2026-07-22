"""
Configuration file for KRD Telegram Shopping Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token - Add your Telegram Bot Token here
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin ID - Add your Telegram User ID here
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Database
DB_NAME = "krd_bot.db"

# Store Information
STORE_NAME = "KRD Store"
STORE_CURRENCY = "USD"

# Pagination
PRODUCTS_PER_PAGE = 6
ORDERS_PER_PAGE = 5

# Admin Settings
ADMIN_PANEL_ENABLED = True
