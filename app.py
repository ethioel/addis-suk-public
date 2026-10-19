# app.py
# Hugging Face Spaces entry point for Addis Suk Bot

import os
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')

import sys
import types

# --- FOOLPROOF SPACES OVERRIDE (Must be before any gradio/other imports) ---
_spaces = types.ModuleType('spaces')
_spaces.GPU = lambda func=None, **kwargs: (func if func is not None else (lambda f: f))
_spaces.gradio_auto_wrap = lambda fn: fn
_spaces.__path__ = []

_reloading = types.ModuleType('spaces.reloading')
_reloading.spaces_reload = lambda *args, **kwargs: None
_reloading.is_in_interactive_mode = lambda: False
_reloading.start_reload_server = lambda *args, **kwargs: None
_reloading.__path__ = []

_spaces.reloading = _reloading
sys.modules['spaces'] = _spaces
sys.modules['spaces.reloading'] = _reloading
# --------------------------------------------------------------------------

import asyncio
import logging
import threading
from pathlib import Path
import gradio as gr

# Setup logging cleanly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout,
)
logger = logging.getLogger('addis_suk')

PORT = int(os.environ.get('PORT', 7860))

def status():
    return 'Addis Suk Bot is running! Telegram polling active.'

demo = gr.Interface(fn=status, inputs=None, outputs='text', title='Addis Suk Bot')

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
        
    # Launch Gradio cleanly as the main blocking process
    demo.launch(server_name='0.0.0.0', server_port=PORT)

if __name__ == '__main__':
    main()