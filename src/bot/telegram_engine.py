import telebot
import threading
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.core.config import Config
from src.core.constants import EMOJI_MAP
from src.services import youtube_service, supabase_service
from src.models import emotion_engine
from src.utils.logger import setup_logging

logger = setup_logging("telegram_bot")

class TelegramBot:
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.bot = None
        self.languages = ["Hindi", "Kannada", "Telugu", "Tamil", "Malayalam", "English", "Punjabi", "Instrumental"]
        
        if self.token and ":" in self.token:
            try:
                self.bot = telebot.TeleBot(self.token)
                self._register_handlers()
                logger.info("Telegram Bot engine initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram Bot: {e}")
        else:
            logger.warning("Invalid Telegram Token. Bot features disabled.")

    def _get_language_keyboard(self, emotion):
        markup = InlineKeyboardMarkup()
        buttons = []
        for lang in self.languages:
            cb_data = f"lang_{emotion}_{lang}"
            buttons.append(InlineKeyboardButton(text=lang, callback_data=cb_data))
        for i in range(0, len(buttons), 2):
            markup.add(*buttons[i:i+2])
        return markup

    def _register_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def welcome(message):
            welcome_text = (
                "🎵 *Welcome to Mood Music Hub Bot!*\n"
                "I detect your mood and find the perfect soundtrack.\n\n"
                "1️⃣ Type your feelings\n"
                "2️⃣ Send a selfie 📸\n"
            )
            self.bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

        @self.bot.message_handler(content_types=['text'])
        def text_mood(message):
            processing = self.bot.send_message(message.chat.id, "⏳ *Analyzing...*", parse_mode="Markdown")
            try:
                res = emotion_engine.analyze_text(message.text)
                emotion = res['emotion']
                reply = f"🧠 *Detected:* {emotion} {EMOJI_MAP.get(emotion, '😐')}\n🎧 Choose language:"
                self.bot.edit_message_text(reply, message.chat.id, processing.message_id, 
                                          parse_mode="Markdown", reply_markup=self._get_language_keyboard(emotion))
            except Exception as e:
                logger.error(f"Bot text error: {e}")
                self.bot.edit_message_text("❌ Error analyzing text.", message.chat.id, processing.message_id)

        @self.bot.message_handler(content_types=['photo'])
        def photo_mood(message):
            processing = self.bot.send_message(message.chat.id, "📸 *Analyzing photo...*", parse_mode="Markdown")
            try:
                file_info = self.bot.get_file(message.photo[-1].file_id)
                downloaded = self.bot.download_file(file_info.file_path)
                temp = os.path.join(Config.UPLOAD_FOLDER, f"tg_{message.message_id}.jpg")
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                with open(temp, 'wb') as f: f.write(downloaded)
                
                res = emotion_engine.analyze_image_emotion(temp)
                if os.path.exists(temp): os.remove(temp)
                
                if not res.get('face_detected'):
                    self.bot.edit_message_text("❌ Face not detected.", message.chat.id, processing.message_id)
                    return
                
                emotion = res['emotion']
                reply = f"🧠 *Detected:* {emotion} {EMOJI_MAP.get(emotion, '😐')}\n🎧 Choose language:"
                self.bot.edit_message_text(reply, message.chat.id, processing.message_id,
                                          parse_mode="Markdown", reply_markup=self._get_language_keyboard(emotion))
            except Exception as e:
                logger.error(f"Bot photo error: {e}")
                self.bot.edit_message_text("❌ Error analyzing photo.", message.chat.id, processing.message_id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
        def lang_select(call):
            parts = call.data.split('_')
            if len(parts) >= 3:
                emotion, lang = parts[1], parts[2]
                self.bot.answer_callback_query(call.id, f"Fetching {lang}...")
                self.bot.edit_message_text(f"🎵 Finding {lang} {emotion} music...", call.message.chat.id, call.message.message_id)
                
                videos = youtube_service.search_music(emotion, [lang])
                if not videos:
                    self.bot.edit_message_text("❌ No recommendations found.", call.message.chat.id, call.message.message_id)
                    return
                
                reply = f"🎧 *Top {lang} for {emotion} Mood:*\n\n"
                for idx, v in enumerate(videos[:3]):
                    reply += f"{idx+1}. [{v['title']}](https://www.youtube.com/watch?v={v['videoId']})\n\n"
                self.bot.edit_message_text(reply, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

    def start(self):
        if not self.bot: return
        logger.info("Bot polling starting...")
        while True:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
            except Exception as e:
                logger.error(f"Bot crashed: {e}. Restarting...")
                time.sleep(5)

def run_bot_threaded():
    bot_engine = TelegramBot()
    thread = threading.Thread(target=bot_engine.start, daemon=True, name="TelegramBotThread")
    thread.start()
    return thread
