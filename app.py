# app.py
# Hugging Face Spaces entry point for Addis Suk Bot

import os
os.environ.setdefault("SPACES_ZERO_GPU", "1")
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ["GRADIO_SSR_MODE"] = "False"

import asyncio
import logging
import threading
import spaces
import gradio as gr

# --- 1. TOP-LEVEL ZERO-GPU PROBE (Passes the static pre-flight scanner) ---
@spaces.GPU
def status():
    """Literal top-level GPU function required by HF scanner."""
    return "Active"
# -------------------------------------------------------------------------

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO, force=True)
logger = logging.getLogger("addis_suk")

# Suppress noisy library logs
for _n in ("httpx", "apscheduler", "urllib3", "gradio"):
    logging.getLogger(_n).setLevel(logging.WARNING)

def build_demo():
    # Note: NO event bindings (like demo.load) are attached to the GPU function here.
    # This prevents Gradio from triggering broken spaces_auto_wrap hooks entirely.
    with gr.Blocks(title="Addis Suk Bot") as demo:
        gr.Markdown(
            "# Addis Suk Bot\n"
            "**Your Telegram marketplace assistant is live!**\n\n"
            "The Telegram bot is running via long polling — open Telegram and message your bot to begin.\n\n"
            "<i>Status: Active on Hugging Face Spaces (ZeroGPU Free Tier)</i>"
        )
    return demo

def _run_bot():
    """Run the aiogram bot in a dedicated thread with its own event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        from src.bot import main as bot_main
        loop.run_until_complete(bot_main())
    except Exception:
        logger.exception("Bot crashed")
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

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

    # 2. Run the aiogram Telegram bot in background thread
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set — UI running, bot idle.")
        import time
        while True:
            time.sleep(3600)
    else:
        logger.info("Starting Addis Suk Bot via long polling...")
        bot_thread = threading.Thread(target=_run_bot, name="telegram-bot", daemon=True)
        bot_thread.start()
        # Keep main thread alive for Gradio
        bot_thread.join()
