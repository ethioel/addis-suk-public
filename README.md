# Addis Suk Bot 🛒

**Telegram price comparison for Ethiopian local markets.**

> "Know the price, save your money."
> "ዋጋውን ይወቁ፣ ገንዘብዎን ይቆጥቡ።"

## 🚀 Use it now

**👉 Open [@AddisSukbot](https://t.me/AddisSukbot) on Telegram and press Start.**

No app to install — everything happens inside Telegram, in English or አማርኛ.

## 🤝 How to use it

**As a buyer:**
1. Send `/start` and pick your language
2. Type what you need — `/search tomato` — or tap 🔍 Search
3. Share your location (or pick your city) and get `/nearby` results with distances
4. Compare prices in clean tables, with 📈/📉 30-day trend arrows
5. Buy several things? `/basket tomato onion shiro` finds the cheapest single shop

**As a seller:**
1. `/register` — shop name, address, phone, city
2. `/add rice 80 kg` — list your items with prices
3. `/setlocation` — drop your GPS pin so nearby buyers find you
4. Go premium for `/analytics`, `/promote` broadcasts and the ✅ verified badge

Premium payments: `/verify_payment` and send your receipt — confirmed by an admin.

## ✨ Highlights

- 📍 GPS **and** manual city picker — 10 cities, Addis Ababa with 19 sub-cities
- 📊 Native Telegram tables — price, shop, distance and trend in one view
- 🧺 `/basket` — cheapest single shop for your whole shopping list
- 🔔 Price alerts that actually fire · ⭐ favorites · 📊 price history (premium)
- ↗️ Share any result to any chat · 🤖 inline mode — type `@AddisSukbot tomato` anywhere
- 🎁 Referrals — you and your friend each get 7 days of premium
- ⚠️ Report wrong prices — community keeps listings honest

## 💰 Premium

| | Buyer — 100 Br/mo | Seller — 250 Br/mo |
|---|---|---|
| | Unlimited searches · alerts · favorites · price history · ad-free | Unlimited items · featured placement · analytics · verified badge · `/promote` |

## 🛠️ Run your own copy

Forking is enough — this repo deploys itself to Hugging Face Spaces (Gradio, free tier, zero GPU).

1. Fork this repo → create a Space from it (or your own host)
2. Add two secrets: `BOT_TOKEN` (from [@BotFather](https://t.me/BotFather)) and `ADMIN_IDS` (your Telegram ID)
3. That's it — the bot builds and starts polling

Optionally set `DB_PATH` to a mounted volume so data survives redeploys. Admins can extend cities with `/addcity` and manage everything from `/admin`.

```bash
# Local development
pip install -r requirements.txt
python -m pytest tests/ -q   # 64 tests
python app.py
```

---

_Made with ❤️ for the Ethiopian market_
