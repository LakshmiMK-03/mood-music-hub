import sqlite3
import os
from datetime import datetime
from database import get_db_connection

def log_analysis(source, text, emotion, stress_level, confidence, stress_score):
    """
    Log an analysis event to hub.db (SQLite).
    source: 'text' or 'image'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        text_preview = (text[:50] + '...') if text and len(text) > 50 else text
        
        cursor.execute('''
            INSERT INTO history (timestamp, source, text_preview, emotion, stress_level, stress_score, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            source,
            text_preview,
            emotion,
            stress_level,
            float(stress_score),
            float(confidence)
        ))
        
        # Enforce history limit (last 1000)
        cursor.execute('''
            DELETE FROM history 
            WHERE id NOT IN (
                SELECT id FROM history ORDER BY id DESC LIMIT 1000
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB Logging Error: {e}")

def get_stats():
    """
    Aggregate statistics from SQLite for the admin dashboard.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total
        cursor.execute('SELECT COUNT(*) FROM history')
        total = cursor.fetchone()[0]
        
        # Emotion Dist
        emotions = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']
        emotion_dist = {e: 0 for e in emotions}
        cursor.execute('SELECT emotion, COUNT(*) FROM history GROUP BY emotion')
        for em, count in cursor.fetchall():
            if em in emotion_dist: 
                emotion_dist[str(em)] = int(count)
            
        # Stress Dist
        stresses = ['Low', 'Medium', 'High']
        stress_dist = {s: 0 for s in stresses}
        cursor.execute('SELECT stress_level, COUNT(*) FROM history GROUP BY stress_level')
        for sl, count in cursor.fetchall():
            if sl in stress_dist: 
                stress_dist[str(sl)] = int(count)
            
        # Recent Activity (last 5)
        cursor.execute('SELECT * FROM history ORDER BY id DESC LIMIT 5')
        recent = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_analyses': total,
            'emotion_dist': emotion_dist,
            'stress_dist': stress_dist,
            'recent_activity': recent
        }
    except Exception as e:
        print(f"❌ DB Stats Error: {e}")
        return {'error': str(e)}
