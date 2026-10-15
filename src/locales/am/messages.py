# src/locales/am/messages.py
# Amharic localization

from typing import Dict

class Messages:
    WELCOME = "እንኳን ወደ አዲስ ሱቅ በደህና መጡ! 🛒"
    WELCOME_BACK = "እንኳን ደህና መጡ! 👋"
    
    START_DESCRIPTION = " ከአካባቢው ኢትዮጵያውያን ሻጮች ምርጥ የአትክልት፣ ፍራፍሬ፣ ሥጋ እና ሌሎች ምርቶች ዋጋ በቀላሉ ያግኙ።"
    
    SEARCH_PLACEHOLDER = "ዕቃዎችን ይፈልጉ (ለምሳሌ፦ ቲማቲም፣ ሽንኩርት፣ ዶሮ)..."
    CATEGORIES = "ምድቦችን ያስሱ"
    NEARBY = "አቅራቢያ ያሉትን ፈልግ"
    HELP = "እርዳታ"
    ABOUT = "ስለ እኛ"
    
    # User commands
    SEARCH_HELP = "የዕቃዎችን ዋጋ ለመፈለግ፦ /search ቲማቲም"
    CATEGORIES_HELP = "የምርት ምድቦችን ለማሰስ።"
    NEARBY_HELP = "በአቅራቢያዎ የሚገኙ ሻጮችን ለማግኘት።"
    
    # Seller commands
    REGISTER_PROMPT = "ለመመዝገብ እባክዎ የሱቅዎን ስም፣ አድራሻ፣ ስልክ ቁጥር እና ከተማ ይሙሉ፡፡"
    REGISTER_SUCCESS = "✅ ሱቅዎ በተሳካ ሁኔታ ተመዝግቧል!"
    REGISTER_FAILED = "❌ ምዝገባው አልተሳካም። እባክዎ እንደገና ይሞክሩ።"
    
    # Admin commands
    ADMIN_DASHBOARD = "📊 የአስተዳዳሪ ዳሽቦርድ"
    APPROVE_SELLER = "ሻጭ አጽድቅ"
    REJECT_SELLER = "ሻጭ ውድቅ አድርግ"
    BROADCAST = "መልእክት አስተላልፍ"
    STATS = "ስታቲስቲክስ"
    EARNINGS = "ገቢ"