from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Tuple, Optional


def create_keyboard(rows: List[List[Tuple[str, str]]],
                    resize_keyboard: bool = True,
                    one_time_keyboard: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for row in rows:
        for text, callback in row:
            builder.button(text=text, callback_data=callback)
    
    # Adjust row sizes based on the input rows
    if rows:
        builder.adjust(*[len(row) for row in rows])
    
    return builder.as_markup()
    
    
def main_menu(lang: str = 'en') -> InlineKeyboardMarkup:
    rows = [
        [('🔍 Search', 'search'), ('📋 Categories', 'categories')],
        [('📍 Nearby', 'nearby'), ('⚙️ Settings', 'settings')],
    ]
    return create_keyboard(rows)


def settings_menu(lang: str = 'en') -> InlineKeyboardMarkup:
    rows = [
        [('🌍 Language', 'settings_language'), ('⭐ Premium', 'settings_premium')],
        [('📰 Weekly Digest', 'digest_toggle')],
        [('❌ Cancel', 'cancel')],
    ]
    return create_keyboard(rows)


def language_selector() -> InlineKeyboardMarkup:
    rows = [
        [('English', 'lang_en'), ('አማርኛ', 'lang_am')],
        [('Cancel', 'cancel')],
    ]
    return create_keyboard(rows)


def search_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [('🌿 Vegetables', 'cat_vegetables'), ('🍎 Fruits', 'cat_fruits')],
        [('🥩 Meat', 'cat_meat'), ('🥛 Dairy', 'cat_dairy')],
        [('🍞 Bakery', 'cat_bakery'), ('☕ Coffee', 'cat_coffee')],
        [('🧴 Household', 'cat_household'), ('❌ Cancel', 'cancel')],
    ]
    return create_keyboard(rows)


def category_keyboard(categories: List[Tuple[str, str, str]], 
                      lang: str = 'en') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for emoji, name_en, name_am in categories:
        button_text = f"{emoji} {name_am if lang == 'am' else name_en}"
        builder.button(text=button_text, callback_data=f'cat_select_{name_en}')
    
    builder.button(text='❌ Cancel', callback_data='cancel')
    return builder.as_markup()


def seller_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [('📝 Register', 'register'), ('📋 My Listings', 'mylistings')],
        [('📍 Set Location', 'setlocation'), ('💰 Premium', 'premium')],
        [('❌ Cancel', 'cancel')],
    ]
    return create_keyboard(rows)


def admin_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [('📊 Dashboard', 'admin_dashboard'), ('👥 Users', 'admin_users')],
        [('💰 Revenue', 'admin_earnings'), ('📢 Broadcast', 'admin_broadcast')],
        [('📈 Stats', 'admin_stats'), ('⚠️ Reports', 'admin_reports')],
        [('⚙️ Settings', 'admin_settings')],
    ]
    return create_keyboard(rows)


def yes_no_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [('✅ Yes', 'yes'), ('❌ No', 'no')],
    ]
    return create_keyboard(rows)


def subscription_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [('💰 Buyer Premium - 100 Br/month', 'buy_premium_buyer'), 
         ('💰 Seller Premium - 250 Br/month', 'sell_premium_seller')],
        [('❌ Skip', 'skip')],
    ]
    return create_keyboard(rows)


def featured_listing_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [('50 Br/day - Top placement', 'featured_1day'), 
         ('30 Br/day - Standard', 'featured_30day')],
        [('❌ Skip', 'skip')],
    ]
    return create_keyboard(rows)


def pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if current_page > 1:
        builder.button(text="⬅️ Previous", callback_data=f"page_{current_page - 1}")
    
    builder.button(text=f"📄 {current_page}/{total_pages}", callback_data="page_info")
    
    if current_page < total_pages:
        builder.button(text="Next ➡️", callback_data=f"page_{current_page + 1}")
    
    builder.button(text="❌ Cancel", callback_data="cancel")
    return builder.as_markup()


def seller_listing_keyboard(item_id: int, lang: str = 'en') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    delete_text = "🗑 Delete" if lang == 'en' else "🗑 ሰርዝ"
    favorite_text = "⭐ Favorite" if lang == 'en' else "⭐ ተወዳጅ"
    builder.button(text=delete_text, callback_data=f"delete_item_{item_id}")
    builder.button(text=favorite_text, callback_data=f"fav_{item_id}")
    builder.button(text="❌ Cancel", callback_data="cancel")
    return builder.as_markup()


def location_menu(lang: str = 'en') -> ReplyKeyboardMarkup:
    share_text = "📍 Share Location" if lang == 'en' else "📍 መገኛዎን ይላኩ"
    manual_text = "🏙️ Choose City" if lang == 'en' else "🏙️ ከተማ ይምረጡ"
    cancel_text = "❌ Cancel" if lang == 'en' else "❌ ሰርዝ"
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=share_text, request_location=True)],
            [KeyboardButton(text=manual_text)],
            [KeyboardButton(text=cancel_text)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


LOCATION_MANUAL_TEXT = "🏙️ Choose City"
LOCATION_MANUAL_TEXT_AM = "🏙️ ከተማ ይምረጡ"
LOCATION_CANCEL_TEXT = "❌ Cancel"
LOCATION_CANCEL_TEXT_AM = "❌ ሰርዝ"


def cities_keyboard(city_names: List[str], city_names_am: List[str],
                    lang: str = 'en') -> InlineKeyboardMarkup:
    """One button per city, 2 per row. callback: loc_city_<index>."""
    builder = InlineKeyboardBuilder()
    names = city_names_am if lang == 'am' else city_names
    for i, name in enumerate(names):
        builder.button(text=f"🏙 {name}", callback_data=f"loc_city_{i}")
    builder.button(text="❌ Cancel", callback_data="cancel")
    builder.adjust(2, 2, 2, 2, 2, 1)
    return builder.as_markup()


def subcities_keyboard(subcity_names: List[str],
                       lang: str = 'en') -> InlineKeyboardMarkup:
    """One button per sub-city/neighborhood, 2 per row. callback: loc_sub_<index>."""
    builder = InlineKeyboardBuilder()
    for i, name in enumerate(subcity_names):
        builder.button(text=f"📍 {name}", callback_data=f"loc_sub_{i}")
    builder.button(text="⬅️ Back", callback_data="loc_back_cities")
    builder.button(text="❌ Cancel", callback_data="cancel")
    builder.adjust(2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1)
    return builder.as_markup()