# app.py
# Hugging Face Spaces entry point for Addis Suk Bot
# Optimized for zero GPU / free HF Spaces tier
# Uses Flask web server for health checks + Telegram bot polling

import os
import sys
import asyncio
import logging
import threading
from pathlib import Path

# Configure logging early for HF Spaces
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout,
)
logger = logging.getLogger("addis_suk")

# HF Spaces port
PORT = int(os.environ.get("PORT", 7860))

# Initialize Flask app for health checks
from flask import Flask, jsonify

app = Flask(__name__)
_bot_task = None


@app.route("/")
def health_check():
    """HF Spaces health check endpoint."""
    return jsonify({"status": "ok", "service": "Addis Suk Bot", "version": "1.0.0"})


@app.route("/health")
def health_detailed():
    """Detailed health check."""
    data_dir = Path(__file__).parent / "data"
    return jsonify({
        "status": "healthy",
        "bot_configured": bool(os.getenv("BOT_TOKEN")),
        "database_exists": data_dir.exists(),
        "platform": "huggingface-spaces",
        "free_tier": True,
        "cpu_only": True
    })


@app.route("/metrics")
def metrics():
    """Metrics endpoint for monitoring."""
    return jsonify({
        "service": "addis-suk-bot",
        "version": "1.0.0",
        "platform": "huggingface-spaces",
        "free_tier": True,
        "cpu_only": True,
        "polling": True,
        "bilingual": True,
        "cities_supported": 10
    })


def run_telegram_bot():
    """Run the Telegram bot in a background thread."""
    global _bot_task
    
    if not os.getenv("BOT_TOKEN"):
        logger.warning("BOT_TOKEN not set. Bot will not start.")
        return
    
    logger.info("Initializing Addis Suk Bot...")
    
    # Import here to avoid blocking during HF build
    from src.bot import main as bot_main
    
    try:
        asyncio.run(bot_main())
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)


def main():
    """Start Flask web server and Telegram bot."""
    logger.info(f"Starting Addis Suk Bot - HF Spaces (port {PORT})")
    
    # Start Flask web server in background daemon thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=PORT, threaded=True),
        daemon=True
    )
    flask_thread.start()
    logger.info("Flask health check server started in background thread.")
    
    # Run Telegram bot polling in main thread (aiogram requires main thread for signal handlers)
    if os.getenv("BOT_TOKEN"):
        logger.info("Starting Telegram bot polling in main thread...")
        from src.bot import main as bot_main
        asyncio.run(bot_main())
    else:
        logger.warning("BOT_TOKEN not set. Only health check server will run.")


if __name__ == "__main__":
    main()
else:
    # Module loaded (for gunicorn or similar)
    main()