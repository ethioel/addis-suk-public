# src/models/database.py
# Database schema and models for Addis Suk

import sqlite3
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class SellerStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class PriceStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


@dataclass
class User:
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    language: str = "en"
    role: UserRole = UserRole.BUYER
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    subscription_expires: Optional[datetime] = None
    city: Optional[str] = None
    sub_city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Seller:
    id: int
    user_id: int
    shop_name: str
    address: str
    phone: str
    city: str
    sub_city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: SellerStatus = SellerStatus.PENDING
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    subscription_expires: Optional[datetime] = None
    featured_until: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Category:
    id: int
    name_en: str
    name_am: str
    emoji: str
    display_order: int
    is_active: bool = True


@dataclass
class Item:
    id: int
    seller_id: int
    category_id: int
    name_en: str
    name_am: str
    price: float
    unit: str
    status: PriceStatus = PriceStatus.PENDING
    is_featured: bool = False
    bulk_price: Optional[float] = None
    bulk_quantity: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Favorite:
    id: int
    user_id: int
    item_id: int
    created_at: datetime = None


@dataclass
class PriceAlert:
    id: int
    user_id: int
    item_name: str
    target_price: float
    category_id: Optional[int]
    is_active: bool = True
    created_at: datetime = None


@dataclass
class PriceHistory:
    id: int
    item_id: int
    price: float
    recorded_at: datetime = None


@dataclass
class SearchLog:
    id: int
    user_id: Optional[int]
    query: str
    category_id: Optional[int]
    results_count: int
    created_at: datetime = None


class Database:
    # Default product categories (name_en, name_am, emoji), in logical
    # market-walk order: fresh produce -> animal products -> pantry staples
    # -> prepared staples -> beverages -> snacks -> non-food.
    DEFAULT_CATEGORIES = [
        ("Vegetables", "አትክልቶች", "🥦"),
        ("Fruits", "ፍራፍሬዎች", "🍎"),
        ("Meat & Poultry", "ሥጋና ዶሮ", "🥩"),
        ("Dairy & Eggs", "ወተትና እንቁላል", "🥛"),
        ("Grains & Pulses", "እህልና ጥራጥሬ", "🌾"),
        ("Spices & Oil", "ቅመምና ዘይት", "🌶️"),
        ("Bakery & Injera", "ዳቦና እንጀራ", "🍞"),
        ("Coffee, Tea & Drinks", "ቡና፣ ሻይና መጠጥ", "☕"),
        ("Snacks & Sweets", "መክሰስና ጣፋጭ", "🍪"),
        ("Household & Care", "የቤትና ግል ንጽህና", "🧴"),
    ]

    # Old -> new category names, migrated once during seeding so existing
    # databases keep their category ids (and therefore their items).
    CATEGORY_RENAMES = {
        "Meat": "Meat & Poultry",
        "Dairy": "Dairy & Eggs",
        "Grains": "Grains & Pulses",
        "Coffee": "Coffee, Tea & Drinks",
        "Bakery": "Bakery & Injera",
        "Household": "Household & Care",
    }

    def __init__(self, db_path: str = "data/addis_suk.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await self._migrate(db)
            await self._dedupe_categories(db)
            await self._seed_categories(db)
            await db.commit()

    @staticmethod
    async def _migrate(db):
        """Add columns missing in older databases."""
        cursor = await db.execute("PRAGMA table_info(sellers)")
        cols = {row[1] for row in await cursor.fetchall()}
        if "views" not in cols:
            await db.execute("ALTER TABLE sellers ADD COLUMN views INTEGER DEFAULT 0")
        if "contact_clicks" not in cols:
            await db.execute("ALTER TABLE sellers ADD COLUMN contact_clicks INTEGER DEFAULT 0")
        if "last_nudge_at" not in cols:
            await db.execute("ALTER TABLE sellers ADD COLUMN last_nudge_at TIMESTAMP")

        cursor = await db.execute("PRAGMA table_info(users)")
        ucols = {row[1] for row in await cursor.fetchall()}
        if "digest_enabled" not in ucols:
            await db.execute("ALTER TABLE users ADD COLUMN digest_enabled INTEGER DEFAULT 1")
        if "referrer_id" not in ucols:
            await db.execute("ALTER TABLE users ADD COLUMN referrer_id INTEGER")

    @staticmethod
    async def _dedupe_categories(db):
        """Merge duplicate category rows, keeping the lowest id per name_en."""
        dupes = await db.execute(
            """
            SELECT id, name_en FROM categories
            WHERE id NOT IN (SELECT MIN(id) FROM categories GROUP BY name_en)
            """
        )
        rows = await dupes.fetchall()
        if not rows:
            return
        for row in rows:
            dupe_id, name_en = row[0], row[1]
            keep = await db.execute(
                "SELECT MIN(id) FROM categories WHERE name_en = ?", (name_en,)
            )
            keep_id = (await keep.fetchone())[0]
            for table in ("items", "price_alerts", "search_logs"):
                await db.execute(
                    f"UPDATE {table} SET category_id = ? WHERE category_id = ?",
                    (keep_id, dupe_id)
                )
            await db.execute("DELETE FROM categories WHERE id = ?", (dupe_id,))

    async def _seed_categories(self, db):
        """Seed default categories and refresh names/emoji/order when the
        taxonomy changes. Renames preserve category ids so items stay grouped."""
        for old_name, new_name in self.CATEGORY_RENAMES.items():
            target = await db.execute(
                "SELECT 1 FROM categories WHERE name_en = ?", (new_name,)
            )
            if await target.fetchone():
                continue
            await db.execute(
                "UPDATE categories SET name_en = ? WHERE name_en = ?",
                (new_name, old_name)
            )

        for order, (name_en, name_am, emoji) in enumerate(self.DEFAULT_CATEGORIES):
            existing = await db.execute(
                "SELECT id FROM categories WHERE name_en = ?", (name_en,)
            )
            row = await existing.fetchone()
            if row:
                await db.execute(
                    "UPDATE categories SET name_am = ?, emoji = ?, display_order = ?, "
                    "is_active = 1 WHERE id = ?",
                    (name_am, emoji, order, row[0])
                )
            else:
                await db.execute(
                    "INSERT INTO categories (name_en, name_am, emoji, display_order) "
                    "VALUES (?, ?, ?, ?)",
                    (name_en, name_am, emoji, order)
                )

    async def execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor

    async def fetchone(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            return await cursor.fetchone()

    async def fetchall(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            return await cursor.fetchall()


SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    language TEXT DEFAULT '',
    role TEXT DEFAULT 'buyer',
    subscription_tier TEXT DEFAULT 'free',
    subscription_expires TIMESTAMP,
    city TEXT,
    sub_city TEXT,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);

-- Sellers table
CREATE TABLE IF NOT EXISTS sellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shop_name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    city TEXT NOT NULL,
    sub_city TEXT,
    latitude REAL,
    longitude REAL,
    status TEXT DEFAULT 'pending',
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    subscription_tier TEXT DEFAULT 'free',
    subscription_expires TIMESTAMP,
    featured_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sellers_user_id ON sellers(user_id);
CREATE INDEX IF NOT EXISTS idx_sellers_status ON sellers(status);
CREATE INDEX IF NOT EXISTS idx_sellers_city ON sellers(city);
CREATE INDEX IF NOT EXISTS idx_sellers_location ON sellers(latitude, longitude);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_en TEXT NOT NULL UNIQUE,
    name_am TEXT NOT NULL,
    emoji TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL REFERENCES sellers(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name_en TEXT NOT NULL,
    name_am TEXT NOT NULL,
    price REAL NOT NULL,
    unit TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    is_featured BOOLEAN DEFAULT FALSE,
    bulk_price REAL,
    bulk_quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_seller_id ON items(seller_id);
CREATE INDEX IF NOT EXISTS idx_items_category_id ON items(category_id);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_name_en ON items(name_en);
CREATE INDEX IF NOT EXISTS idx_items_name_am ON items(name_am);
CREATE INDEX IF NOT EXISTS idx_items_featured ON items(is_featured);

-- Favorites table (Premium feature)
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);

-- Price alerts table (Premium feature)
CREATE TABLE IF NOT EXISTS price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    target_price REAL NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts(is_active);

-- Price history table (Premium feature)
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    price REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_price_history_item_id ON price_history(item_id);
CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at);

-- Search logs table
CREATE TABLE IF NOT EXISTS search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_logs_user_id ON search_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs(created_at);

-- Admin actions log
CREATE TABLE IF NOT EXISTS admin_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL REFERENCES users(id),
    action_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Broadcast messages log
CREATE TABLE IF NOT EXISTS broadcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments/Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type TEXT NOT NULL, -- 'buyer_premium', 'seller_premium', 'featured_listing', 'verified_badge', 'broadcast', 'bulk_discount'
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'ETB',
    payment_method TEXT,
    payment_reference TEXT,
    status TEXT DEFAULT 'pending',
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

-- Custom locations added by admins
CREATE TABLE IF NOT EXISTS custom_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_am TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    is_subcity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item price reports (community moderation)
CREATE TABLE IF NOT EXISTS item_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_item_reports_item_id ON item_reports(item_id);

-- Payments table (alias for transactions, used by verify_payment handler)
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'ETB',
    payment_method TEXT,
    payment_reference TEXT,
    receipt_photo TEXT,
    status TEXT DEFAULT 'pending',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
"""