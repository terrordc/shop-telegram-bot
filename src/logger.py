# src/logger.py

import logging
import traceback
from aiogram import Bot

# This should be your personal Telegram user ID to receive logs
ADMIN_ID = 347242473 # <-- IMPORTANT: Replace with YOUR admin ID

class TelegramBotHandler(logging.Handler):
    def __init__(self, bot_instance: Bot):
        super().__init__()
        self.bot = bot_instance

    def emit(self, record: logging.LogRecord):
        # Format the log message
        log_entry = self.format(record)
        
        # We only want to send critical errors to Telegram
        if record.levelno >= logging.ERROR:
            # Prepare a clean traceback if it exists
            if record.exc_info:
                tb = traceback.format_exception(*record.exc_info)
                log_entry += "\n\n" + "".join(tb)
            
            # Send the message
            try:
                # We use a coroutine, so we need to schedule it
                import asyncio
                # Truncate the message if it's too long for Telegram
                message_text = f"🚨 **BOT ERROR** 🚨\n\n`{log_entry[:4000]}`"
                asyncio.create_task(self.bot.send_message(
                    ADMIN_ID,
                    text=message_text,
                    parse_mode="Markdown"
                ))
            except Exception as e:
                print(f"Failed to send log to Telegram: {e}")

def setup_logger(bot_instance: Bot):
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Set the minimum level to capture

    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create a handler to print to console (for journalctl)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create our custom handler to send errors to Telegram
    telegram_handler = TelegramBotHandler(bot_instance)
    telegram_formatter = logging.Formatter('%(levelname)s - %(message)s')
    telegram_handler.setFormatter(telegram_formatter)
    # Only send ERROR and CRITICAL level messages to Telegram
    telegram_handler.setLevel(logging.ERROR)
    logger.addHandler(telegram_handler)

    print("✅ Logger setup complete. Errors will be sent to the admin.")