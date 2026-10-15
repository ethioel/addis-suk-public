# HF Spaces config - minimal dependencies for free CPU
# Runs on Hugging Face Spaces with zero GPU

[build]
# Use Python 3.11
python_version = "3.11"

[run]
# Run as a worker process (background bot)
command = "python -m src.bot"
# HF Spaces uses uvicorn/gunicorn for web, but we need polling
# So we use the app.py with a web server + background worker

# For HuggingFace Spaces, create app.py that runs the bot in background
# or use webhook mode for lower resource usage

[env]
# Required environment variables
BOT_TOKEN = ""
ADMIN_IDS = ""