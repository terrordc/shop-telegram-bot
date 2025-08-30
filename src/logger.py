# src/logger.py - UPGRADED WITH A NOISE FILTER

import logging
import traceback
from aiogram import Bot

ADMIN_ID = 347242473 # <-- IMPORTANT: Replace with YOUR admin ID

# --- START OF NEW CODE ---
# This is our custom filter to ignore the harmless BadStatusLine error
class AiohttpNoiseFilter(logging.Filter):
    def __init__(self, name: str = "AiohttpNoiseFilter") -> None:
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        # Get the message from the log record
        message = record.getMessage()
        # Check if the harmless error strings are in the message
        if "BadStatusLine" in message or "Invalid method encountered" in message:
            return False # Returning False drops the message
        return True # Returning True lets the message pass through
# --- END OF NEW CODE ---


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

    # --- ADD THE FILTER TO OUR HANDLERS ---
    noise_filter = AiohttpNoiseFilter()

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(noise_filter) # <-- Apply the filter
    logger.addHandler(console_handler)

    telegram_handler = TelegramBotHandler(bot_instance)
    telegram_formatter = logging.Formatter('%(levelname)s - %(message)s')
    telegram_handler.setFormatter(telegram_formatter)
    telegram_handler.setLevel(logging.ERROR)
    telegram_handler.addFilter(noise_filter) # <-- Apply the filter
    logger.addHandler(telegram_handler)

    print("✅ Logger setup complete. Errors will be sent to the admin.")