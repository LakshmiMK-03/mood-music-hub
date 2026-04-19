import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'mood-music-hub-secret-key-2025')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 7860))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Supabase Settings
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # YouTube API Settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip('"').strip("'")
    
    # HuggingFace Settings
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    
    # Folder Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'src', 'static')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'src', 'templates')

    @classmethod
    def validate(cls):
        """Validates that critical configuration is present."""
        missing = []
        if not cls.SUPABASE_URL: missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY: missing.append("SUPABASE_KEY")
        if not cls.YOUTUBE_API_KEY: missing.append("YOUTUBE_API_KEY")
        
        if missing:
            print(f"WARNING: Missing environment variables: {', '.join(missing)}")
            return False
        return True
