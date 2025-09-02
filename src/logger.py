# src/logger.py - FINAL VERSION WITH ADVANCED EXCEPTION FILTER

import logging
import traceback
from aiogram import Bot
from aiohttp.http_exceptions import BadStatusLine # <-- Import the specific exception

ADMIN_ID = 347242473 # <-- Make sure this is your correct admin ID

# --- THIS IS THE NEW, SMARTER FILTER ---
class AdvancedAiohttpNoiseFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Check if there is an exception attached to the log record
        if record.exc_info:
            # Unpack the exception information
            exc_type, exc_value, exc_traceback = record.exc_info
            # Check if the exception is an instance of the specific error we want to ignore
            if isinstance(exc_value, BadStatusLine):
                return False # Returning False drops this log record completely.
        
        # For all other logs (or logs without exceptions), let them pass.
        return True
# --- END OF NEW FILTER ---


class TelegramBotHandler(logging.Handler):
    def __init__(self, bot_instance: Bot):
        super().__init__()
        self.bot = bot_instance

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        
        if record.levelno >= logging.ERROR:
            if record.exc_info:
                tb = traceback.format_exception(*record.exc_info)
                log_entry += "\n\n" + "".join(tb)
            
            try:
                import asyncio
                message_text = f"🚨 **BOT ERROR** 🚨\n\n`{log_entry[:4000]}`"
                asyncio.create_task(self.bot.send_message(
                    ADMIN_ID,
                    text=message_text,
                    parse_mode="Markdown"
                ))
            except Exception as e:
                print(f"Failed to send log to Telegram: {e}")

def setup_logger(bot_instance: Bot):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # --- Use the new, advanced filter ---
    noise_filter = AdvancedAiohttpNoiseFilter()

    # Console Handler (for journalctl and docker logs)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(noise_filter) # <-- Apply the filter
    logger.addHandler(console_handler)

    # Telegram Handler (for your private alerts)
    telegram_handler = TelegramBotHandler(bot_instance)
    telegram_formatter = logging.Formatter('%(levelname)s - %(message)s')
    telegram_handler.setFormatter(telegram_formatter)
    telegram_handler.setLevel(logging.ERROR)
    telegram_handler.addFilter(noise_filter) # <-- Apply the filter
    logger.addHandler(telegram_handler)

    print("✅ Logger setup complete. Advanced noise filtering is active.")