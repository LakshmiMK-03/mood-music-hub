# 🎵 Mood Music Hub

Mood Music Hub is an intelligent web application that detects your emotions and stress levels through text, image, and camera inputs, and recommends personalized music to match your mood.

## 🚀 Key Features

*   **Multimodal Emotion Detection:** Analyzes text sentiment (VADER), facial landmarks (MediaPipe), and uses AI models to classify your mood.
*   **Stress Analysis:** Calculates stress scores and provides actionable relaxation tips and affirmations.
*   **Music Recommendations:** Fetched via YouTube API, tailored to specific "Multinational Language / Regional Industry" preferences (Bollywood, Sandalwood, Tollywood, Pollywood, etc.).
*   **Telegram Bot Integration:** Get your mood analysis and music recommendations directly on Telegram.
*   **Admin Dashboard:** Comprehensive analytics for administrators to monitor system usage and user distribution.

## 🛠️ Tech Stack

- **Backend:** Flask (Python 3.10+) 
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript
- **Database:** Supabase (PostgreSQL + REST API)
- **AI/ML:** VADER Sentiment, MediaPipe, HuggingFace Inference API
- **External APIs:** YouTube Data API v3, Telegram Bot API (telebot)

## 📂 Project Structure

```text
mood-music-hub/
├── src/
│   ├── api/          # Flask Blueprints (REST Endpoints & Frontend Views)
│   ├── bot/          # Telegram Bot engine logic
│   ├── core/         # App configuration, custom exceptions, constants
│   ├── models/       # Emotion & Stress detection logic
│   ├── services/     # Supabase & YouTube service wrappers
│   ├── static/       # CSS, JS, and image assets
│   └── templates/    # Jinja2 HTML templates
├── logs/             # Application logs
├── uploads/          # Temporary file processing
├── .env              # Environment Configuration
├── requirements.txt  # Project Dependencies
└── main.py           # Application Entry Point
```

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LakshmiMK-03/mood-music-hub.git
   cd mood-music-hub
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   # Flask
   FLASK_SECRET_KEY=your_secret_key
   PORT=5001

   # Database (Supabase)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-key

   # YouTube API
   YOUTUBE_API_KEY=your_youtube_api_key

   # Telegram Bot
   TELEGRAM_BOT_TOKEN=your_bot_token
   ```

## 🏃 Running the Application

To start both the Flask web server and the Telegram bot, simply run:

```bash
python main.py
```

- **Web Portal:** Access at `http://localhost:5001`
- **Telegram Bot:** Start your bot on Telegram to begin interaction.

## 🛡️ Error Handling & Best Practices

- **Centralized Errors:** Custom exceptions (`AppError`, `ValidationError`, etc.) ensure consistent API responses.
- **Service Isolation:** External APIs are wrapped in service classes to decouple logic.
- **Logging:** Rotating file logs are maintained in the `/logs` directory for monitoring.
- **Clean Code:** Standardized directory structure following Python best practices.
