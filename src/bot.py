# src/bot.py
# Public Wrapper (Core logic is NOT here)

import logging
import os
import sys
from pathlib import Path

# Import from compiled module (not included in public repo)
try:
    # This would be a compiled .so/.pyd file in production
    from addis_suk_core import AddisSukBot
except ImportError:
    logging.warning("⚠️ Core module not found. Running in demo mode.")
    # Fallback to basic demo
    from demo import DemoBot as AddisSukBot

from src.config import BOT_TOKEN, ADMIN_IDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run the bot - core logic is in compiled module"""
    logger.info("🚀 Starting Addis Suk Bot (Public Wrapper)")
    logger.info("📡 Core logic loaded from external module")
    
    bot = AddisSukBot(
        token=BOT_TOKEN,
        admins=ADMIN_IDS,
        mode="public"  # Limited mode
    )
    
    await bot.run()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Stopped")
    except Exception as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
