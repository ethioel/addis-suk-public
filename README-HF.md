# Hugging Face Spaces Configuration for Addis Suk Bot

# This file is read by HF Spaces to configure the deployment
# Place this file in the root as .safetensors or spaces.yaml equivalent
# HF Spaces uses the presence of app.py or similar to detect Python apps

# Create a README for HF Spaces visibility
# HF Spaces automatically detects and displays the repository README

# The app.py file already contains the HF-optimized implementation:
# - Runs both web server (for HF health checks) and Telegram bot (polling)
# - Uses minimal dependencies
# - Optimized for CPU-only execution
# - Includes graceful error handling
# - Has proper logging for HF Spaces logs

# No additional configuration files needed - HF Spaces will:
# 1. Install from requirements.txt
# 2. Run the command specified in the README or detect the Python app
# 3. Provide logs and monitoring
# 4. Auto-restart on crashes
# 5. Provide environment variable storage via Secrets

# To deploy:
# 1. Create new Space on huggingface.co
# 2. Connect this repository
# 3. Set Secrets: BOT_TOKEN, ADMIN_IDS
# 4. Wait for build and deployment
# 5. Bot will be live and polling Telegram