# app.py
# Hugging Face Spaces entry point for Addis Suk Bot

import os
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')

import sys
import asyncio
import logging
import threading
from pathlib import Path

try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(func):
            return func

@spaces.GPU
def _gpu_dummy():
    return None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout,
)
logger = logging.getLogger('addis_suk')

PORT = int(os.environ.get('PORT', 7860))

from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({'status': 'ok', 'service': 'Addis Suk Bot', 'version': '1.0.0'})

@app.route('/health')
def health_detailed():
    data_dir = Path(__file__).parent / 'data'
    return jsonify({
        'status': 'healthy',
        'bot_configured': bool(os.getenv('BOT_TOKEN')),
        'database_exists': data_dir.exists(),
        'platform': 'huggingface-spaces',
        'free_tier': True,
        'cpu_only': True
    })

@app.route('/metrics')
def metrics():
    return jsonify({
        'service': 'addis-suk-bot',
        'version': '1.0.0',
        'platform': 'huggingface-spaces',
        'free_tier': True,
        'cpu_only': True,
        'polling': True,
        'bilingual': True,
        'cities_supported': 10
    })

def run_telegram_bot():
    global _bot_task
    if not os.getenv('BOT_TOKEN'):
        logger.warning('BOT_TOKEN not set. Bot will not start.')
        return
    logger.info('Initializing Addis Suk Bot...')
    from src.bot import main as bot_main
    try:
        asyncio.run(bot_main())
    except Exception as e:
        logger.error(f'Bot error: {e}', exc_info=True)

def main():
    logger.info(f'Starting Addis Suk Bot - HF Spaces (port {PORT})')
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=PORT, threaded=True),
        daemon=True
    )
    flask_thread.start()
    logger.info('Flask health check server started in background thread.')
    if os.getenv('BOT_TOKEN'):
        logger.info('Starting Telegram bot polling in main thread...')
        from src.bot import main as bot_main
        asyncio.run(bot_main())
    else:
        logger.warning('BOT_TOKEN not set. Only health check server will run.')

if __name__ == '__main__':
    main()
else:
    main()
