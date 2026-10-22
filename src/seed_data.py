# src/seed_data.py
# Demonstration data seeder for Addis Suk Bot

from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# City coordinates for Addis Suk Bot
CITY_LOCATIONS: Dict[str, Tuple[float, float]] = {
    "Addis Ababa": (9.0320, 38.7529),
    "Bahir Dar": (11.5961, 37.3914),
    "Gondar": (12.6121, 37.2334),
    "Mekelle": (13.5052, 39.4856),
    "Hawassa": (6.7964, 38.4895),
    "Dire Dawa": (9.5940, 41.9615),
    "Jimma": (7.6710, 38.4896),
    "Harar": (9.3086, 42.0756),
    "Adama": (8.5393, 39.2258),
}

# Demonstration categories
SEED_CATEGORIES = [
    (1, "Vegetables", "የአቲካል ወተት", "🥦", 1),
    (2, "Fruits", "ፍራፍሬ", "🍎", 2),
    (3, "Meat", "ሥጋ", "🥩", 3),
    (4, "Dairy", "አሟራ ምርት", "🥛", 4),
    (5, "Bakery", "እንቁላል", "🍞", 5),
    (6, "Coffee", "ቡና", "☕", 6),
    (7, "Household", "ቤት መሰረቻዊ", "🧴", 7),
]

# Demonstration shops in different cities
SEED_SHOPS: List[Dict[str, Any]] = [
    {
        "shop_name": "Mercato Fresh Produce",
        "address": "Mercato, Addis Ababa",
        "phone": "0911123456",
        "city": "Addis Ababa",
        "sub_city": "Lideta",
        "latitude": 9.0350,
        "longitude": 38.7489,
        "items": [
            ("Tomato", "መብሃሪ", 12.5, "kg", 1, "2024-01-15"),
            ("Onion", "ድንሽ", 8.0, "kg", 1, "2024-01-10"),
            ("Potato", "ድሩስ", 6.5, "kg", 1, "2024-02-01"),
        ],
    },
    {
        "shop_name": "Bahir Dar Organics",
        "address": "Giyerga, Bahir Dar",
        "phone": "0912233445",
        "city": "Bahir Dar",
        "sub_city": "",
        "latitude": 11.5980,
        "longitude": 37.3905,
        "items": [
            ("Tomato", "መብሃሪ", 15.0, "kg", 1, "2024-01-20"),
            ("Lettuce", "ሃስላ", 25.0, "piece", 1, "2024-01-15"),
        ],
    },
    {
        "shop_name": "Gondar Meat House",
        "address": "Gondar University Area",
        "phone": "0913344556",
        "city": "Gondar",
        "sub_city": "",
        "latitude": 12.6110,
        "longitude": 37.2330,
        "items": [
            ("Beef", "ሥጋ (በእንውဃ)", 220.0, "kg", 3, "2024-01-25"),
            ("Chicken", "ዝርዝር", 180.0, "kg", 3, "2024-01-25"),
        ],
    },
    {
        "shop_name": "Hawassa Dairy Farm",
        "address": "Lake Awassa Resort Area",
        "phone": "0914455667",
        "city": "Hawassa",
        "sub_city": "",
        "latitude": 6.7950,
        "longitude": 38.4910,
        "items": [
            ("Milk", "ወተት", 35.0, "liter", 4, "2024-02-05"),
            ("Yogurt", "የነጸ አማራዊ", 25.0, "cup", 4, "2024-02-05"),
            ("Butter", "በተኬው", 180.0, "pack", 4, "2024-02-05"),
        ],
    },
    {
        "shop_name": "Mekelle Coffee House",
        "address": "Hadinet, Mekelle",
        "phone": "0915566778",
        "city": "Mekelle",
        "sub_city": "",
        "latitude": 13.5060,
        "longitude": 39.4865,
        "items": [
            ("Coffee Beans", "ቡና ድሮ", 450.0, "kg", 6, "2024-01-30"),
            ("Tea", "ሽა჈", 180.0, "kg", 7, "2024-01-30"),
        ],
    },
    {
        "shop_name": "Dire Dawa Fruits",
        "address": "Kebur Kubsa, Dire Dawa",
        "phone": "0916677889",
        "city": "Dire Dawa",
        "sub_city": "",
        "latitude": 9.5930,
        "longitude": 41.9620,
        "items": [
            ("Banana", "በንለን", 28.0, "kg", 2, None),
            ("Mango", "መንግት", 85.0, "kg", 2, None),
            ("Papaya", "ፓጣኛ", 35.0, "piece", 2, None),
        ],
    },
    {
        "shop_name": "Jimma Bakery & Cafe",
        "address": "Jimma University Campus",
        "phone": "0917788990",
        "city": "Jimma",
        "sub_city": "",
        "latitude": 7.6700,
        "longitude": 38.4900,
        "items": [
            ("Bread", "እንቁላል", 18.0, "loaf", 5, None),
            ("Cookies", "ኩኪስ", 45.0, "pack", 5, None),
            ("Cake", "ኬክ", 150.0, "piece", 5, None),
        ],
    },
    {
        "shop_name": "Harar Household Goods",
        "address": "Harar Paga, Harar",
        "phone": "0918899000",
        "city": "Harar",
        "sub_city": "",
        "latitude": 9.3090,
        "longitude": 42.0800,
        "items": [
            ("Soap", "ሱፍና", 12.0, "piece", 7, None),
            ("Salt", "ጨው", 8.0, "pack", 7, None),
            ("Oil", "ባቢኩል", 220.0, "liter", 7, None),
        ],
    },
    {
        "shop_name": "Adama Central Market",
        "address": "Adama Main Market",
        "phone": "0919900111",
        "city": "Adama",
        "sub_city": "",
        "latitude": 8.5380,
        "longitude": 39.2260,
        "items": [
            ("Onion", "ድንሽ", 7.5, "kg", 1, None),
            ("Garlic", "ስንስምን", 90.0, "kg", 1, None),
            ("Chicken", "ዝርዝር", 175.0, "kg", 3, None),
            ("Eggs", "እንደር", 22.0, "dozen", 3, None),
        ],
    },
    {
        "shop_name": "Addis Suk Premium Market",
        "address": "Bole, Addis Ababa",
        "phone": "0920011223",
        "city": "Addis Ababa",
        "sub_city": "Bole",
        "latitude": 9.0500,
        "longitude": 38.7620,
        "items": [
            ("Avocado", "አቕድን", 120.0, "kg", 2, None),
            ("Spinach", "አስፋላጥ", 30.0, "bunch", 1, None),
            ("Beef", "ሥጋ (በእንውဃ)", 240.0, "kg", 3, None),
            ("Coffee Beans", "ቡና ድሮ", 520.0, "kg", 6, None),
            ("Milk", "ወተት", 42.0, "liter", 4, None),
        ],
    },
]


async def seed_database(db) -> bool:
    """Seed the database with demonstration data. Idempotent."""
    try:
        # Seed categories
        for cat_id, name_en, name_am, emoji, order in SEED_CATEGORIES:
            await db.execute(
                """
                INSERT OR IGNORE INTO categories (id, name_en, name_am, emoji, display_order, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (cat_id, name_en, name_am, emoji, order)
            )

        # Check if shops already seeded
        existing = await db.fetchone("SELECT COUNT(*) as cnt FROM sellers WHERE status = 'approved'")
        if existing and existing['cnt'] > 0:
            logger.info("Demo data already seeded — skipping")
            return False

        # Seed shops and items
        for shop in SEED_SHOPS:
            # Use a fake user_id for demo shops (or create users)
            cursor = await db.execute(
                """
                INSERT INTO sellers
                (user_id, shop_name, address, phone, city, sub_city, latitude, longitude, status, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'approved', 1)
                """,
                (
                    9999,  # demo user_id placeholder — real shops tied to real users
                    shop["shop_name"],
                    shop["address"],
                    shop["phone"],
                    shop["city"],
                    shop["sub_city"],
                    shop["latitude"],
                    shop["longitude"],
                )
            )
            seller_id = cursor.lastrowid

            for name_en, name_am, price, unit, cat_id, recorded_at in shop["items"]:
                cursor = await db.execute(
                    """
                    INSERT INTO items (seller_id, category_id, name_en, name_am, price, unit, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'approved')
                    """,
                    (seller_id, cat_id, name_en, name_am, price, unit)
                )
                item_id = cursor.lastrowid
                await db.execute(
                    "INSERT INTO price_history (item_id, price, recorded_at) VALUES (?, ?, ?)",
                    (item_id, price, recorded_at or datetime.utcnow().isoformat())
                )

        logger.info("Demo data seeded successfully — %d shops, %d items",
                     len(SEED_SHOPS), sum(len(s["items"]) for s in SEED_SHOPS))
        return True

    except Exception as e:
        logger.exception(f"Error seeding database: {e}")
        return False
