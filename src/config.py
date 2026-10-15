# src/config.py
# Configuration for Addis Suk Bot

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    """Main configuration class."""

    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = field(default_factory=list)

    # Database
    DB_PATH: str = str(DATA_DIR / "addis_suk.db")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Premium Features
    BUYER_PREMIUM_PRICE: float = float(os.getenv("BUYER_PREMIUM_PRICE", "100"))
    SELLER_PREMIUM_PRICE: float = float(os.getenv("SELLER_PREMIUM_PRICE", "250"))
    FEATURED_LISTING_PRICE: float = float(os.getenv("FEATURED_LISTING_PRICE", "50"))
    VERIFIED_BADGE_PRICE: float = float(os.getenv("VERIFIED_BADGE_PRICE", "100"))
    PROMOTIONAL_BROADCAST_PRICE: float = float(os.getenv("PROMOTIONAL_BROADCAST_PRICE", "100"))
    BULK_DISCOUNT_FEATURE_PRICE: float = float(os.getenv("BULK_DISCOUNT_FEATURE_PRICE", "150"))

    # Limits
    FREE_SEARCH_LIMIT: int = int(os.getenv("FREE_SEARCH_LIMIT", "5"))
    FREE_ITEMS_LIMIT: int = int(os.getenv("FREE_ITEMS_LIMIT", "10"))
    PREMIUM_ALERTS_LIMIT: int = int(os.getenv("PREMIUM_ALERTS_LIMIT", "10"))
    PRICE_HISTORY_DAYS: int = int(os.getenv("PRICE_HISTORY_DAYS", "30"))

    # Payment Methods
    PAYMENT_METHODS: list[str] = field(default_factory=lambda: ["telebirr", "cbebirr", "chapa", "cash", "bank"])

    # Cities (Ethiopia)
    CITIES: dict[str, str] = field(default_factory=dict)

    # Sub-cities for Addis Ababa
    ADDIS_SUB_CITIES: list[str] = field(default_factory=list)

    # Default location (Addis Ababa)
    DEFAULT_LATITUDE: float = 9.0320
    DEFAULT_LONGITUDE: float = 38.7529

    # Search radius in km
    SEARCH_RADIUS_KM: float = float(os.getenv("SEARCH_RADIUS_KM", "10"))

    def __post_init__(self):
        if not self.ADMIN_IDS:
            admin_ids_str = os.getenv("ADMIN_IDS", "")
            self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

        self.CITIES = {
            "Addis Ababa": "አዲስ አበባ",
            "Bahir Dar": "ባህር ዳር",
            "Gondar": "ጎንደር",
            "Mekelle": "መቄል",
            "Hawassa": "strom",
            "Dire Dawa": "idir",
            "Jimma": "jimma",
            "Harar": "hara",
            "Debre Zeyit": "debre",
            "Adama": "adama",
        }

        self.ADDIS_SUB_CITIES = [
            "Bole", "Megenagna", "Piazza", "Gerji", "Sar Bet",
            "Summit", "Kazanchis", "Arada", "Gulele", "Kirkos"
        ]


def load_config() -> Config:
    """Load configuration."""
    config = Config()

    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required. Please set it in .env file.")

    return config


config = load_config()

# Export commonly used values
BOT_TOKEN = config.BOT_TOKEN
ADMIN_IDS = config.ADMIN_IDS
DB_PATH = config.DB_PATH