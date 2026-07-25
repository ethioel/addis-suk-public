# src/config.py
# Public Wrapper Config Only

import os
from dotenv import load_dotenv

load_dotenv()

# === REQUIRED ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN required")

ADMIN_IDS = os.getenv("ADMIN_IDS", "")
ADMINS = [int(id.strip()) for id in ADMIN_IDS.split(",") if id.strip()]

# === PUBLIC WRAPPER ===
VERSION = "1.0.0-public"
MODE = "public"  # Limited functionality

# === EXTERNAL DEPENDENCY ===
# Core logic is loaded from compiled module
# This prevents source code exposure
