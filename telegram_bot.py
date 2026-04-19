import os
import time
import threading
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from emotion_model import analyze_text, analyze_image_emotion
from youtube_client import YouTubeClient
from logger_config import setup_logging

# Load environment variables
load_dotenv()

# Setup Logger
logger = setup_logging("telegram_bot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip('"').strip("'")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is missing from .env")

# Initialize clients
youtube_client = YouTubeClient()

# Initialize bot safely to prevent crashes if token is missing
bot = None
if TELEGRAM_BOT_TOKEN and ":" in TELEGRAM_BOT_TOKEN:
    try:
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        logger.info("Telegram Bot initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram Bot: {e}")
else:
    logger.warning("TELEGRAM_BOT_TOKEN is missing or invalid. Telegram features will be disabled.")

EMOJI_MAP = {
    'Happy': "😊",
    'Sad': "😟",
    'Angry': "😤",
    'Fearful': "😨",
    'Neutral': "😐",
    'Surprised': "😲"
}

LANGUAGES = ["Hindi", "Kannada", "Telugu", "Tamil", "Malayalam", "English", "Punjabi", "Instrumental"]

def get_language_keyboard(emotion):
    """Creates an inline keyboard allowing the user to select the language of their music."""
    markup = InlineKeyboardMarkup()
    
    # Create buttons in pairs (2 per row)
    buttons = []
    for lang in LANGUAGES:
        # callback_data max is 64 bytes. E.g., 'lang_Happy_Kannada'
        cb_data = f"lang_{emotion}_{lang}"
        buttons.append(InlineKeyboardButton(text=lang, callback_data=cb_data))
        
    # Group into rows of 2
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        markup.add(*row)
        
    return markup

if bot:
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🎵 *Welcome to Mood Music Hub Bot!*\n\n"
            "I can detect how you're feeling and recommend the perfect music for your mood.\n\n"
            "👉 *How to use me:*\n"
            "1️⃣ Type a sentence about how you are feeling.\n"
            "2️⃣ OR send me a selfie 📸 and I will detect your emotion!\n\n"
            "   No login required. We will analyze your input securely and locally!"
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

    @bot.message_handler(content_types=['text'])
    def handle_text_analysis(message):
        user_text = message.text.strip()
        
        if not user_text:
            return
            
        chat_id = message.chat.id
        processing_msg = bot.send_message(chat_id, "⏳ *Analyzing your emotion...*", parse_mode="Markdown")
        
        try:
            result = analyze_text(user_text)
            emotion = result.get('emotion', 'Neutral')
            stress = result.get('stress_level', 'Low')
            emoji = EMOJI_MAP.get(emotion, '😐')
            
            analysis_reply = (
                f"🧠 *Analysis Complete!* {emoji}\n\n"
                f"• *Detected Emotion:* {emotion}\n"
                f"• *Stress Level:* {stress}\n\n"
                f"🎧 *Choose your preferred music language:*"
            )
            
            bot.edit_message_text(
                analysis_reply, 
                chat_id, 
                processing_msg.message_id, 
                parse_mode="Markdown",
                reply_markup=get_language_keyboard(emotion)
            )
            
        except Exception as e:
            logger.error(f"Telegram processing error: {e}", exc_info=True)
            bot.edit_message_text("❌ *An error occurred while analyzing your text. Please try again later.*", chat_id, processing_msg.message_id, parse_mode="Markdown")


    @bot.message_handler(content_types=['photo'])
    def handle_image_analysis(message):
        chat_id = message.chat.id
        processing_msg = bot.send_message(chat_id, "📸 *Analyzing your photo...*", parse_mode="Markdown")
        
        try:
            # Get highest resolution photo (last in the array)
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Save temporarily
            os.makedirs("uploads", exist_ok=True)
            temp_path = os.path.join("uploads", f"temp_tg_{message.message_id}.jpg")
            with open(temp_path, 'wb') as new_file:
                new_file.write(downloaded_file)
                
            # Analyze
            result = analyze_image_emotion(temp_path)
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            emotion = result.get('emotion', 'Neutral')
            stress = result.get('stress_level', 'Low')
            emoji = EMOJI_MAP.get(emotion, '😐')
            face_detected = result.get('face_detected', False)
            
            if not face_detected:
                bot.edit_message_text("❌ *Could not detect a clear face. Please try another photo!*", chat_id, processing_msg.message_id, parse_mode="Markdown")
                return
                
            analysis_reply = (
                f"🧠 *Facial Analysis Complete!* {emoji}\n\n"
                f"• *Detected Emotion:* {emotion}\n"
                f"• *Confidence:* {result.get('confidence', 0)}%\n\n"
                f"🎧 *Choose your preferred music language:*"
            )
            
            bot.edit_message_text(
                analysis_reply, 
                chat_id, 
                processing_msg.message_id, 
                parse_mode="Markdown",
                reply_markup=get_language_keyboard(emotion)
            )
            
        except Exception as e:
            logger.error(f"Telegram Image processing error: {e}", exc_info=True)
            bot.edit_message_text("❌ *An error occurred while analyzing your photo. Please try again later.*", chat_id, processing_msg.message_id, parse_mode="Markdown")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def handle_language_selection(call):
        # Data is like: 'lang_Happy_Telugu'
        try:
            parts = call.data.split('_')
            if len(parts) >= 3:
                emotion = parts[1]
                language = parts[2]
                
                # Acknowledge the callback quickly so the button stops flashing
                bot.answer_callback_query(call.id, f"Fetching {language} songs...")
                
                bot.edit_message_text(
                    f"🎵 _Fetching top-tier {language} music recommendations for {emotion}..._",
                    call.message.chat.id, 
                    call.message.message_id, 
                    parse_mode="Markdown"
                )
                
                # Fetch videos
                videos = youtube_client.search_music(emotion, [language])
                
                if not videos:
                    bot.edit_message_text(
                        f"❌ Sorry, I couldn't find any {language} music recommendations at the moment.",
                        call.message.chat.id, 
                        call.message.message_id, 
                        parse_mode="Markdown"
                    )
                    return
                    
                # Format and Send Recommendations
                songs_reply = f"🎧 *Top {language} Playlists for {emotion} Mood:*\n\n"
                
                for idx, video in enumerate(videos[:3]):
                    title = video['title']
                    url = f"https://www.youtube.com/watch?v={video['videoId']}"
                    songs_reply += f"{idx + 1}. [{title}]({url})\n\n"
                    
                bot.edit_message_text(
                    songs_reply, 
                    call.message.chat.id, 
                    call.message.message_id, 
                    parse_mode="Markdown", 
                    disable_web_page_preview=False
                )
                
        except Exception as e:
            logger.error(f"Callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "An error occurred.")


def start_polling():
    """Starts the Telegram bot polling mechanism in an infinite loop."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Cannot start bot polling: Missing TELEGRAM_BOT_TOKEN.")
        return
        
    logger.info(">>> [START] TELEGRAM BOT STARTED POLLING")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Telegram polling crashed: {e}. Restarting in 5s...")
            time.sleep(5)

def run_telegram_bot_thread():
    """Wrapper to run the bot in a background daemon thread."""
    bot_thread = threading.Thread(target=start_polling, daemon=True, name="TelegramBot")
    bot_thread.start()
    return bot_thread

if __name__ == "__main__":
    start_polling()
