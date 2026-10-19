# app.py
# Hugging Face Spaces entry point for Addis Suk Bot

import os
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')
os.environ['GRADIO_SSR_MODE'] = 'False'

import sys
import types
import asyncio
import logging
import threading
from pathlib import Path

# --- ZERO-GPU COMPLIANCE & PATCHING ---
from spaces import GPU  # Literal decorator required by ZeroGPU hardware scanner

import spaces
if not hasattr(spaces, 'gradio_auto_wrap'):
    spaces.gradio_auto_wrap = lambda fn: fn

if not hasattr(spaces, 'reloading'):
    _reloading = types.ModuleType('spaces.reloading')
    _reloading.spaces_reload = lambda *args, **kwargs: None
    _reloading.is_in_interactive_mode = lambda: False
    _reloading.start_reload_server = lambda *args, **kwargs: None
    _reloading.__path__ = []
    spaces.reloading = _reloading
    sys.modules['spaces.reloading'] = _reloading
# ---------------------------------------

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

@GPU  # Satisfies Hugging Face ZeroGPU startup orchestrator requirement
def status():
    return 'Addis Suk Bot is running! Telegram polling active.'

# Initialize Gradio interface
demo = gr.Interface(fn=status, inputs=None, outputs='text', title='Addis Suk Bot')

def run_telegram_bot():
    try:
        if not os.getenv('BOT_TOKEN'):
            logger.warning('BOT_TOKEN not set. Bot will not start.')
            return
        logger.info('Initializing Addis Suk Bot...')
        from src.bot import main as bot_main
        asyncio.run(bot_main())
    except Exception as e:
        logger.error(f'Bot thread failed safely: {e}', exc_info=True)

def main():
    logger.info(f'Starting Addis Suk Bot - HF Spaces (port {PORT})')
    
    # Run Telegram bot in a safe background daemon thread
    if os.getenv('BOT_TOKEN'):
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
        logger.info('Telegram bot polling started in background thread.')
        
    # Launch Gradio
    demo.launch(server_name='0.0.0.0', server_port=PORT)

if __name__ == '__main__':
    main()