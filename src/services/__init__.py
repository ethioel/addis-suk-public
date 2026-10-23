# src/services/__init__.py
# Business logic services

from typing import Optional, List, Dict, Any, Tuple
from src.models.database import Database
from src.config import config
from datetime import datetime, timedelta
import math


class UserService:
    """Handles user-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_or_create_user(
        self, 
        telegram_id: int,
        username: Optional[str] = None,
        first_name: str = "",
        last_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get existing user or create new one."""
        user = await self.db.fetchone(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        
        if user:
            # Update last seen
            await self.db.execute(
                "UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
                (telegram_id,)
            )
            return dict(user)
        
        # Create new user
        cursor = await self.db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, username, first_name, last_name)
        )
        user_id = cursor.lastrowid
        
        user = await self.db.fetchone(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        return dict(user)
    
    async def update_user_language(self, telegram_id: int, language: str) -> bool:
        """Update user's language preference."""
        result = await self.db.execute(
            "UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (language, telegram_id)
        )
        return result.rowcount > 0
    
    async def update_user_location(
        self, 
        telegram_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        city: Optional[str] = None,
        sub_city: Optional[str] = None
    ) -> bool:
        """Update user's location."""
        result = await self.db.execute(
            """
            UPDATE users 
            SET latitude = ?, longitude = ?, city = ?, sub_city = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = ?
            """,
            (latitude, longitude, city, sub_city, telegram_id)
        )
        return result.rowcount > 0
    
    async def get_user_subscription_info(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's subscription details."""
        user = await self.db.fetchone(
            """
            SELECT subscription_tier, subscription_expires 
            FROM users WHERE telegram_id = ?
            """,
            (telegram_id,)
        )
        
        if not user:
            return {}
        
        is_premium = (
            user['subscription_tier'] == 'premium' and 
            user['subscription_expires'] and 
            datetime.fromisoformat(user['subscription_expires']) > datetime.utcnow()
        )
        
        return {
            'tier': user['subscription_tier'],
            'is_premium': is_premium,
            'expires': user['subscription_expires']
        }
    
    async def set_user_premium(self, telegram_id: int, months: int = 1) -> bool:
        """Set user as premium for specified months."""
        expires = datetime.utcnow() + timedelta(days=30 * months)
        result = await self.db.execute(
            """
            UPDATE users 
            SET subscription_tier = 'premium', 
                subscription_expires = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = ?
            """,
            (expires.isoformat(), telegram_id)
        )
        return result.rowcount > 0


class SellerService:
    """Handles seller-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def register_seller(
        self,
        user_id: int,
        shop_name: str,
        address: str,
        phone: str,
        city: str,
        sub_city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Tuple[bool, int]:
        """Register a new seller."""
        # First check if user already has a seller profile
        existing = await self.db.fetchone(
            "SELECT id FROM sellers WHERE user_id = ?", (user_id,)
        )
        
        if existing:
            # Update existing
            await self.db.execute(
                """
                UPDATE sellers 
                SET shop_name = ?, address = ?, phone = ?, city = ?, 
                    sub_city = ?, latitude = ?, longitude = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (shop_name, address, phone, city, sub_city, latitude, longitude, user_id)
            )
            seller_id = existing['id']
        else:
            # Create new
            cursor = await self.db.execute(
                """
                INSERT INTO sellers 
                (user_id, shop_name, address, phone, city, sub_city, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, shop_name, address, phone, city, sub_city, latitude, longitude)
            )
            seller_id = cursor.lastrowid
        
        return True, seller_id
    
    async def get_seller_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get seller profile by user ID."""
        seller = await self.db.fetchone(
            "SELECT * FROM sellers WHERE user_id = ?", (user_id,)
        )
        return dict(seller) if seller else None
    
    async def get_seller_by_id(self, seller_id: int) -> Optional[Dict[str, Any]]:
        """Get seller by ID."""
        seller = await self.db.fetchone(
            "SELECT * FROM sellers WHERE id = ?", (seller_id,)
        )
        return dict(seller) if seller else None
    
    async def approve_seller(self, seller_id: int) -> bool:
        """Approve a pending seller."""
        result = await self.db.execute(
            """
            UPDATE sellers 
            SET status = 'approved', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (seller_id,)
        )
        return result.rowcount > 0
    
    async def reject_seller(self, seller_id: int, reason: str = "") -> bool:
        """Reject a seller."""
        result = await self.db.execute(
            """
            UPDATE sellers 
            SET status = 'rejected', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (seller_id,)
        )
        return result.rowcount > 0

    async def get_shop_details(self, seller_id: int) -> Optional[Dict[str, Any]]:
        """Get a shop profile with aggregate stats."""
        shop = await self.db.fetchone(
            """
            SELECT s.*, u.telegram_id, u.username, u.first_name
            FROM sellers s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ?
            """,
            (seller_id,)
        )
        if not shop:
            return None
        return dict(shop)

    async def get_shop_items(
        self,
        seller_id: int,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get all sellable items for a shop with distance info."""
        items = await self.db.fetchall(
            """
            SELECT i.*, c.name_en as category_name_en, c.name_am as category_name_am
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE i.seller_id = ? AND i.status = 'approved'
            ORDER BY c.display_order, i.name_en
            """,
            (seller_id,)
        )
        results = []
        for item in items:
            item_dict = dict(item)
            if user_lat is not None and user_lon is not None and item_dict.get('latitude') is not None:
                item_dict['distance_km'] = round(self._haversine_distance(
                    user_lat, user_lon,
                    float(item_dict['latitude']), float(item_dict['longitude'])
                ), 2)
            results.append(item_dict)
        return results

    async def search_shops(
        self,
        query: str = "",
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search shops by name/city/address, ranked by closeness."""
        conditions = ["s.status = 'approved'"]
        params: List[Any] = []

        if query:
            conditions.append("(s.shop_name LIKE ? OR s.city LIKE ? OR s.address LIKE ? OR s.sub_city LIKE ?)")
            term = f"%{query}%"
            params.extend([term, term, term, term])

        where_clause = " AND ".join(conditions)

        shops = await self.db.fetchall(
            f"""
            SELECT s.*,
                   COUNT(i.id) as item_count,
                   MIN(i.price) as min_price,
                   MAX(i.price) as max_price
            FROM sellers s
            LEFT JOIN items i ON i.seller_id = s.id AND i.status = 'approved'
            WHERE {where_clause}
            GROUP BY s.id
            ORDER BY item_count DESC
            LIMIT ?
            """,
            (*params, limit)
        )

        results = []
        for shop in shops:
            shop_dict = dict(shop)
            if user_lat is not None and user_lon is not None and shop_dict.get('latitude') is not None:
                distance = self._haversine_distance(
                    user_lat, user_lon,
                    float(shop_dict['latitude']), float(shop_dict['longitude'])
                )
                shop_dict['distance_km'] = round(distance, 2)
            results.append(shop_dict)

        if user_lat is not None and user_lon is not None:
            results.sort(key=lambda x: (x.get('distance_km', float('inf'))))
        return results


class ItemService:
    """Handles item-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add_item(
        self,
        seller_id: int,
        category_id: int,
        name_en: str,
        name_am: str,
        price: float,
        unit: str,
        bulk_price: Optional[float] = None,
        bulk_quantity: Optional[int] = None
    ) -> Tuple[bool, int]:
        """Add a new item for sale."""
        cursor = await self.db.execute(
            """
            INSERT INTO items 
            (seller_id, category_id, name_en, name_am, price, unit, bulk_price, bulk_quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (seller_id, category_id, name_en, name_am, price, unit, bulk_price, bulk_quantity)
        )
        item_id = cursor.lastrowid
        
        # Add to price history
        await self.db.execute(
            """
            INSERT INTO price_history (item_id, price)
            VALUES (?, ?)
            """,
            (item_id, price)
        )
        
        return True, item_id
    
    async def update_item_price(
        self,
        seller_id: int,
        item_name: str,
        price: float
    ) -> Tuple[bool, int]:
        """Update price of an existing item."""
        # First find the item
        item = await self.db.fetchone(
            """
            SELECT i.* FROM items i
            JOIN sellers s ON i.seller_id = s.id
            WHERE s.user_id = ? 
            AND (i.name_en LIKE ? OR i.name_am LIKE ?)
            AND i.status = 'approved'
            """,
            (seller_id, f"%{item_name}%", f"%{item_name}%")
        )
        
        if not item:
            return False, 0
        
        # Update price
        await self.db.execute(
            """
            UPDATE items 
            SET price = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (price, item['id'])
        )
        
        # Add to price history
        await self.db.execute(
            """
            INSERT INTO price_history (item_id, price)
            VALUES (?, ?)
            """,
            (item['id'], price)
        )
        
        return True, item['id']
    
    async def delete_item(self, seller_id: int, item_name: str) -> bool:
        """Delete an item."""
        result = await self.db.execute(
            """
            DELETE FROM items 
            WHERE seller_id = ? 
            AND (name_en LIKE ? OR name_am LIKE ?)
            """,
            (seller_id, f"%{item_name}%", f"%{item_name}%")
        )
        return result.rowcount > 0
    
    async def get_seller_items(self, seller_id: int) -> List[Dict[str, Any]]:
        """Get all items for a seller."""
        items = await self.db.fetchall(
            """
            SELECT i.*, c.name_en as category_name_en, c.name_am as category_name_am
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE i.seller_id = ?
            ORDER BY i.created_at DESC
            """,
            (seller_id,)
        )
        return [dict(item) for item in items]
    
    async def search_items(
        self,
        query: str,
        category_id: Optional[int] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search for items with smart ranking by distance, price, and relevance."""
        # Build WHERE clause
        conditions = ["i.status = 'approved'", "s.status = 'approved'"]
        params: List[Any] = []
        
        if query:
            conditions.append("(i.name_en LIKE ? OR i.name_am LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term])
        
        if category_id:
            conditions.append("i.category_id = ?")
            params.append(category_id)
        
        where_clause = " AND ".join(conditions)
        
        # Count query
        count_query = f"""
            SELECT COUNT(*) 
            FROM items i
            JOIN sellers s ON i.seller_id = s.id
            WHERE {where_clause}
        """
        
        # Main query - fetch all matching items with seller/cat info
        query_sql = f"""
            SELECT i.*, 
                   s.shop_name, s.address, s.city, s.sub_city,
                   s.latitude, s.longitude,
                   c.name_en as category_name_en, c.name_am as category_name_am
            FROM items i
            JOIN sellers s ON i.seller_id = s.id
            JOIN categories c ON i.category_id = c.id
            WHERE {where_clause}
            ORDER BY i.created_at DESC
            LIMIT ? OFFSET ?
        """
        
        # Execute count using only the search params (not limit/offset)
        count_result = await self.db.fetchone(count_query, tuple(params))
        total_count = count_result['COUNT(*)'] if count_result else 0

        params.extend([limit, offset])
        
        # Execute main query
        items = await self.db.fetchall(query_sql, params)
        
        # Calculate smart score for each item
        result_items = []
        for item in items:
            item_dict = dict(item)
            
            # Initialize score components
            distance_km = None
            price_score = 0.0
            relevance_score = 0.0
            
            # 1. Calculate distance if user location provided
            if user_lat is not None and user_lon is not None and item_dict.get('latitude') is not None:
                distance = self._haversine_distance(
                    user_lat, user_lon,
                    float(item_dict['latitude']), float(item_dict['longitude'])
                )
                distance_km = round(distance, 2)
                # Score: closer is better (max 30 points, 0 at 50km+)
                if distance_km <= 5:
                    distance_score = 30
                elif distance_km <= 10:
                    distance_score = 25
                elif distance_km <= 20:
                    distance_score = 20
                elif distance_km <= 30:
                    distance_score = 15
                elif distance_km <= 50:
                    distance_score = 10
                else:
                    distance_score = 0
            else:
                distance_km = None
                distance_score = 0
            
            # 2. Price relevance scoring (0-30 points)
            # Lower price within category gets higher score; normalize against avg
            try:
                item_price = float(item_dict['price'])
                if item_price > 0:
                    # Base score: inverse price, capped; cheaper gets more points
                    price_score = max(0, 30 - min(25, int(item_price / 10)))
                    # Bonus for premium items being featured
                    if item_dict.get('featured_until') and item_dict.get('featured_until') > datetime.utcnow().isoformat() if isinstance(item_dict.get('featured_until'), str) else True:
                        price_score = min(price_score + 5, 30)
            except (ValueError, TypeError):
                price_score = 10  # Default neutral score
            
            # 3. Relevance to query (0-25 points)
            if query:
                name_en = str(item_dict.get('name_en', '')).lower()
                name_am = str(item_dict.get('name_am', '')).lower()
                q = query.lower()
                # Exact match gets highest score
                if q in name_en or q in name_am:
                    relevance_score = 25
                # Partial match (first word)
                elif name_en.startswith(q) or name_am.startswith(q):
                    relevance_score = 15
                # Contains query anywhere
                elif q in name_en or q in name_am:
                    relevance_score = 10
                # Category match bonus
                if item_dict.get('category_name_en') and q in str(item_dict['category_name_en']).lower():
                    relevance_score = min(relevance_score + 5, 25)
            else:
                # No query = freshness/relevance boost for recent/featured items
                try:
                    featured = item_dict.get('featured_until')
                    if featured:
                        fdate = datetime.fromisoformat(featured) if isinstance(featured, str) else featured
                        if fdate > datetime.utcnow():
                            relevance_score = 10  # Featured items get boost
                        else:
                            relevance_score = 0
                    else:
                        # Recent items get small boost
                        rel_created = item_dict.get('created_at')
                        if rel_created:
                            created = datetime.fromisoformat(rel_created) if isinstance(rel_created, str) else rel_created
                            if (datetime.utcnow() - created).days < 30:
                                relevance_score = 5
                except Exception:
                    relevance_score = 0
            
            # Total score = distance + price + relevance (max 85 points)
            total_score = distance_score + price_score + relevance_score
            
            item_dict['search_score'] = total_score
            item_dict['distance_km'] = distance_km
            result_items.append(item_dict)
        
        # Sort by total score (highest first), tie-break: featured first, then closer
        result_items.sort(key=lambda x: (
            -x.get('search_score', 0),
            0 if x.get('featured_until') else 1,
            x['distance_km'] if x.get('distance_km') is not None else float('inf'),
        ))
        
        # Return top 'limit' items (already sorted)
        final_items = result_items[:limit]
        
        return final_items, total_count
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) * 
            math.cos(math.radians(lat2)) * 
            math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    async def get_price_history(
        self,
        item_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price history for an item."""
        since_date = datetime.utcnow() - timedelta(days=days)
        history = await self.db.fetchall(
            """
            SELECT price, recorded_at 
            FROM price_history 
            WHERE item_id = ? AND recorded_at >= ?
            ORDER BY recorded_at DESC
            """,
            (item_id, since_date.isoformat())
        )
        return [dict(h) for h in history]


class FavoriteService:
    """Handles favorite items (premium feature)."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add_favorite(self, user_id: int, item_id: int) -> bool:
        """Add item to favorites."""
        try:
            await self.db.execute(
                """
                INSERT OR IGNORE INTO favorites (user_id, item_id)
                VALUES (?, ?)
                """,
                (user_id, item_id)
            )
            return True
        except Exception:
            return False
    
    async def remove_favorite(self, user_id: int, item_id: int) -> bool:
        """Remove item from favorites."""
        result = await self.db.execute(
            """
            DELETE FROM favorites 
            WHERE user_id = ? AND item_id = ?
            """,
            (user_id, item_id)
        )
        return result.rowcount > 0
    
    async def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all favorites for a user."""
        favorites = await self.db.fetchall(
            """
            SELECT f.*, 
                   i.name_en, i.name_am, i.price, i.unit,
                   s.shop_name, s.address
            FROM favorites f
            JOIN items i ON f.item_id = i.id
            JOIN sellers s ON i.seller_id = s.id
            WHERE f.user_id = ? AND i.status = 'approved' AND s.status = 'approved'
            ORDER BY f.created_at DESC
            """,
            (user_id,)
        )
        return [dict(fav) for fav in favorites]


class AlertService:
    """Handles price alerts (premium feature)."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_alert(
        self,
        user_id: int,
        item_name: str,
        target_price: float,
        category_id: Optional[int] = None
    ) -> Tuple[bool, int]:
        """Create a price alert."""
        cursor = await self.db.execute(
            """
            INSERT INTO price_alerts 
            (user_id, item_name, target_price, category_id)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, item_name, target_price, category_id)
        )
        return True, cursor.lastrowid
    
    async def get_user_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all alerts for a user."""
        alerts = await self.db.fetchall(
            """
            SELECT pa.*, 
                   c.name_en as category_name_en, c.name_am as category_name_am
            FROM price_alerts pa
            LEFT JOIN categories c ON pa.category_id = c.id
            WHERE pa.user_id = ? AND pa.is_active = TRUE
            ORDER BY pa.created_at DESC
            """,
            (user_id,)
        )
        return [dict(alert) for alert in alerts]
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all active alerts and return triggered ones."""
        alerts = await self.db.fetchall(
            """
            SELECT pa.*, u.telegram_id, u.language
            FROM price_alerts pa
            JOIN users u ON pa.user_id = u.id
            WHERE pa.is_active = TRUE
            """
        )
        
        triggered = []
        for alert in alerts:
            # Find current lowest price for this item
            items = await self.db.fetchall(
                """
                SELECT MIN(i.price) as min_price
                FROM items i
                JOIN sellers s ON i.seller_id = s.id
                WHERE (i.name_en LIKE ? OR i.name_am LIKE ?)
                  AND i.status = 'approved' 
                  AND s.status = 'approved'
                """,
                (f"%{alert['item_name']}%", f"%{alert['item_name']}%")
            )
            
            if items and items[0]['min_price'] is not None:
                min_price = items[0]['min_price']
                if min_price <= alert['target_price']:
                    triggered.append({
                        'alert': dict(alert),
                        'current_price': min_price,
                        'savings': alert['target_price'] - min_price
                    })
        
        return triggered


# Service container
class Services:
    """Container for all services."""
    
    def __init__(self, db: Database):
        self.user = UserService(db)
        self.seller = SellerService(db)
        self.item = ItemService(db)
        self.favorite = FavoriteService(db)
        self.alert = AlertService(db)