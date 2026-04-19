import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random
import re
from logger_config import setup_logging

# Initialize Logger
logger = setup_logging("youtube_client")

def parse_duration(duration_str):
    """Parses ISO 8601 duration (e.g. PT4M13S) into seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

class YouTubeClient:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key, static_discovery=False, cache_discovery=False)
                logger.info("YouTube API client successfully initialized.")
            except Exception as e:
                logger.error(f"Error initializing YouTube API: {e}", exc_info=True)

    def validate_video(self, item, lang_str, verified_channels):
        """Unified validation for all videos."""
        v_id = item['id'] if isinstance(item['id'], str) else item['id'].get('videoId')
        if not v_id: return None

        snippet = item.get('snippet', {})
        status = item.get('status', {})
        content_details = item.get('contentDetails', {})

        # 0. EMBEDDABILITY & REGION LOCK
        if not status.get('embeddable', True): return None
        restrictions = content_details.get('regionRestriction', {})
        if 'blocked' in restrictions and 'IN' in restrictions['blocked']: return None
        if 'allowed' in restrictions and 'IN' not in restrictions['allowed']: return None

        title = snippet.get('title', '').lower()
        channel = snippet.get('channelTitle', '').lower()
        # Normalize channel for matching (no spaces/special chars)
        norm_channel = re.sub(r'[^a-z0-9]', '', channel)
        
        published_at = snippet.get('publishedAt', '')
        year = int(published_at[:4]) if published_at else 0

        # 1. CHANNEL LOCK (Strict Official Labels Only - Normalized)
        match_found = False
        for brand in verified_channels:
            norm_brand = re.sub(r'[^a-z0-9]', '', brand.lower())
            if norm_brand in norm_channel:
                match_found = True
                break
        
        if not match_found:
            return None

        # 2. YEAR LOCK (1990 - 2026)
        if year < 1990 or year > 2026:
            return None

        # 3. DURATION LOCK (Strictly 3.0m - 10.0m)
        dur = parse_duration(content_details.get('duration', 'PT0S'))
        if dur < 180 or dur > 600:
            return None

        # 4. CONTENT LOCK (No compilation/jukebox/shorts/lofi)
        banned_terms = [
            'jukebox', 'making of', 'interview', 'review', 'reaction', 'climax', 
            'photo editing', 'tutorial', 'how to', 'shorts', '1-hour', '1 hour', 
            'full album', 'compilation', 'mashup', 'remix', 'lofi', 'sleep'
        ]
        if any(x in title for x in banned_terms):
            return None

        # 5. LANGUAGE LOCK (Avoid crossover)
        other_langs = ["hindi", "telugu", "tamil", "kannada", "malayalam", "english"]
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

        premium_labels = {
            "Telugu": ["aditya music", "mango music", "saregama south", "sony music south", "lahari music", "t-series telugu", "mango music telugu"],
            "Hindi": ["t-series", "sony music india", "zee music company", "yrf", "tips official", "saregama music", "t series"],
            "Kannada": ["anand audio", "saregama kannada", "jhankar music", "lahari music kannada", "prk audio", "a2 music"],
            "Tamil": ["sony music south", "think music india", "saregama tamil", "u1 records", "muzik247 tamil", "think music"],
            "Malayalam": ["muzik247", "saregama malayalam", "satyam audios", "goodwill entertainments"],
            "English": ["vevo", "warner records", "atlantic records", "sony music", "universal music", "columbia records", "republic records", "interscope"]
        }

        lang_str = languages[0] if (languages and len(languages) > 0) else "Hindi"
        target_labels = premium_labels.get(lang_str, premium_labels["Hindi"])
        verified_channels = target_labels + ['vevo', 'official', 'records', 'music']

        mood_terms = {
            'Happy': 'happy songs mass songs item songs official',
            'Sad': 'melody and sad songs official',
            'Angry': 'angry songs mass intense official',
            'Neutral': 'normal movies songs official',
            'Fearful': 'suspense thriller official',
            'Relaxed': 'soft melody official'
        }
        mood_query = mood_terms.get(emotion, 'top movie songs')
        
        # QUOTA OPTIMIZED: Exactly ONE high-quality query to save your API limit
        query = f"{lang_str} official full movie video song {mood_query} -jukebox -shorts"
        
        valid_videos = []
        seen_ids = set()

        try:
            # Single search call (100 units)
            request = self.youtube.search().list(
                part="snippet",
                maxResults=50,
                q=query,
                type="video",
                videoEmbeddable="true",
                regionCode="IN" if lang_str != "English" else "US"
            )
            response = request.execute()
            v_ids = [item['id']['videoId'] for item in response.get('items', [])]
            
            if v_ids:
                # Single videos call (1 unit)
                details_response = self.youtube.videos().list(
                    part="snippet,contentDetails,status",
                    id=",".join(v_ids)
                ).execute()

                for item in details_response.get('items', []):
                    if len(valid_videos) >= 20: break
                    video_data = self.validate_video(item, lang_str, verified_channels)
                    if video_data and video_data['videoId'] not in seen_ids:
                        seen_ids.add(video_data['videoId'])
                        valid_videos.append(video_data)

        except Exception as e:
            if 'quotaExceeded' in str(e):
                logger.error("!!! YOUTUBE API QUOTA EXCEEDED !!!")
            else:
                logger.error(f"Search error: {e}")

        # Reverse Chronological Sort (2026 -> 1990)
        valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)
        return valid_videos[:20]
