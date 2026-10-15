from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Tuple, Optional


def create_keyboard(rows: List[List[Tuple[str, str]]],
                    resize_keyboard: bool = True,
                    one_time_keyboard: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for row in rows:
        for text, callback in row:
            builder.button(text=text, callback_data=callback)
    
    return builder.as_markup()
    
    
def main_menu(lang: str = 'en') -> InlineKeyboardMarkup:
    rows = [
        [('🔍 Search', 'search'), ('📋 Categories', 'categories')],
        [('📍 Nearby', 'nearby'), ('⚙️ Settings', 'settings')],
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
        [('📈 Stats', 'admin_stats'), ('⚙️ Settings', 'admin_settings')],
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
    favorite_text = "⭐ Favorite" if lang == 'en' else "⭐ የተመረጡ"
    builder.button(text=delete_text, callback_data=f"delete_item_{item_id}")
    builder.button(text=favorite_text, callback_data=f"fav_{item_id}")
    builder.button(text="❌ Cancel", callback_data="cancel")
    return builder.as_markup()


def location_menu(lang: str = 'en') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    share_text = "📍 Share Location" if lang == 'en' else "📍 መገኛዎን ይላኩ"
    builder.button(text=share_text, request_location=True)
    builder.button(text="❌ Cancel", callback_data="cancel")
    return builder.as_markup()