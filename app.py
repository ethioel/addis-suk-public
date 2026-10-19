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

# Gradio interface for HF Spaces
import gradio as gr

def status():
    return 'Addis Suk Bot is running! Telegram polling active.'

demo = gr.Interface(fn=status, inputs=None, outputs='text', title='Addis Suk Bot')

# Flask app for health checks
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

def run_telegram_bot():
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
    # Run Telegram bot in background thread
    if os.getenv('BOT_TOKEN'):
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
        logger.info('Telegram bot polling started in background thread.')
    # Launch Gradio (HF Spaces expects this)
    demo.launch(server_name='0.0.0.0', server_port=PORT)

if __name__ == '__main__':
    main()
else:
    main()
