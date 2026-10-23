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


@dataclass
class Config:
    """Main configuration class."""

    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = field(default_factory=list)

    # Paths
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    DATA_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    LOG_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")

    # Database
    DB_PATH: str = ""

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
        self.DB_PATH = str(self.DATA_DIR / "addis_suk.db")

        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        if not self.ADMIN_IDS:
            admin_ids_str = os.getenv("ADMIN_IDS", "")
            self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

        self.CITIES = {
            "Addis Ababa": "አዲስ አበባ",
            "Bahir Dar": "ባህር ዳር",
            "Gondar": "ጎንደር",
            "Mekelle": "መቀሌ",
            "Hawassa": "ሀዋሳ",
            "Dire Dawa": "ድሬዳዋ",
            "Jimma": "ጀምማ",
            "Harar": "ሐረር",
            "Debre Zeyit": "ደብረዘይት",
            "Adama": "አዳማ",
        }

        self.ADDIS_SUB_CITIES = [
            "Addis Ketema", "Merkato","Akaki Kaliti","Lemi Kura","Kolfe Keranio", "Lideta", "Nifas Silk-Lafto", "Yeka", "Bole", "Mexico", "Megenagna", "Piazza", "Gerji", "Sar Bet",
            "Summit", "Kazanchis", "Arada", "Gulele", "Kirkos"
        ]

        # Approximate city centers (lat, lon) for manual location selection
        self.CITY_COORDS: dict[str, tuple[float, float]] = {
            "Addis Ababa": (9.0320, 38.7529),
            "Bahir Dar": (11.5936, 37.3908),
            "Gondar": (12.6096, 37.4663),
            "Mekelle": (13.4967, 39.4753),
            "Hawassa": (7.0621, 38.4764),
            "Dire Dawa": (9.5931, 41.8661),
            "Jimma": (7.6761, 36.8339),
            "Harar": (9.3114, 42.1281),
            "Debre Zeyit": (8.7378, 39.0686),
            "Adama": (8.5404, 39.2700),
        }

        # Approximate Addis Ababa neighborhood centers (lat, lon)
        self.ADDIS_SUBCITY_COORDS: dict[str, tuple[float, float]] = {
            "Addis Ketema": (9.0333, 38.7333),
            "Merkato": (9.0350, 38.7380),
            "Akaki Kaliti": (8.8800, 38.7500),
            "Lemi Kura": (8.9500, 38.8500),
            "Kolfe Keranio": (9.0100, 38.7100),
            "Lideta": (9.0200, 38.7400),
            "Nifas Silk-Lafto": (8.9900, 38.7300),
            "Yeka": (9.0333, 38.8000),
            "Bole": (9.0050, 38.7900),
            "Mexico": (9.0060, 38.7613),
            "Megenagna": (9.0250, 38.8010),
            "Piazza": (9.0350, 38.7540),
            "Gerji": (9.0100, 38.8200),
            "Sar Bet": (9.0180, 38.7530),
            "Summit": (8.9858, 38.8199),
            "Kazanchis": (9.0167, 38.7667),
            "Arada": (9.0367, 38.7578),
            "Gulele": (9.0500, 38.7300),
            "Kirkos": (9.0100, 38.7500),
        }


def load_config() -> Config:
    """Load configuration."""
    config = Config()

    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required. Please set it in .env file.")

    return config


try:
    config = load_config()
except ValueError:
    config = None

# Export commonly used values (set after load_config() is called)
BOT_TOKEN = config.BOT_TOKEN if config else ""
ADMIN_IDS = config.ADMIN_IDS if config else []
DB_PATH = str(DATA_DIR / "addis_suk.db")