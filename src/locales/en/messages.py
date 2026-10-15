# src/locales/en/messages.py
# English localization

from typing import Dict

class Messages:
    WELCOME = "Welcome to Addis Suk! 🛒"
    WELCOME_BACK = "Welcome back! 👋"
    
    START_DESCRIPTION = "Find the best prices on vegetables, fruits, meat and more from local Ethiopian sellers."
    
    SEARCH_PLACEHOLDER = "Search for items (e.g., tomato, onion, chicken)..."
    CATEGORIES = "Browse Categories"
    NEARBY = "Find Nearby"
    HELP = "Help"
    ABOUT = "About"
    
    # User commands
    SEARCH_HELP = "Search for prices of items. Example: /search tomato"
    CATEGORIES_HELP = "Browse product categories."
    NEARBY_HELP = "Find sellers near your location."
    
    # Seller commands
    REGISTER_PROMPT = "Please provide your shop name, address, phone number and city to register."
    REGISTER_SUCCESS = "✅ Your shop has been registered successfully!"
    REGISTER_FAILED = "❌ Registration failed. Please try again."
    
    # Admin commands
    ADMIN_DASHBOARD = "📊 Admin Dashboard"
    APPROVE_SELLER = "Approve Seller"
    REJECT_SELLER = "Reject Seller"
    BROADCAST = "Broadcast Message"
    STATS = "Statistics"
    EARNINGS = "Revenue"