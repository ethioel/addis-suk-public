import asyncio
import logging
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, ErrorEvent,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Any

from src.config import load_config
config = load_config()
from src.models.database import Database, UserRole, SellerStatus


def get_args(message: Message) -> str:
    """Helper to extract command arguments in aiogram v3."""
    if not message.text:
        return ""
    parts = message.text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""
from src.services import Services
from src.locales import i18n
from src.middleware import (
    DatabaseMiddleware, LocalizationMiddleware,
    UserMiddleware, RateLimitMiddleware
)
from src.keyboards import (
    main_menu, language_selector, search_keyboard,
    seller_keyboard, admin_keyboard, subscription_keyboard,
    create_keyboard
)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_DIR / 'bot.log'),
        logging.StreamHandler(sys.stdout)
    ],
)
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    LANGUAGE_SELECT = State()
    SEARCH_QUERY = State()
    SELLER_NAME = State()
    SELLER_ADDRESS = State()
    SELLER_PHONE = State()
    SELLER_CITY = State()
    ITEM_NAME = State()
    ITEM_PRICE = State()
    ITEM_UNIT = State()
    ALERT_PRICE = State()
    BROADCAST_MESSAGE = State()


class AddisSukBot:

    def __init__(self):
        self.bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = Database(config.DB_PATH)
        self.services = Services(self.db)
        self.router = Router()

        self._setup_middlewares()
        self._register_startup()

    def _setup_middlewares(self):
        for event_type in [self.dp.message, self.dp.callback_query]:
            event_type.middleware(DatabaseMiddleware(self.db))
            event_type.middleware(LocalizationMiddleware())
            event_type.middleware(UserMiddleware())
            event_type.middleware(RateLimitMiddleware())

    async def _seed_categories(self):
        categories = [
            ("Vegetables", "አትክልት", "🌿"),
            ("Fruits", "ፍራፍሬ", "🍎"),
            ("Meat", "ሥጋ", "🥩"),
            ("Dairy", "ወተት", "🥛"),
            ("Bakery", "ዳቦ", "🍞"),
            ("Grains", "እህል", "🌾"),
            ("Coffee", "ቡና", "☕"),
            ("Household", "የቤት እቃ", "🧴"),
        ]
        for i, (name_en, name_am, emoji) in enumerate(categories):
            await self.db.execute(
                "INSERT OR IGNORE INTO categories (name_en, name_am, emoji, display_order) VALUES (?, ?, ?, ?)",
                (name_en, name_am, emoji, i)
            )
        logger.info("Categories seeded successfully.")

    def _register_startup(self):
        @self.dp.startup.register
        async def on_startup(dispatcher: Dispatcher, bot: Bot):
            try:
                await self.db.init()
                logger.info("Database initialized.")
                await self._seed_categories()
            except Exception as e:
                logger.error(f"Startup error: {e}")

    def register_handlers(self):
        self._register_commands()
        self._register_callbacks()
        self._register_errors()
        self.dp.include_router(self.router)
        logger.info("All handlers registered.")

    def _register_commands(self):
        @self.router.message(CommandStart())
        async def cmd_start(message: Message, state: FSMContext, db: Database, i18n, lang: str, t):
            user = await self.services.user.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            if not user.get('language'):
                await state.set_state(Form.LANGUAGE_SELECT)
                await message.answer(
                    "🌍 Please select your language / እባክዎ ቋንቋ ይምረጡ",
                    reply_markup=language_selector()
                )
                return

            welcome_text = {
                'en': (
                    "🛒 *Welcome to Addis Suk!*\n\n"
                    "Find the best prices on vegetables, fruits, meat, and more "
                    "from local sellers across Ethiopia.\n\n"
                    "🔍 /search tomato - Find current prices\n"
                    "📋 /categories - Browse by category\n"
                    "📍 /nearby tomato - Find sellers near you\n\n"
                    "Use the buttons below to navigate:"
                ),
                'am': (
                    "🛒 *ወደ አዲስ ሱቅ እንኳን ደህና መጡ!*\n\n"
                    "በመላው ኢትዮጵያ ከሚገኙ የሀገር ውስጥ ሻጮች የአትክልት፣ የፍራፍሬ፣ የሥጋ እና ሌሎች ምርቶችን ምርጥ ዋጋ ያግኙ።\n\n"
                    "🔍 /search tomato - የአሁኑን ዋጋ ለመፈለግ\n"
                    "📋 /categories - በምድብ ለመመልከት\n"
                    "📍 /nearby tomato - በአቅራቢያዎ ያሉ ሱቆችን ለመፈለግ\n\n"
                    "ለማሰስ ከታች ያሉትን ቁልፎች ይጠቀሙ:"
                ),
            }
            await message.answer(
                welcome_text.get(lang, welcome_text['en']),
                reply_markup=main_menu(lang)
            )

        @self.router.message(Command("help"))
        async def cmd_help(message: Message, lang: str):
            help_text = {
                'en': (
                    "📖 *Addis Suk Help Center*\n\n"
                    "🔍 /search [item] - Search for prices (e.g., /search tomato)\n"
                    "📋 /categories - Browse product categories\n"
                    "📍 /nearby [item] - Find sellers near your location\n"
                    "⚙️ /settings - Adjust your preferences\n"
                    "📢 /about - Information about Addis Suk\n\n"
                    "_Premium Features:\n"
                    "⭐ /favorites - View saved items\n"
                    "🔔 /alerts - Manage price alerts\n"
                    "📊 /history [item] - Price change history\n"
                    "🧾 /subscribe - Upgrade your account\n\n"
                    "_Seller Tools:\n"
                    "📝 /register - Register your shop\n"
                    "📋 /mylistings - View your items\n"
                    "📍 /setlocation - Set your shop location\n"
                    "📉 /update [item] [price] - Update your prices\n"
                    "🗑 /delete [item] - Remove a listing"
                ),
                'am': (
                    "📖 *የአዲስ ሱቅ እርዳታ ማዕከል*\n\n"
                    "🔍 /search [ምርት] - ዋጋ ለመፈለግ (ለምሳሌ /search tomato)\n"
                    "📋 /categories - የምርት ምድቦችን ለመመልከት\n"
                    "📍 /nearby [ምርት] - በአቅራቢያዎ ያሉ ሱቆችን ለመፈለግ\n"
                    "⚙️ /settings - ምርጫዎችዎን ለማስተካከል\n"
                    "📢 /about - ስለ አዲስ ሱቅ መረጃ\n\n"
                    "⭐ *ልዩ አገልግሎቶች (ፕሪሚየም):*\n"
                    "⭐ /favorites - የተቀመጡ ምርቶችን ለመመልከት\n"
                    "🔔 /alerts - የዋጋ ማሳወቂያዎችን ለማስተዳደር\n"
                    "📊 /history [ምርት] - የዋጋ ለውጥ ታሪክ\n"
                    "🧾 /subscribe - አባልነትዎን ለማሳደግ\n\n"
                    "💼 *የሻጭ መሣሪያዎች:*\n"
                    "📝 /register - ሱቅዎን ለመመዝገብ\n"
                    "📋 /mylistings - የእርስዎን ምርቶች ለመመልከት\n"
                    "📍 /setlocation - የሱቅዎን አድራሻ ለማስተካከል\n"
                    "📉 /update [ምርት] [ዋጋ] - ዋጋ ለማዘመን\n"
                    "🗑 /delete [ምርት] - ምርት ለማስወገድ"
                ),
            }
            await message.answer(help_text.get(lang, help_text['en']), parse_mode="Markdown")

        @self.router.message(Command("about"))
        async def cmd_about(message: Message, lang: str):
            about_text = {
                'en': (
                    "🏪 *Addis Suk v1.0*\n\n"
                    "Telegram-based price comparison platform connecting Ethiopian consumers "
                    "with local sellers.\n\n"
                    "🌍 Bilingual: Amharic & English\n"
                    "📍 10+ cities: Addis Ababa, Bahir Dar, Gondar, Mekelle, Hawassa...\n"
                    "🔒 Free core features with optional premium\n\n"
                    "_Payments: Telebirr • CBEBirr • Chapa • Cash_"
                ),
                'am': (
                    "🏪 *አዲስ ሱቅ v1.0*\n\n"
                    "የኢትዮጵያ ደንበኞችን ከሀገር ውስጥ ሱቆች ጋር የሚያገናኝ በቴሌግራም ላይ የተመሠረተ የዋጋ ማወዳደሪያ መድረክ።\n\n"
                    "🌍 ባለሁለት ቋንቋ፡ አማርኛ እና እንግሊዝኛ\n"
                    "📍 ከ10 በላይ ከተሞች፡ አዲስ አበባ፣ ባሕር ዳር፣ ጎንደር፣ መቐለ፣ ሀዋሳ...\n"
                    "🔒 ነፃ መሠረታዊ አገልግሎቶች ከተጨማሪ የፕሪሚየም ምርጫዎች ጋር\n\n"
                    "_የክፍያ አማራጮች፡ ቴሌብር • ሲቢኢ ብር • ቻፓ • በጥሬ ገንዘብ_"
                ),
            }
            await message.answer(about_text.get(lang, about_text['en']))

        @self.router.message(Command("settings"))
        async def cmd_settings(message: Message, lang: str):
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text="🌍 Language", callback_data="settings_language")
            keyboard.button(text="⭐ Premium", callback_data="settings_premium")
            keyboard.button(text="❌ Cancel", callback_data="cancel")
            await message.answer(
                "⚙️ *Settings*\nChoose an option:" if lang == 'en' else "⚙️ *ማስተካከያዎች*\n ይምረጡ:",
                reply_markup=keyboard.as_markup(), parse_mode="Markdown"
            )

        @self.router.message(Command("search"))
        async def cmd_search(message: Message, state: FSMContext, db: Database, user: dict, lang: str):
            if not user:
                user = await self.services.user.get_or_create_user(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )
            user_info = await self.services.user.get_user_subscription_info(message.from_user.id)
            search_count = await db.fetchone(
                "SELECT COUNT(*) as cnt FROM search_logs WHERE user_id = ? AND date(created_at) = date('now')",
                (user['id'],)
            )
            count = search_count['cnt'] if search_count else 0
            if not user_info['is_premium'] and count >= config.FREE_SEARCH_LIMIT:
                await message.answer(
                    "⚠️ You've reached your daily free limit (5 searches).\n"
                    "Upgrade to Premium for unlimited searches!\n/subscribe"
                    if lang == 'en' else "⚠️ የዕለት ነፃ ፍለጋ ገደብዎን (5 ፍለጋዎች) ጨርሰዋል።\nላልተገደበ ፍለጋ ወደ ፕሪሚየም ያሻሽሉ!\n/subscribe",
                    reply_markup=subscription_keyboard()
                )
                return

            query = get_args(message)
            if query:
                await self._perform_search(message, query, db, user, lang)
            else:
                await state.set_state(Form.SEARCH_QUERY)
                await message.answer("🔍 Enter item name (e.g., tomato)"
                    if lang == 'en' else "🔍 የሚፈልጉትን ምርት ስም ያስገቡ (ለምሳሌ፦ ቲማቲም)፦")

        @self.router.message(Form.SEARCH_QUERY)
        async def process_search(message: Message, state: FSMContext, db: Database, user: dict, lang: str):
            await state.clear()
            await self._perform_search(message, message.text, db, user, lang)

        @self.router.message(Command("categories"))
        async def cmd_categories(message: Message, db: Database, lang: str):
            cats = await db.fetchall(
                "SELECT * FROM categories WHERE is_active = 1 ORDER BY display_order"
            )
            keyboard = InlineKeyboardBuilder()
            for cat in cats:
                emoji = cat['emoji'] or ''
                name = cat['name_am'] if lang == 'am' else cat['name_en']
                keyboard.button(text=f"{emoji} {name}", callback_data=f"cat_{cat['id']}")
            keyboard.button(text="❌ Cancel", callback_data="cancel")
            await message.answer("📋 Categories" if lang == 'en' else "📋 የምርት ምድቦች",
                reply_markup=keyboard.as_markup())

        @self.router.message(Command("nearby"))
        async def cmd_nearby(message: Message, state: FSMContext, db: Database, user: dict, lang: str):
            if not user:
                user = await self.services.user.get_or_create_user(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )
            query = get_args(message)
            if not user.get('latitude') or not user.get('longitude'):
                keyboard = location_menu(lang)
                await message.answer(
                    "📍 Please share your location to find nearby sellers."
                        if lang == 'en' else "📍 በአቅራቢያዎ ያሉ ሱቆችን ለማግኘት እባክዎ መገኛ ቦታዎን (Location) ያጋሩ።",
                    reply_markup=keyboard
                )
                if query:
                    await state.set_state(Form.SEARCH_QUERY)
                    await state.update_data(nearby_query=query)
                return

            items, total = await self.services.item.search_items(
                query=query, user_lat=user['latitude'], user_lon=user['longitude'], limit=20
            )
            await self._display_results(message, items, total, lang, query or "nearby")

        @self.router.message(Command("register"))
        async def cmd_register(message: Message, state: FSMContext, db: Database, user: dict, lang: str):
            existing = await self.services.seller.get_seller_by_user_id(user['id'])
            if existing and existing['status'] != 'rejected':
                await message.answer(f"✅ You're already registered!\nShop: {existing['shop_name']}")
                return
            await state.set_state(Form.SELLER_NAME)
            await message.answer("📝 Enter shop name:" if lang == 'en' else "📝 የሱቁን ስም ያስገቡ፦")

        @self.router.message(Form.SELLER_NAME)
        async def seller_name_handler(message: Message, state: FSMContext, lang: str):
            await state.update_data(name=message.text)
            await state.set_state(Form.SELLER_ADDRESS)
            await message.answer("🏠 Enter address:" if lang == 'en' else "🏠 አድራሻ ያስገቡ፦")

        @self.router.message(Form.SELLER_ADDRESS)
        async def seller_address_handler(message: Message, state: FSMContext, lang: str):
            await state.update_data(address=message.text)
            await state.set_state(Form.SELLER_PHONE)
            await message.answer("📱 Enter phone number (e.g., 0912345678):"
                if lang == 'en' else "📱 ስልክ ቁጥር ያስገቡ (ለምሳሌ፦ 0912345678)፦")

        @self.router.message(Form.SELLER_PHONE)
        async def seller_phone_handler(message: Message, state: FSMContext, lang: str):
            await state.update_data(phone=message.text)
            await state.set_state(Form.SELLER_CITY)
            await message.answer("🏙️ Enter city:" if lang == 'en' else "🏙️ ከተማ ያስገቡ፦")

        @self.router.message(Form.SELLER_CITY)
        async def seller_city_handler(message: Message, state: FSMContext, db: Database, user: dict, lang: str):
            data = await state.get_data()
            await state.clear()
            success, seller_id = await self.services.seller.register_seller(
                user_id=user['id'], shop_name=data['name'], address=data['address'],
                phone=data['phone'], city=message.text
            )
            await message.answer(
                "✅ Shop registered! Pending approval.\nYour shop ID: " + str(seller_id)
                if lang == 'en' else f"✅ ሱቁ ተመዝግቧል! ማረጋገጫ በመጠበቅ ላይ።\nየሱቅዎ መለያ ቁጥር (ID): {seller_id}",
                reply_markup=main_menu(lang)
            )

        @self.router.message(Command("setlocation"))
        async def cmd_setlocation(message: Message, lang: str):
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text="📍 Share Location", request_location=True)
            keyboard.button(text="❌ Cancel", callback_data="cancel")
            await message.answer("📍 Send your location to save it:"
                if lang == 'en' else "📍 ለማስቀመጥ መገኛዎን (Location) ይላኩ፦", reply_markup=keyboard.as_markup())

        @self.router.message(lambda m: m.location is not None)
        async def handle_location(message: Message, db: Database, user: dict, lang: str):
            loc = message.location
            await self.services.user.update_user_location(
                user['telegram_id'], latitude=loc.latitude, longitude=loc.longitude
            )
            # Auto-set location and perform nearby search
            await cmd_nearby_auto(message, loc.latitude, loc.longitude, lang)

        async def cmd_nearby_auto(message: Message, lat: float, lon: float, lang: str):
            """Auto-perform nearby search using shared location."""
            from src.services import Services
            items, total = await self.services.item.search_items(
                query="", user_lat=lat, user_lon=lon, limit=20
            )
            await self._display_results(message, items, total, lang, "nearby")

        @self.router.message(Command("add"))
        async def cmd_add(message: Message, db: Database, user: dict, lang: str):
            seller = await self.services.seller.get_seller_by_user_id(user['id'])
            if not seller or seller['status'] != 'approved':
                await message.answer("❌ You need to be an approved seller to add items."
                    if lang == 'en' else "❌ ምርቶችን ለማስገባት የተፈቀደለት ሻጭ መሆን አለብዎት።")
                return
            args = get_args(message).split()
            if len(args) < 3:
                await message.answer("Usage: /add [item] [price] [unit]\nExample: /add tomato 80 kg"
                    if lang == 'en' else "አጠቃቀም: /add [ምርት] [ዋጋ] [መለኪያ]\nለምሳሌ: /add ቲማቲም 80 ኪሎ")
                return
            try:
                price = float(args[1])
            except ValueError:
                await message.answer("❌ Invalid price format. Example: 80")
                return
            category = await db.fetchone("SELECT id FROM categories WHERE is_active = 1 ORDER BY display_order LIMIT 1")
            category_id = category['id'] if category else 1
            success, item_id = await self.services.item.add_item(
                seller_id=seller['id'], category_id=category_id,
                name_en=args[0], name_am=args[0], price=price, unit=args[2]
            )
            await message.answer(
                f"✅ Item added! ID: {item_id} - awaiting approval."
                if lang == 'en' else f"✅ ምርቱ ተጨምሯል! መለያ ቁጥር (ID): {item_id} - ማጽደቅን በመጠበቅ ላይ።"
            )

        @self.router.message(Command("mylistings"))
        async def cmd_mylistings(message: Message, db: Database, user: dict, lang: str):
            seller = await self.services.seller.get_seller_by_user_id(user['id'])
            if not seller:
                await message.answer("❌ Seller registration required." if lang == 'en' else "❌ የሻጭ ምዝገባ ያስፈልጋል።")
                return
            items = await self.services.item.get_seller_items(seller['id'])
            if not items:
                await message.answer("📭 No items listed yet.\nUse /add to add items." if lang == 'en' else "📭 እስካሁን የተመዘገቡ ምርቶች የሉም።\nምርቶችን ለመጨመር /add ይጠቀሙ።")
                return
            parts = ["📋 *My Listings*"]
            for item in items:
                name = item['name_am'] if lang == 'am' else item['name_en']
                icon = "✅" if item['status'] == 'approved' else "⏳" if item['status'] == 'pending' else "❌"
                parts.append(f"{icon} {name} - {item['price']} {item['unit']}")
            await message.answer("\n".join(parts), parse_mode="Markdown")

        @self.router.message(Command("update"))
        async def cmd_update(message: Message, db: Database, user: dict, lang: str):
            args = get_args(message).split()
            if len(args) < 2:
                await message.answer("Usage: /update [item] [price]\nExample: /update tomato 75")
                return
            seller = await self.services.seller.get_seller_by_user_id(user['id'])
            if not seller:
                await message.answer("❌ Seller registration required." if lang == 'en' else "❌ የሻጭ ምዝገባ ያስፈልጋል።")
                return
            try:
                new_price = float(args[1])
            except ValueError:
                await message.answer("❌ Invalid price format.")
                return
            success, _ = await self.services.item.update_item_price(seller['id'], args[0], new_price)

            if lang == 'en':
                msg = f"✅ Price updated to {new_price}" if success else "❌ Item not found."
            else:
                msg = f"✅ ዋጋው ወደ {new_price} ተዘምኗል" if success else "❌ ምርቱ አልተገኘም።"
            await message.answer(msg)

        @self.router.message(Command("delete"))
        async def cmd_delete(message: Message, db: Database, user: dict, lang: str):
            item_name = get_args(message)
            if not item_name:
                await message.answer("Usage: /delete [item]")
                return
            seller = await self.services.seller.get_seller_by_user_id(user['id'])
            if not seller:
                await message.answer("❌ Seller registration required." if lang == 'en' else "❌ የሻጭ ምዝገባ ያስፈልጋል።")
                return
            success = await self.services.item.delete_item(seller['id'], item_name)

            if lang == 'en':
                msg = "✅ Item deleted." if success else "❌ Item not found."
            else:
                msg = "✅ ምርቱ ተሰርዟል።" if success else "❌ ምርቱ አልተገኘም።"
            await message.answer(msg)

        @self.router.message(Command("subscribe"))
        async def cmd_subscribe(message: Message, lang: str):
            sub_text = {
                'en': (
                    "🌟 *Premium Subscription*\n\n"
                    "*Buyer Premium - 100 Br/month:*\n"
                    "  ✅ Unlimited searches\n  ✅ Price alerts (10 items)\n"
                    "  ✅ Favorites\n  ✅ Price history (30 days)\n"
                    "  ✅ Ad-free\n  ✅ Priority support\n\n"
                    "*Seller Premium - 250 Br/month:*\n"
                    "  ✅ Unlimited items\n  ✅ Featured listings\n"
                    "  ✅ Full analytics\n  ✅ Verified badge\n"
                    "  ✅ Bulk discounts\n  ✅ Promotional broadcasts\n\n"
                    "Choose a plan below:"
                ),
                'am': (
                    "🌟 *ፕሪሚየም አባልነት*\n\n"
                    "*የገዢ ፕሪሚየም - 100 ብር/ወር:*\n"
                    "  ✅ ያልተገደበ ፍለጋ\n  ✅ የዋጋ ማሳወቂያዎች (10 ምርቶች)\n"
                    "  ✅ ተወዳጅ\n  ✅ የዋጋ ታሪክ (30 ቀናት)\n"
                    "  ✅ ከማስታወቂያ ነፃ\n  ✅ ቅድሚያ የሚሰጠው ድጋፍ\n\n"
                    "*የሻጭ ፕሪሚየም - 250 ብር/ወር:*\n"
                    "  ✅ ያልተገደቡ ምርቶች\n  ✅ ተመራጭ ዝርዝሮች\n  ✅ ሙሉ ትንታኔዎች\n  ✅ የተረጋገጠ ባጅ\n  ✅ የጅምላ ቅናሾች\n  ✅ የማስተዋወቂያ ስርጭቶች\n\n"
                    "ከዚህ በታች ያሉትን እቅን ይምረጡ:"
                )
            }
            keyboard = subscription_keyboard()
            await message.answer(sub_text.get(lang, sub_text['en']), reply_markup=keyboard)

        @self.router.message(Command("favorites"))
        async def cmd_favorites(message: Message, db: Database, user: dict, lang: str):
            user_info = await self.services.user.get_user_subscription_info(message.from_user.id)
            if not user_info['is_premium']:
                await message.answer("⭐ Premium feature. Use /subscribe to upgrade." if lang == 'en' else "⭐ የፕሪሚየም አገልግሎት። ለማሻሻል /subscribe ይጠቀሙ።")
                return
            favorites = await self.services.favorite.get_user_favorites(user['id'])
            if not favorites:
                await message.answer("📭 Your favorites list is empty." if lang == 'en' else "📭 የተወዳጆች ዝርዝርዎ ባዶ ነው።")
                return
            parts = ["⭐ *My Favorites*"] if lang == 'en' else ["⭐ *የእኛ ተወዳጆች*"]
            for f in favorites:
                name = f['name_am'] if lang == 'am' else f['name_en']
                parts.append(f"• {name} - {f['price']} {f['unit']} ({f['shop_name']})")
            await message.answer("\n".join(parts), parse_mode="Markdown")

        @self.router.message(Command("alerts"))
        async def cmd_alerts(message: Message, db: Database, user: dict, lang: str):
            user_info = await self.services.user.get_user_subscription_info(message.from_user.id)
            if not user_info['is_premium']:
                await message.answer("⭐ Premium feature. Use /subscribe to upgrade." if lang == 'en' else "⭐ የፕሪሚየም አገልግሎት። ለማሻሻል /subscribe ይጠቀሙ።")
                return
            alerts = await self.services.alert.get_user_alerts(user['id'])
            if not alerts:
                await message.answer("🔔 No active alerts. Set alerts with /alert [item] [price]" if lang == 'en' else "🔔 ንቁ ማሳወቂያዎች የሉም። በ /alert [ምርት] [ዋጋ] ማሳወቂያዎችን ያዘጋጁ።")
                return
            parts = ["🔔 *My Price Alerts*"] if lang == 'en' else ["🔔 *የዋጋ ማሳወቂያዎቼ*"]
            for a in alerts:
                parts.append(f"• {a['item_name']} at or below {a['target_price']} Br" if lang == 'en' else f"• {a['item_name']} ከ {a['target_price']} ብር ወይም በታች ሲሆን")
            await message.answer("\n".join(parts), parse_mode="Markdown")

        @self.router.message(Command("alert"))
        async def cmd_alert_add(message: Message, db: Database, user: dict, lang: str):
            args = get_args(message).split()
            if len(args) < 2:
                await message.answer("Usage: /alert [item] [target_price]\nExample: /alert tomato 50")
                return
            user_info = await self.services.user.get_user_subscription_info(message.from_user.id)
            if not user_info['is_premium']:
                await message.answer("⭐ Premium feature. Use /subscribe to upgrade." if lang == 'en' else "⭐ የፕሪሚየም አገልግሎት። ለማሻሻል /subscribe ይጠቀሙ።")
                return
            try:
                target = float(args[1])
            except ValueError:
                await message.answer("❌ Invalid price format." if lang == 'en' else "❌ ትክክል ያልሆነ የዋጋ ግብአት።")
                return
            success, alert_id = await self.services.alert.create_alert(user['id'], args[0], target)
            await message.answer(f"🔔 Alert created! You'll be notified when {args[0]} is at or below {target} Br." if lang == 'en' else f"🔔 ማሳወቂያ ተፈጥሯል! {args[0]} ከ {target} ብር ወይም በታች ሲሆን ማሳወቂያ ይደርስዎታል።")

        @self.router.message(Command("history"))
        async def cmd_history(message: Message, db: Database, user: dict, lang: str):
            user_info = await self.services.user.get_user_subscription_info(message.from_user.id)
            if not user_info['is_premium']:
                await message.answer("⭐ Premium feature. Use /subscribe to upgrade." if lang == 'en' else "⭐ የፕሪሚየም አገልግሎትን ለማሻሻል /subscribe ይጠቀሙ።")
                return
            query = get_args(message)
            if not query:
                await message.answer("Usage: /history [item]" if lang == 'en' else "አጠቃቀም: /history [ምርት]")
                return
            items = await db.fetchall(
                "SELECT DISTINCT i.id, i.name_en, i.name_am FROM items i WHERE i.name_en LIKE ? OR i.name_am LIKE ? LIMIT 5",
                (f"%{query}%", f"%{query}%")
            )
            if not items:
                await message.answer("❌ Item not found." if lang == 'en' else "❌ ምርቱ አልተገኘም።")
                return
            history = await self.services.item.get_price_history(items[0]['id'], days=30)
            if not history:
                await message.answer("No price history available." if lang == 'en' else "የዋጋ ታሪክ የለም።")
                return
            parts = [f"📊 *Price History for {items[0]['name_en']}*"] if lang == 'en' else [f"📊 *የ{items[0]['name_am']} የዋጋ ታሪክ*"]
            for entry in history:
                parts.append(f"• {entry['recorded_at']}: {entry['price']} Br")
            await message.answer("\n".join(parts), parse_mode="Markdown")

        @self.router.message(Command("admin"))
        async def cmd_admin(message: Message, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                await message.answer("❌ Access denied." if lang == 'en' else "❌ ፍቃድ አልተሰጠዎትም።")
                return
            stats = await db.fetchone(
                "SELECT (SELECT COUNT(*) FROM sellers WHERE status='pending') as pending_sellers, "
                "(SELECT COUNT(*) FROM items WHERE status='pending') as pending_items, "
                "(SELECT COUNT(*) FROM users WHERE subscription_tier='premium') as premium_users"
            )
            await message.answer(
                f"📊 *Admin Dashboard*\n\n"
                f"Pending Sellers: {stats['pending_sellers']}\n"
                f"Pending Items: {stats['pending_items']}\n"
                f"Premium Users: {stats['premium_users']}",
                reply_markup=admin_keyboard(), parse_mode="Markdown"
            )

        @self.router.message(Command("approve_seller"))
        async def cmd_approve_seller(message: Message, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                await message.answer("❌ Access denied." if lang == 'en' else "❌ ፍቃድ አልተሰጠዎትም።")
                return
            args = get_args(message).split()
            if not args or not args[0].isdigit():
                await message.answer("Usage: /approve_seller [id]")
                return
            cursor = await db.execute("UPDATE sellers SET status='approved' WHERE id=?", (int(args[0]),))
            await message.answer("✅ Seller approved!" if cursor.rowcount else "❌ Not found.")

        @self.router.message(Command("approve_price"))
        async def cmd_approve_price(message: Message, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                return
            args = get_args(message).split()
            if not args or not args[0].isdigit():
                await message.answer("Usage: /approve_price [id]")
                return
            await db.execute("UPDATE items SET status='approved' WHERE id=?", (int(args[0]),))
            await message.answer("✅ Item approved!")

        @self.router.message(Command("reject"))
        async def cmd_reject(message: Message, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                return
            args = get_args(message).split(None, 1)
            if len(args) < 1:
                await message.answer("Usage: /reject [id] [reason]")
                return
            reason = args[1] if len(args) > 1 else "No reason provided"
            await db.execute("UPDATE items SET status='rejected' WHERE id=?", (int(args[0]),))
            await message.answer(f"❌ Item rejected: {reason}")

        @self.router.message(Command("broadcast"))
        async def cmd_broadcast(message: Message, state: FSMContext, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                return
            await state.set_state(Form.BROADCAST_MESSAGE)
            await message.answer("📢 Enter your broadcast message:" if lang == 'en' else "📢 ለተጠቃሚዎች የሚተላለፈውን መልእክት ያስገቡ፦")

        @self.router.message(Form.BROADCAST_MESSAGE)
        async def process_broadcast(message: Message, state: FSMContext, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                return
            text = message.text
            users = await db.fetchall("SELECT telegram_id FROM users")
            sent = 0
            for user_row in users:
                try:
                    await self.bot.send_message(user_row['telegram_id'], text)
                    sent += 1
                except Exception:
                    pass
            await db.execute(
                "INSERT INTO broadcasts (admin_id, message, sent_count) VALUES (?, ?, ?)",
                (message.from_user.id, text, sent)
            )
            await message.answer(f"✅ Broadcast sent to {sent} users." if lang == 'en' else f"✅ መልእክቱ ለ {sent} ተጠቃሊዎች ተልኳል።")
            await state.clear()

        @self.router.message(Command("stats"))
        async def cmd_stats(message: Message, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                return
            rows = await db.fetchall(
                "SELECT date(created_at) as day, COUNT(*) as cnt FROM search_logs "
                "WHERE created_at >= date('now', '-7 days') GROUP BY date(created_at) ORDER BY day DESC"
            )
            parts = ["📈 *Weekly Search Stats*"]
            for row in rows:
                parts.append(f"• {row['day']}: {row['cnt']} searches")
            await message.answer("\n".join(parts) or "No data yet.", parse_mode="Markdown")

        @self.router.message(Command("earnings"))
        async def cmd_earnings(message: Message, db: Database, lang: str):
            if message.from_user.id not in config.ADMIN_IDS:
                return
            rows = await db.fetchall(
                "SELECT type, COUNT(*) as cnt, SUM(amount) as total FROM transactions "
                "WHERE status='completed' GROUP BY type ORDER BY total DESC"
            )
            parts = ["💰 *Revenue Report*"]
            total_rev = 0
            for row in rows:
                total = row['total'] or 0
                total_rev += total
                parts.append(f"• {row['type']}: {row['cnt']} txns, {total:.2f} Br")
            parts.append(f"\n📊 *Total Revenue: {total_rev:.2f} Br*")
            await message.answer("\n".join(parts), parse_mode="Markdown")

    def _register_callbacks(self):
        @self.router.callback_query(F.data == "language" or F.data.startswith("lang_"))
        async def cb_language(callback: CallbackQuery, db: Database, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            if callback.data.startswith("lang_"):
                new_lang = callback.data.split("_")[1]
                await self.services.user.update_user_language(callback.from_user.id, new_lang)
                try:
                    await callback.message.edit_text(
                        "✅ Language updated!" if new_lang == 'en' else "✅ ቋንቋው ተዘምኗል!",
                        reply_markup=None
                    )
                except Exception:
                    pass
            elif callback.data == "language":
                try:
                    await callback.message.edit_text(
                        "🌍 Select language:" if lang == 'en' else "🌍 ቋንቋ ይምረጡ፦",
                        reply_markup=language_selector()
                    )
                except Exception:
                    await callback.message.answer("🌍 Select language:" if lang == 'en' else "🌍 ቋንቋ ይምረጡ፦")

        @self.router.callback_query(F.data == "settings_language")
        async def cb_settings_language(callback: CallbackQuery, db: Database, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            try:
                await callback.message.edit_text(
                    "🌍 Select language:" if lang == 'en' else "🌍 ቋንቋ ይምረጡ፦",
                    reply_markup=language_selector()
                )
            except Exception:
                await callback.message.answer("🌍 Select language:" if lang == 'en' else "🌍 ቋንቋ ይምረጡ፦")

        @self.router.callback_query(F.data == "settings_premium")
        async def cb_settings_premium(callback: CallbackQuery, db: Database, user: dict, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            info = await self.services.user.get_user_subscription_info(callback.from_user.id)
            status_text = "⭐ Your subscription is active" if info['is_premium'] else "⭐ No active subscription"
            am_status_text = "⭐ አባል ነዎት" if info['is_premium'] else "⭐ አ巴ል አይደልም"
            try:
                await callback.message.edit_text(
                    status_text if lang == 'en' else am_status_text,
                    reply_markup=subscription_keyboard()
                )
            except Exception:
                await callback.message.answer(status_text if lang == 'en' else am_status_text)

        @self.router.callback_query(F.data.startswith("cat_"))
        async def cb_category(callback: CallbackQuery, db: Database, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            cat_id = int(callback.data.split("_")[1])
            category = await db.fetchone("SELECT * FROM categories WHERE id=?", (cat_id,))
            if not category:
                return
            cat_name = category['name_am'] if lang == 'am' else category['name_en']

            items = await db.fetchall(
                """SELECT i.*, s.shop_name, s.city, s.latitude, s.longitude
                   FROM items i JOIN sellers s ON i.seller_id=s.id
                   WHERE i.category_id=? AND i.status='approved' AND s.status='approved'
                   ORDER BY s.featured_until IS NULL, i.price ASC LIMIT 10""",
                (cat_id,)
            )
            if not items:
                msg = f"No items in {cat_name} yet." if lang == 'en' else f"በ{cat_name} ምድብ ውስጥ እስካሁን ምርቶች የሉም።"
                try:
                    await callback.message.edit_text(
                        msg,
                        reply_markup=main_menu(lang)
                    )
                except Exception:
                    await callback.message.answer(msg)
                return
            parts = [f"📋 *{cat_name} - {len(items)} items*" if lang == 'en' else f"📋 *{cat_name} - {len(items)} ምርቶች*"]
            for item in items:
                name = item['name_am'] if lang == 'am' else item['name_en']
                parts.append(f"• {name}: {item['price']} {item['unit']}")

            keyboard = InlineKeyboardBuilder()
            for item in items[:5]:
                keyboard.button(text=f"⭐", callback_data=f"fav_{item['id']}")
            keyboard.button(text="❌ Cancel", callback_data="cancel")
            try:
                await callback.message.edit_text(
                    "\n".join(parts), reply_markup=keyboard.as_markup(), parse_mode="Markdown"
                )
            except Exception:
                await callback.message.answer(
                    "\n".join(parts), reply_markup=keyboard.as_markup()
                )

        @self.router.callback_query(F.data.startswith("fav_"))
        async def cb_favorite(callback: CallbackQuery, db: Database, user: dict, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            item_id = int(callback.data.split("_")[1])
            info = await self.services.user.get_user_subscription_info(callback.from_user.id)
            if not info['is_premium']:
                return
            success = await self.services.favorite.add_favorite(user['id'], item_id)
            msg = "⭐ Added to favorites!" if success else "Already favorited!"
            am_msg = "⭐ ተመራጭ ሆኗል!" if success else "ቀደም ሲል ተራት ላይ አለ!"
            try:
                await callback.answer(msg if lang == 'en' else am_msg)
            except Exception:
                pass  # Ignore if the answer is no longer valid

        @self.router.callback_query(F.data.startswith("buy_premium_"))
        async def cb_buy_premium(callback: CallbackQuery, db: Database, user: dict, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            plan = callback.data.replace("buy_premium_", "")
            price = config.BUYER_PREMIUM_PRICE if plan == "buyer" else config.SELLER_PREMIUM_PRICE
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, status) VALUES (?, ?, ?, 'pending')",
                (user['id'], f"{plan}_premium", price)
            )
            try:
                await callback.message.edit_text(
                    f"🧾 *Payment for {plan.title()} Premium*\n\n"
                    f"Amount: {price} Br\n\n"
                    f"Send payment to:\n📱 Telebirr: 0912345678\n"
                    f"After payment, send the receipt or use /verify_payment [reference]",
                    reply_markup=None, parse_mode="Markdown"
                )
            except Exception:
                await callback.message.answer(
                    f"🧾 *Payment for {plan.title()} Premium*\n\n"
                    f"Amount: {price} Br\n\n"
                    f"Send payment to:\n📱 Telebirr: 0912345678\n"
                    f"After payment, send the receipt or use /verify_payment [reference]",
                    parse_mode="Markdown"
                )

        @self.router.callback_query(F.data.startswith("sell_premium_"))
        async def cb_sell_premium(callback: CallbackQuery, db: Database, user: dict, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid
            price = config.SELLER_PREMIUM_PRICE
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, status) VALUES (?, ?, ?, 'pending')",
                (user['id'], "seller_premium", price)
            )
            try:
                await callback.message.edit_text(
                    "🧾 *Seller Premium Payment*\n\n"
                    f"Amount: {price} Br\n\n"
                    "Send payment to Telebirr: 0912345678 and send receipt.",
                    reply_markup=None, parse_mode="Markdown"
                )
            except Exception:
                await callback.message.answer(
                    "🧾 *Seller Premium Payment*\n\n"
                    f"Amount: {price} Br\n\n"
                    "Send payment to Telebirr: 0912345678 and send receipt.",
                    parse_mode="Markdown"
                )

        @self.router.callback_query(F.data == "cancel")
        async def cb_cancel(callback: CallbackQuery, lang: str):
            # Safely answer immediately to prevent Telegram query expiration timeouts
            try:
                await callback.answer()
            except Exception:
                pass  # Ignore if the query has already timed out or is invalid

            try:
                await callback.message.edit_text(
                    "Cancelled." if lang == 'en' else "ተሰርዟል።",
                    reply_markup=main_menu(lang)
                )
            except Exception:
                await callback.message.answer("Cancelled." if lang == 'en' else "ተሰርዟል።")

    def _register_errors(self):
        async def error_handler(event: ErrorEvent):
            exception = event.exception
            logger.error(f"Error: {exception}", exc_info=True)
            if isinstance(event.update, Message):
                await event.update.answer("❌ An error occurred. Please try again.")
        self.dp.errors.register(error_handler)

    async def _perform_search(self, message: Message, query: str, db: Database, user: dict, lang: str):
        await db.execute(
            "INSERT INTO search_logs (user_id, query) VALUES (?, ?)",
            (user['id'], query)
        )
        items, total = await self.services.item.search_items(
            query=query, user_lat=user.get('latitude'), user_lon=user.get('longitude'), limit=20
        )
        await self._display_results(message, items, total, lang, query)

    async def _display_results(self, message: Message, items: list, total: int, lang: str, query: str):
        if not items:
            text = (
                f"🔍 No results found for '{query}'.\nTry a different search term."
                if lang == 'en' else f"🔍 ለ '{query}' የፍለጋ ውጤት አልተገኘም። ሌላ ቃል ይሞክሩ።"
            )
            await message.answer(text, reply_markup=main_menu(lang))
            return

        parts = [f"🔍 *Results for '{query}'* ({total} found)\n"] if lang == 'en' \
            else [f"🔍 *የ '{query}' ፍለጋ ውጤቶች* ({total} ተገኝተዋል)\n"]
        for item in items[:10]:
            name = item['name_am'] if lang == 'am' else item['name_en']
            dist = f"📍{item.get('distance_km', 'N/A')}km" if item.get('distance_km') else ""
            parts.append(
                f"• {name}: {item['price']} {item['unit']} ({item['shop_name']}) {dist}"
            )

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🔍 New Search", callback_data="search_again")
        keyboard.button(text="📋 Categories", callback_data="categories")
        keyboard.button(text="❌ Done", callback_data="cancel")

        await message.answer("\n".join(parts), reply_markup=keyboard.as_markup(), parse_mode="Markdown")

    async def run(self):
        self.register_handlers()
        await self.dp.start_polling(self.bot, handle_signals=False)


async def main():
    global config, BOT_TOKEN, ADMIN_IDS, DB_PATH
    config = load_config()
    BOT_TOKEN = config.BOT_TOKEN
    ADMIN_IDS = config.ADMIN_IDS
    DB_PATH = config.DB_PATH

    bot = AddisSukBot()
    try:
        logger.info("Starting Addis Suk Bot...")
        await bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"{e}")
        sys.exit(1)