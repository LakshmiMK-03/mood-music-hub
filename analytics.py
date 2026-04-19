import os
import requests
from datetime import datetime
from database import URL, get_rest_headers
from logger_config import setup_logging

# Initialize Logger
logger = setup_logging("analytics")

def log_analysis(user_id, source, text, emotion, stress_level, confidence, stress_score):
    """
    Log an analysis event to Supabase using REST API.
    source: 'text' or 'image'
    """
    try:
        text_preview = (text[:50] + '...') if text and len(text) > 50 else text
        
        data = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "text_preview": text_preview,
            "emotion": emotion,
            "stress_level": stress_level,
            "stress_score": float(stress_score),
            "confidence": float(confidence)
        }
        
        url = f"{URL}/rest/v1/history"
        response = requests.post(url, headers=get_rest_headers(), json=data, timeout=5)
        if response.status_code not in (201, 200, 204):
            logger.error(f"Supabase REST Logging Error (User {user_id}): {response.text}")
            
    except Exception as e:
        logger.error(f"Supabase Logging Exception (User {user_id}): {e}")

def get_stats():
    """
    Aggregate statistics from Supabase REST API for the admin dashboard.
    """
    try:
        url_history = f"{URL}/rest/v1/history"
        headers = get_rest_headers()
        
        # We can fetch all history for simple stats (or use RPC for heavy DBs)
        response = requests.get(url_history, headers=headers, timeout=5)
        if response.status_code != 200:
            return {'error': f'Failed to fetch stats: {response.text}'}
            
        history_data = response.json()
        total = len(history_data)
        
        emotions = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']
        emotion_dist = {e: 0 for e in emotions}
        
        stresses = ['Low', 'Medium', 'High']
        stress_dist = {s: 0 for s in stresses}
        
        for item in history_data:
            em = item.get('emotion')
            sl = item.get('stress_level')
            if em in emotion_dist:
                emotion_dist[em] += 1
            if sl in stress_dist:
                stress_dist[sl] += 1
                
        # Recent Activity (last 5)
        # Using Supabase REST API query params for ordering and limits
        url_recent = f"{url_history}?order=id.desc&limit=5"
        resp_recent = requests.get(url_recent, headers=headers, timeout=5)
        recent = resp_recent.json() if resp_recent.status_code == 200 else []
        
        return {
            'total_analyses': total,
            'emotion_dist': emotion_dist,
            'stress_dist': stress_dist,
            'recent_activity': recent
        }
    except Exception as e:
        logger.error(f"Supabase Stats Aggregation Error: {e}", exc_info=True)
        return {'error': str(e)}
