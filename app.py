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
import gradio as gr

# Setup logging to output cleanly to Hugging Face Spaces log tab
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout,
)
logger = logging.getLogger('addis_suk')

PORT = int(os.environ.get('PORT', 7860))

# 1. Simple Status Web Interface (Required by HF Spaces to keep container awake)
def get_bot_status():
    bot_configured = "Configured (OK)" if os.getenv('BOT_TOKEN') else "Missing BOT_TOKEN"
    db_path = Path(__file__).parent / 'data' / 'addis_suk.db'
    db_status = "Initialized (OK)" if db_path.exists() else "Not created yet"
    
    return f"""
    🤖 Addis Suk Bot Status
    -----------------------------
    Status: Running 🟢
    Telegram Polling: Active
    Bot Token: {bot_configured}
    Database: {db_status}
    Platform: Hugging Face Spaces
    """

with gr.Blocks(title="Addis Suk Bot Dashboard") as demo:
    gr.Markdown("# 🇪🇹 Addis Suk Bot Control Panel")
    status_output = gr.Textbox(
        label="System Diagnostics", 
        value=get_bot_status(), 
        lines=8,
        interactive=False
    )
    refresh_btn = gr.Button("Refresh Status")
    refresh_btn.click(fn=get_bot_status, inputs=None, outputs=status_output)

# 2. Background worker wrapper for your Telegram bot loop
def run_telegram_bot():
    if not os.getenv('BOT_TOKEN'):
        logger.error('CRITICAL: BOT_TOKEN environment variable not set. Telegram bot aborted.')
        return
        
    logger.info('Initializing Addis Suk Bot Async Loop...')
    from src.bot import main as bot_main
    
    try:
        # Create an isolated event loop for this specific background thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_main())
    except Exception as e:
        logger.critical(f'Bot polling thread crashed: {e}', exc_info=True)

# 3. Main orchestration initialization logic
def start_application():
    logger.info(f'Launching Addis Suk Bot Engine on Port {PORT}...')
    
    # Fire up the Telegram bot in an isolated daemon thread
    if os.getenv('BOT_TOKEN'):
        bot_thread = threading.Thread(target=run_telegram_bot, name="TelegramBotThread", daemon=True)
        bot_thread.start()
        logger.info('Telegram bot polling successfully spawned in background thread.')
    
    # Launch Gradio interface (This blocks the main thread and satisfies HF Space requirements)
    demo.launch(
        server_name='0.0.0.0', 
        server_port=PORT,
        show_api=False,
        quiet=True
    )

if __name__ == '__main__':
    start_application()
