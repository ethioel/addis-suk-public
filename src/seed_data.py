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

# Demonstration shops in different cities.
# Items reference categories by name (resolved from the seeded taxonomy in
# src/models/database.py, DEFAULT_CATEGORIES).
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
            ("Tomato", "ቲማቲም", 12.5, "kg", "Vegetables", "2024-01-15"),
            ("Onion", "ሽንኩርት", 8.0, "kg", "Vegetables", "2024-01-10"),
            ("Potato", "ድንች", 6.5, "kg", "Vegetables", "2024-02-01"),
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
            ("Tomato", "ቲማቲም", 15.0, "kg", "Vegetables", "2024-01-20"),
            ("Lettuce", "ሰላጣ", 25.0, "piece", "Vegetables", "2024-01-15"),
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
            ("Beef", "የበሬ ሥጋ", 220.0, "kg", "Meat & Poultry", "2024-01-25"),
            ("Chicken", "የዶሮ ሥጋ", 180.0, "kg", "Meat & Poultry", "2024-01-25"),
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
            ("Milk", "ወተት", 35.0, "liter", "Dairy & Eggs", "2024-02-05"),
            ("Yogurt", "እርጎ", 25.0, "cup", "Dairy & Eggs", "2024-02-05"),
            ("Butter", "ቅቤ", 180.0, "pack", "Dairy & Eggs", "2024-02-05"),
            ("Eggs", "እንቁላል", 22.0, "dozen", "Dairy & Eggs", "2024-02-05"),
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
            ("Coffee Beans", "የቡና ዘር", 450.0, "kg", "Coffee, Tea & Drinks", "2024-01-30"),
            ("Tea", "ሻይ", 180.0, "kg", "Coffee, Tea & Drinks", "2024-01-30"),
            ("Soda", "ሶዳ", 35.0, "piece", "Coffee, Tea & Drinks", None),
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
            ("Banana", "ሙዝ", 28.0, "kg", "Fruits", None),
            ("Mango", "ማንጎ", 85.0, "kg", "Fruits", None),
            ("Papaya", "ፓፒያ", 35.0, "piece", "Fruits", None),
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
            ("Bread", "ዳቦ", 18.0, "loaf", "Bakery & Injera", None),
            ("Injera", "እንጀራ", 30.0, "piece", "Bakery & Injera", None),
            ("Cake", "ኬክ", 150.0, "piece", "Bakery & Injera", None),
            ("Cookies", "ብስኩት", 45.0, "pack", "Snacks & Sweets", None),
        ],
    },
    {
        "shop_name": "Harar Market Goods",
        "address": "Harar Paga, Harar",
        "phone": "0918899000",
        "city": "Harar",
        "sub_city": "",
        "latitude": 9.3090,
        "longitude": 42.0800,
        "items": [
            ("Soap", "ሳሙና", 12.0, "piece", "Household & Care", None),
            ("Tissue", "ቲሸው", 60.0, "pack", "Household & Care", None),
            ("Berbere", "በርበሬ", 350.0, "kg", "Spices & Oil", None),
            ("Cooking Oil", "የምግብ ዘይት", 220.0, "liter", "Spices & Oil", None),
            ("Salt", "ጨው", 8.0, "pack", "Spices & Oil", None),
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
            ("Onion", "ሽንኩርት", 7.5, "kg", "Vegetables", None),
            ("Garlic", "ነጭ", 90.0, "kg", "Vegetables", None),
            ("Teff", "ጤፍ", 120.0, "kg", "Grains & Pulses", None),
            ("Shiro Powder", "ሽሮ ዱቄት", 260.0, "kg", "Grains & Pulses", None),
            ("Chicken", "የዶሮ ሥጋ", 175.0, "kg", "Meat & Poultry", None),
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
            ("Avocado", "አቮካዶ", 120.0, "kg", "Fruits", None),
            ("Collard Greens", "ጎመን", 30.0, "bunch", "Vegetables", None),
            ("Beef", "የበሬ ሥጋ", 240.0, "kg", "Meat & Poultry", None),
            ("Coffee Beans", "የቡና ዘር", 520.0, "kg", "Coffee, Tea & Drinks", None),
            ("Milk", "ወተት", 42.0, "liter", "Dairy & Eggs", None),
        ],
    },
]

# Corrects demo items seeded by older versions that used the old taxonomy
# (e.g. Eggs under Meat, Tea/Oil/Salt under Household). Idempotent.
ITEM_CATEGORY_FIXES: Dict[str, str] = {
    "Tea": "Coffee, Tea & Drinks",
    "Coffee Beans": "Coffee, Tea & Drinks",
    "Eggs": "Dairy & Eggs",
    "Milk": "Dairy & Eggs",
    "Yogurt": "Dairy & Eggs",
    "Butter": "Dairy & Eggs",
    "Oil": "Spices & Oil",
    "Salt": "Spices & Oil",
    "Cookies": "Snacks & Sweets",
    "Bread": "Bakery & Injera",
    "Chicken": "Meat & Poultry",
    "Beef": "Meat & Poultry",
    "Tomato": "Vegetables",
    "Onion": "Vegetables",
    "Potato": "Vegetables",
    "Lettuce": "Vegetables",
    "Garlic": "Vegetables",
    "Spinach": "Vegetables",
    "Banana": "Fruits",
    "Mango": "Fruits",
    "Papaya": "Fruits",
    "Avocado": "Fruits",
    "Soap": "Household & Care",
}


async def seed_database(db) -> bool:
    """Seed the database with demonstration data. Idempotent."""
    try:
        # Resolve category ids by name (categories are seeded by Database.init)
        cat_rows = await db.fetchall("SELECT id, name_en FROM categories")
        cat_ids: Dict[str, int] = {r['name_en']: r['id'] for r in cat_rows}

        # Re-group items from databases seeded with the old taxonomy
        for item_name, cat_name in ITEM_CATEGORY_FIXES.items():
            cid = cat_ids.get(cat_name)
            if cid:
                await db.execute(
                    "UPDATE items SET category_id = ? WHERE name_en = ? AND category_id != ?",
                    (cid, item_name, cid)
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

            for name_en, name_am, price, unit, cat_name, recorded_at in shop["items"]:
                cat_id = cat_ids.get(cat_name)
                if not cat_id:
                    logger.warning("Unknown category '%s' for item '%s' — skipped",
                                   cat_name, name_en)
                    continue
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
