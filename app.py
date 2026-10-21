# app.py
# Hugging Face Spaces entry point for Addis Suk Bot

import os
os.environ.setdefault("SPACES_ZERO_GPU", "1")
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ["GRADIO_SSR_MODE"] = "False"

import asyncio
import logging

# --- 1. CLEAN ZERO-GPU IMPORT (Let spaces manage its own reloading internals) ---
import spaces

@spaces.GPU
def _zerogpu_probe():
    return "active"
# ------------------------------------------------------------------------------

import gradio as gr

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO, force=True)
logger = logging.getLogger("addis_suk")

# Suppress noisy library logs
for _n in ("httpx", "apscheduler", "urllib3", "gradio"):
    logging.getLogger(_n).setLevel(logging.WARNING)

def build_demo():
    with gr.Blocks(title="Addis Suk Bot") as demo:
        gr.Markdown(
            "# Addis Suk Bot\n"
            "**Your Telegram marketplace assistant is live!**\n\n"
            "The Telegram bot is running via long polling — open Telegram and message your bot to begin.\n\n"
            "<i>Status: Active on Hugging Face Spaces</i>"
        )
        
        # Hidden component to safely trigger the GPU probe initialization
        hidden_out = gr.Textbox(visible=False)
        demo.load(fn=_zerogpu_probe, inputs=None, outputs=hidden_out)
        
    return demo

if __name__ == "__main__":
    PORT = int(os.getenv("GRADIO_SERVER_PORT") or os.getenv("PORT") or 7860)
    
    # 1. Launch Gradio non-blocking
    demo = build_demo()
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT, 
        ssr_mode=False, 
        prevent_thread_lock=True
    )
    logger.info(f"Gradio dashboard successfully launched on port {PORT}")

    # 2. Run the aiogram Telegram bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set — UI running, bot idle.")
        import time
        while True:
            time.sleep(3600)
    else:
        logger.info("Starting Addis Suk Bot via long polling...")
        from src.bot import main as bot_main
        try:
            asyncio.run(bot_main())
        except KeyboardInterrupt:
            logger.info("Bot shutting down gracefully...")
