import os
from flask import Flask
from flask_cors import CORS

from src.core.config import Config
from src.api.auth import auth_bp
from src.api.analysis import analysis_bp
from src.api.music import music_bp
from src.api.admin import admin_bp
from src.api.views import views_bp
from src.api.errors import register_error_handlers
from src.utils.logger import setup_logging
from src.bot.telegram_engine import run_bot_threaded

# Initialize Logging
logger = setup_logging("main")

def create_app():
    """Application factory for Mood Music Hub."""
    
    # Validate Config
    Config.validate()
    
    app = Flask(__name__, 
                static_folder=Config.STATIC_FOLDER,
                template_folder=Config.TEMPLATE_FOLDER)
    
    app.secret_key = Config.SECRET_KEY
    CORS(app)

    # Register Blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(admin_bp)

    # Register Centralized Error Handlers
    register_error_handlers(app)

    # Ensure necessary folders exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.LOG_DIR, exist_ok=True)

    return app

if __name__ == '__main__':
    logger.info(f">>> [BOOT] Starting Mood Music Hub on {Config.HOST}:{Config.PORT}")
    
    try:
        # 1. Start Telegram Bot in Background
        run_bot_threaded()
        
        # 2. Start Flask Server
        app = create_app()
        app.run(debug=Config.DEBUG, port=Config.PORT, host=Config.HOST)
        
    except Exception as e:
        logger.critical(f"FATAL SYSTEM FAILURE: {e}", exc_info=True)
