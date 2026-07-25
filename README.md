# Addis Suk Bot Framework

**A Telegram bot framework for price comparison.**

---

## About

This is the public framework for the Addis Suk price comparison system.

### 🔒 Important

This repository contains the **public wrapper only**.

- **Core business logic** is distributed separately
- **Production deployment** requires a license
- **Commercial use** is prohibited without permission

---

## Quick Start

```bash
git clone https://github.com/ethioel/addis-suk-public.git
cd addis-suk-public
pip install -r requirements.txt
cp .env.example .env
# Fill in your BOT_TOKEN and ADMIN_IDS
python src/bot.py
