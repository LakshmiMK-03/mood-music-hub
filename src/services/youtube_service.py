import os
import re
from googleapiclient.discovery import build
from src.core.config import Config
from src.core.exceptions import ExternalAPIError
from src.utils.logger import setup_logging

logger = setup_logging("youtube_service")

def parse_duration(duration_str):
    """Parses ISO 8601 duration (e.g. PT4M13S) into seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

class YouTubeService:
    PREMIUM_LABELS = {
        "Telugu": ["aditya music", "mango music", "saregama south", "sony music south", "lahari music", "t-series telugu", "mango music telugu"],
        "Hindi": ["t-series", "sony music india", "zee music company", "yrf", "tips official", "saregama music", "t series"],
        "Kannada": ["anand audio", "saregama kannada", "jhankar music", "lahari music kannada", "prk audio", "a2 music"],
        "Tamil": ["sony music south", "think music india", "saregama tamil", "u1 records", "muzik247 tamil", "think music"],
        "Malayalam": ["muzik247", "saregama malayalam", "satyam audios", "goodwill entertainments"],
        "Punjabi": ["speed records", "white hill music", "desi melodies", "t-series apna punjab", "geet mp3", "jass records", "punjabi"],
        "English": ["vevo", "warner records", "atlantic records", "sony music", "universal music", "columbia records", "republic records", "interscope"],
        "Instrumental": ["t-series", "saregama", "relaxing", "meditation", "instrumental"]
    }

    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY
        self.youtube = None
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key, 
                                     static_discovery=False, cache_discovery=False)
                logger.info("YouTube API client successfully initialized.")
            except Exception as e:
                logger.error(f"Error initializing YouTube API: {e}")
        else:
            logger.warning("YouTube API Key is missing. Music recommendations will not work.")

    def validate_video(self, item, lang_str, verified_channels):
        """Unified validation for all videos."""
        v_id = item['id'] if isinstance(item['id'], str) else item['id'].get('videoId')
        if not v_id: return None

        snippet = item.get('snippet', {})
        status = item.get('status', {})
        content_details = item.get('contentDetails', {})

        # Embeddability & Region check
        if not status.get('embeddable', True): return None
        restrictions = content_details.get('regionRestriction', {})
        if 'blocked' in restrictions and 'IN' in restrictions['blocked']: return None
        if 'allowed' in restrictions and 'IN' not in restrictions['allowed']: return None

        title = snippet.get('title', '').lower()
        channel = snippet.get('channelTitle', '').lower()
        norm_channel = re.sub(r'[^a-z0-9]', '', channel)
        
        published_at = snippet.get('publishedAt', '')
        year = int(published_at[:4]) if published_at else 0

        # 1. SPECIAL CASE: ENGLISH FILTERING
        is_english = lang_str.lower() == "english"
        regional_keywords = ["hindi", "telugu", "tamil", "kannada", "malayalam", "punjabi", "bengali", "bollywood", "tollywood", "kollywood", "sandalwood"]
        
        if is_english:
            if any(rk in norm_channel for rk in regional_keywords) or any(rk in title for rk in regional_keywords):
                return None

        # 2. CHANNEL LOCK (Strict Official Labels Only)
        match_found = False
        for brand in verified_channels:
            norm_brand = re.sub(r'[^a-z0-9]', '', brand.lower())
            if norm_brand in norm_channel:
                if is_english:
                    is_regional = False
                    for regional_lang, labels in self.PREMIUM_LABELS.items():
                        if regional_lang == "English": continue
                        for l_brand in labels:
                            norm_l_brand = re.sub(r'[^a-z0-9]', '', l_brand.lower())
                            if norm_l_brand in norm_channel:
                                is_regional = True
                                break
                        if is_regional: break
                    if is_regional: continue 
                
                match_found = True
                break
        if not match_found: return None

        # 3. YEAR LOCK (1990 - 2026)
        if year < 1990 or year > 2026: return None

        # 4. DURATION LOCK (Strictly 2.5m - 11.0m)
        dur = parse_duration(content_details.get('duration', 'PT0S'))
        if dur < 150 or dur > 660: return None

        # 5. CONTENT LOCK
        banned_terms = ['jukebox', 'making of', 'interview', 'review', 'reaction', 'climax', 
                        'photo editing', 'tutorial', 'how to', 'shorts', '1-hour', '1 hour', 
                        'full album', 'compilation', 'mashup', 'remix', 'lofi', 'sleep']
        if any(x in title for x in banned_terms): return None

        # 6. LANGUAGE LOCK
        other_langs = ["hindi", "telugu", "tamil", "kannada", "malayalam", "english", "punjabi"]
        if lang_str.lower() in other_langs:
            local_langs = [l for l in other_langs if l != lang_str.lower()]
            if any(ol in title for ol in local_langs) and (lang_str.lower() not in title):
                return None

        return {
            'title': snippet.get('title'),
            'videoId': v_id,
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url'),
            'channelTitle': snippet.get('channelTitle'),
            'publishedAt': published_at,
            'duration': dur,
            'year': year
        }

    def search_music(self, emotion, languages=None):
        if not self.youtube: return []

        langs_to_fetch = languages if (languages and len(languages) > 0) else ["Hindi"]
        
        mood_terms = {
            'Happy': 'happy upbeat energetic music official',
            'Sad': 'emotional sad soul melody official',
            'Angry': 'intense powerful aggressive official',
            'Neutral': 'pleasant chill movie songs official',
            'Fearful': 'suspenseful dark thriller official',
            'Relaxed': 'calming soft peaceful official'
        }
        mood_query = mood_terms.get(emotion, 'best songs official')
        
        valid_videos = []
        seen_ids = set()

        for lang_str in langs_to_fetch:
            target_labels = self.PREMIUM_LABELS.get(lang_str, self.PREMIUM_LABELS["Hindi"])
            verified_channels = target_labels + ['vevo', 'official', 'records', 'music', 'studio']
            query = f"{lang_str} movie video song {mood_query} -jukebox -shorts"
            
            try:
                request = self.youtube.search().list(
                    part="snippet",
                    maxResults=25,
                    q=query,
                    type="video",
                    videoEmbeddable="true",
                    regionCode="IN" if lang_str != "English" else "US"
                )
                response = request.execute()
                v_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                if v_ids:
                    details_response = self.youtube.videos().list(
                        part="snippet,contentDetails,status",
                        id=",".join(v_ids)
                    ).execute()

                    for item in details_response.get('items', []):
                        if len(valid_videos) >= 30: break
                        
                        video_data = self.validate_video(item, lang_str, verified_channels)
                        if video_data and video_data['videoId'] not in seen_ids:
                            seen_ids.add(video_data['videoId'])
                            valid_videos.append(video_data)

            except Exception as e:
                if 'quotaExceeded' in str(e):
                    logger.error("!!! YOUTUBE API QUOTA EXCEEDED !!!")
                    # Optionally raise if you want the app to handle it globally
                else:
                    logger.error(f"Search error for {lang_str}: {e}")

            if len(valid_videos) >= 30: break

        valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)
        logger.info(f"[SEARCH] Final counts for {langs_to_fetch}: {len(valid_videos)} songs.")
        return valid_videos[:30]
