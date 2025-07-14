import json
import random
import time
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from dotenv import load_dotenv
load_dotenv()


# Get bot token from environment variable or use default
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in environment variables or .env file!")


CODES_FILE = "phone_codes.json"
CODE_EXPIRY_SECONDS = 60  # 1 minute

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_codes():
    try:
        with open(CODES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_codes(codes):
    with open(CODES_FILE, "w") as f:
        json.dump(codes, f)

def validate_telegram_code(phone_number: str, code: str) -> bool:
    try:
        codes = load_codes()
        logger.info(f"Validating code for phone: {phone_number}, provided code: {code}")
        logger.info(f"Available codes in file: {codes}")
        
        entry = codes.get(phone_number)
        if not entry:
            logger.warning(f"No code found for phone number: {phone_number}")
            return False
            
        logger.info(f"Found entry for phone {phone_number}: {entry}")
        
        if entry["code"] != code:
            logger.warning(f"Code mismatch. Expected: {entry['code']}, Got: {code}")
            return False
            
        if time.time() > entry["expiry"]:
            logger.warning(f"Code expired. Current time: {time.time()}, Expiry: {entry['expiry']}")
            # Remove expired code
            del codes[phone_number]
            save_codes(codes)
            return False
            
        logger.info(f"Code validation successful for {phone_number}")
        # Remove code after successful use
        del codes[phone_number]
        save_codes(codes)
        return True
    except Exception as e:
        logger.error(f"Error validating code: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    # Show the phone number sharing button right away
    keyboard = [
        [KeyboardButton("Share phone number", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Please share your phone number to receive a verification code.",
        reply_markup=reply_markup
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.contact:
        return
    contact = update.message.contact
    if contact.phone_number:
        phone_number = contact.phone_number
        telegram_user_id = update.message.from_user.id if update.message.from_user else None
        if not telegram_user_id:
            return
        # Generate a 4-digit code
        code = str(random.randint(1000, 9999))
        expiry = time.time() + CODE_EXPIRY_SECONDS
        # Save the code, expiry, and mapping
        codes = load_codes()
        codes[phone_number] = {
            "code": code,
            "telegram_user_id": telegram_user_id,
            "expiry": expiry
        }
        save_codes(codes)
        # Send the code to the user
        await update.message.reply_text(
            f"Your verification code is: {code} (valid for 1 minute)"
        )
        # Show the "Share phone number" button again
        keyboard = [
            [KeyboardButton("Share phone number", request_contact=True)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "If you need a new code, tap the button below to share your phone number again.",
            reply_markup=reply_markup
        )
        logger.info(f"Sent code {code} to {phone_number} (Telegram user {telegram_user_id})")

def start_telegram_bot():
    """Start the Telegram bot in a separate thread"""
    import threading
    import asyncio
    
    def run_bot():
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
            app.run_polling()
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
        finally:
            loop.close()
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram bot started in background thread")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.run_polling()

if __name__ == "__main__":
    main()