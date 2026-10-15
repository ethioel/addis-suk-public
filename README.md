# Addis Suk Bot

**A Telegram-based price comparison platform connecting Ethiopian consumers with local sellers.**

---

## 🚀 Deploy on Hugging Face Spaces

This bot is optimized for **Hugging Face Spaces** (free tier, zero GPU required).

### Quick Deploy

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose "Python" SDK
3. Connect this repository
4. Set the following **Secrets** in your Space settings:
   - `BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
   - `ADMIN_IDS` - Comma-separated Telegram user IDs of admins

5. Click "Create Space" - the bot will auto-deploy!

### Environment Variables

Set via HF Spaces secrets:

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |
| `ADMIN_IDS` | ✅ | Comma-separated list of admin Telegram IDs |
| `LOG_LEVEL` | ❌ | Logging level (default: INFO) |
| `SEARCH_RADIUS_KM` | ❌ | Default search radius (default: 10) |

All other configuration uses defaults from `src/config.py`.

---

## 📋 Features

### For Buyers
- 🔍 Price search across local sellers
- 📋 Category browsing (Vegetables, Fruits, Meat, etc.)
- 📍 Location-based seller discovery
- 💰 Price comparison across multiple sellers
- 🌍 Bilingual: Amharic (አማርኛ) & English

### Premium Features (100 Br/month)
- ⭐ Unlimited searches (5/day free)
- 🔔 Price drop alerts
- 📋 Favorites
- 📊 Price history (30 days)

### For Sellers
- 📝 Shop registration
- 📋 Item listing management
- 📍 GPS location sharing
- 💰 Real-time price updates

### Admin Tools
- ✅ Seller approval
- 🔍 Price moderation
- 📢 Broadcast messaging
- 📊 Analytics dashboard
- 💰 Revenue tracking

---

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/search [item]` | Search prices |
| `/categories` | Browse categories |
| `/nearby [item]` | Find nearby sellers |
| `/register` | Register as seller |
| `/add [item] [price] [unit]` | Add item |
| `/subscribe` | Upgrade to premium |
| `/admin` | Admin dashboard |

---

## 💰 Revenue Model

### Buyer Premium - 100 Br/month
- Unlimited searches
- Price alerts (10 items)
- Favorites
- Price history (30 days)
- Ad-free experience

### Seller Premium - 250 Br/month
- Unlimited items
- Featured listings
- Full analytics
- Verified badge
- Bulk discounts

---

## 📍 Supported Cities

✅ Addis Ababa | ✅ Bahir Dar | ✅ Gondar | ✅ Mekelle | ✅ Hawassa | ✅ Dire Dawa | ✅ Jimma | ✅ Harar | ✅ Adama

---

## 🛠️ Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env with your BOT_TOKEN and ADMIN_IDS

# Run locally
python app.py
# Or: python -m src.bot
```

---

## 📄 License

MIT License - see [LICENSE.md](LICENSE.md)

---

_Made with ❤️ for the Ethiopian market_