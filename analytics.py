import os
from datetime import datetime
from database import get_db_connection

def log_analysis(source, text, emotion, stress_level, confidence, stress_score):
    """
    Log an analysis event to Supabase.
    source: 'text' or 'image'
    """
    try:
        supabase = get_db_connection()
        
        text_preview = (text[:50] + '...') if text and len(text) > 50 else text
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "text_preview": text_preview,
            "emotion": emotion,
            "stress_level": stress_level,
            "stress_score": float(stress_score),
            "confidence": float(confidence)
        }
        
        supabase.table('history').insert(data).execute()
        
        # Note: We don't manually enforce 1000 limit here to save on API calls, 
        # Supabase can handle much more or use a CRON job later.
        
    except Exception as e:
        print(f"❌ Supabase Logging Error: {e}")

def get_stats():
    """
    Aggregate statistics from Supabase for the admin dashboard.
    """
    try:
        supabase = get_db_connection()
        
        # 1. Total History Count
        # Using select with count='exact' to get total without fetching rows
        response = supabase.table('history').select('*', count='exact').execute()
        total = response.count if response.count is not None else 0
        
        # 2. Emotion Dist
        emotions = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']
        emotion_dist = {e: 0 for e in emotions}
        
        # In Supabase, we fetch IDs and emotions to count on the app side (or use RPC)
        # Fetching all to count for now (small scale)
        resp_em = supabase.table('history').select('emotion').execute()
        for item in resp_em.data:
            em = item.get('emotion')
            if em in emotion_dist:
                emotion_dist[em] += 1
            
        # 3. Stress Dist
        stresses = ['Low', 'Medium', 'High']
        stress_dist = {s: 0 for s in stresses}
        resp_st = supabase.table('history').select('stress_level').execute()
        for item in resp_st.data:
            sl = item.get('stress_level')
            if sl in stress_dist:
                stress_dist[sl] += 1
            
        # 4. Recent Activity (last 5)
        resp_recent = supabase.table('history').select('*').order('id', desc=True).limit(5).execute()
        recent = resp_recent.data
        
        return {
            'total_analyses': total,
            'emotion_dist': emotion_dist,
            'stress_dist': stress_dist,
            'recent_activity': recent
        }
    except Exception as e:
        print(f"❌ Supabase Stats Error: {e}")
        return {'error': str(e)}
