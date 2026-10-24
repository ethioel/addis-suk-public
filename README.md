---
title: Addis Suk Bot
emoji: 🛒
colorFrom: indigo
colorTo: pink
sdk: gradio
sdk_version: 6.30.0
app_file: app.py
pinned: false
---

# Addis Suk Bot 🛒

**A Telegram-based price comparison platform connecting Ethiopian consumers with local sellers.**

> “Know the price, save your money.”
> “ዋጋውን ይወቁ፣ ገንዘብዎን ይቆጥቡ።”

---

## 🚀 Deploy on Hugging Face Spaces

This bot runs on **Hugging Face Spaces** (free tier, zero GPU) with a Gradio dashboard and the Telegram bot on long polling.

### Quick Deploy

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose **Gradio** SDK and connect this repository
3. Set the following **Secrets** in your Space settings:
   - `BOT_TOKEN` — get from [@BotFather](https://t.me/BotFather)
   - `ADMIN_IDS` — comma-separated Telegram user IDs of admins
4. (Recommended) Enable **persistent storage** on the Space, or set `DB_PATH` — the local database is wiped on every redeploy otherwise
5. Click "Create Space" — the bot auto-deploys

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |
| `ADMIN_IDS` | ✅ | Comma-separated list of admin Telegram IDs |
| `DB_PATH` | ❌ | Database file path (e.g. `/data/addis_suk.db` for HF persistent storage) |
| `LOG_LEVEL` | ❌ | Logging level (default: `INFO`) |
| `SEARCH_RADIUS_KM` | ❌ | Default nearby-search radius (default: `10`) |

For **inline mode** (`@yourbot tomato` in any chat), enable Inline Mode in @BotFather → Bot Settings.

---

## ✨ Features

### For Buyers
- 🔍 Smart price search — ranked by distance, price, relevance and freshness
- 📋 10 logical market categories — Vegetables, Fruits, Meat & Poultry, Dairy & Eggs, Grains & Pulses, Spices & Oil, Bakery & Injera, Coffee/Tea & Drinks, Snacks & Sweets, Household & Care
- 📍 Location-based discovery — GPS **and** manual city/sub-city picker
- 📊 Native Telegram tables with 📈/📉 30-day price trend indicators
- 🧺 `/basket` — finds the cheapest single shop for a whole shopping list
- 📄 Paginated results with best-price footer
- ⚠️ "Report wrong price" community moderation
- ↗️ Shareable deep links (`t.me/<bot>?start=item_<id>`)
- 🌍 Bilingual: Amharic (አማርኛ) & English
- 💎 Premium tier with referrals (both sides get 7 free days)

### For Sellers
- 📝 Self-registration (shop, address, phone, city)
- 📦 Item listing with units, admin-approved price updates
- 📍 Shop GPS pin (separate from buyer location)
- 📊 `/analytics` (premium) — shop views, contact clicks, item status
- ⭐ Verified badge (admin-granted, shown everywhere)
- 📢 `/promote` (premium) — broadcast deals to buyers in your city
- 📦 Stale-listing reminders — sellers with 14+ day-old prices get nudged

### For Admin
- ✅ Approve/reject sellers, items and price updates
- 💎 `/approve_premium [txn_id]` — activate premium payments
- ⭐ `/verify_seller [id]` — grant the verified badge
- 📍 `/addcity`, `/addsubcity`, `/dellocation`, `/listlocations` — manage locations (rendered as native Telegram tables)
- ⚠️ `/reports` — open price-report queue
- 📢 Broadcast to all users
- 📊 Dashboard, user stats and revenue — as commands *and* working inline-keyboard buttons

### Platform
- 🤖 Inline query mode — search prices from any chat
- 📰 Weekly digest — cheapest staple prices, opt-out in Settings
- 🔔 Automatic price-alert engine (alerts fire and deactivate)
- 🧱 Schema migrations — new columns/tables are added to existing databases on startup
- 💾 Configurable `DB_PATH` for persistent storage on HF Spaces

---

## 🛠️ Commands

### Buyers
| Command | Description |
|---------|-------------|
| `/start` | Welcome + language picker (`item_<id>` / `ref_<id>` deep links) |
| `/search [item]` | Search prices across sellers |
| `/categories` | Browse the 10 categories |
| `/nearby [item]` | Find nearby sellers (GPS or manual location) |
| `/basket [items]` | Cheapest shop for a whole shopping list |
| `/subscribe` | Upgrade to premium |
| `/favorites` | View favorites (premium) |
| `/alert [item] [price]` · `/alerts` | Price alerts (premium) |
| `/history [item]` | 30-day price history (premium) |
| `/verify_payment` | Send a payment receipt screenshot |
| `/setlocation` | Share GPS or pick a city manually |
| `/cancel` | Cancel the current action |

### Sellers
| Command | Description |
|---------|-------------|
| `/register` | Register your shop (FSM flow) |
| `/add [item] [price] [unit]` · `/additem` | Add an item |
| `/update [item] [price]` | Update price (re-enters moderation) |
| `/delete [item]` | Remove a listing |
| `/mylistings` | View your listings |
| `/setlocation` | Save your shop's GPS pin |
| `/analytics` | Shop views, contact clicks, item status (premium) |
| `/promote` | Broadcast a deal to buyers in your city (premium) |

### Admin
| Command | Description |
|---------|-------------|
| `/admin` | Dashboard (with working button panel) |
| `/approve_seller [id]` · `/reject [id] [reason]` | Moderate sellers |
| `/approve_price [id]` | Approve pending items/price updates |
| `/approve_premium [txn_id]` | Confirm a premium payment |
| `/verify_seller [id]` | Grant the ✅ verified badge |
| `/reports` | Open price reports |
| `/broadcast` | Message all users |
| `/stats` · `/earnings` | Usage stats · revenue |
| `/addcity <lat> <lon> <Name> [| <Amharic>]` | Add a city |
| `/addsubcity <lat> <lon> <Name>` | Add an Addis Ababa sub-city |
| `/dellocation <name>` | Remove a custom location |
| `/listlocations` | List all locations (native table) |

---

## 💰 Revenue Model

**Buyer Premium — 100 Br/month:** unlimited searches · price alerts (10) · favorites · 30-day price history · ad-free

**Seller Premium — 250 Br/month:** unlimited items · featured listings · full analytics · verified badge · bulk discounts · promotional broadcasts

**Referrals:** both referrer and new user get 7 days of premium.

Payment verification: pay, then `/verify_payment` and send the receipt; an admin confirms with `/approve_premium`.

---

## 📍 Supported Cities

✅ Addis Ababa (19 sub-cities) | ✅ Bahir Dar | ✅ Gondar | ✅ Mekelle | ✅ Hawassa | ✅ Dire Dawa | ✅ Jimma | ✅ Harar | ✅ Debre Zeyit | ✅ Adama

Admins can add more at any time with `/addcity` — custom locations appear in the city picker automatically.

---

## 🛠️ Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env with your BOT_TOKEN and ADMIN_IDS

# Run tests (64 tests)
python -m pytest tests/ -q

# Run locally
python app.py
# Or: python -m src.bot
```

**Project structure**

```
app.py                  # HF Spaces entry point (Gradio + polling thread)
src/bot.py              # Handlers, FSM, rich tables, pagination, jobs
src/keyboards/          # Keyboard builders (menus, city picker, admin panel)
src/services/           # User/Seller/Item/Favorite/Alert business logic
src/models/database.py  # Schema, migrations, category taxonomy
src/middleware/         # DB, localization, user (auto-create), rate limit
src/seed_data.py        # Demo shops/items (bilingual, category-safe)
src/locales/            # i18n strings (en/am)
tests/                  # 64 tests: services, keyboards, migrations, regressions
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

_Made with ❤️ for the Ethiopian market_
