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

        # Channel verification
        match_found = False
        for brand in verified_channels:
            norm_brand = re.sub(r'[^a-z0-9]', '', brand.lower())
            if norm_brand in norm_channel:
                match_found = True
                break
        if not match_found: return None

        # Metadata constraints
        if year < 1990 or year > 2026: return None
        dur = parse_duration(content_details.get('duration', 'PT0S'))
        if dur < 180 or dur > 600: return None

        # Content filtering
        banned_terms = ['jukebox', 'making of', 'interview', 'review', 'reaction', 'climax', 
                        'photo editing', 'tutorial', 'how to', 'shorts', '1-hour', 'full album', 
                        'compilation', 'mashup', 'remix', 'lofi', 'sleep']
        if any(x in title for x in banned_terms): return None

        # Language isolation
        other_langs = ["hindi", "telugu", "tamil", "kannada", "malayalam", "english", "punjabi", "instrumental"]
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
            "Punjabi": ["speed records", "white hill music", "desi melodies", "t-series apna punjab", "geet mp3", "jass records", "punjabi"],
            "English": ["vevo", "warner records", "atlantic records", "sony music", "universal music", "columbia records", "republic records", "interscope"],
            "Instrumental": ["t-series", "saregama", "relaxing", "meditation", "instrumental"]
        }

        lang_str = languages[0] if (languages and len(languages) > 0) else "Hindi"
        target_labels = premium_labels.get(lang_str, premium_labels["Hindi"])
        verified_channels = target_labels + ['vevo', 'official', 'records', 'music', 'studio']

        mood_terms = {
            'Happy': 'party dance upbeat hit song',
            'Sad': 'sad emotional heartbreak cry song',
            'Angry': 'aggressive intense hype powerful song',
            'Neutral': 'popular trending hit track',
            'Fearful': 'dark intense cinematic suspense music',
            'Relaxed': 'relaxing soothing calm lofi melody'
        }
        mood_query = mood_terms.get(emotion, 'best popular song')
        
        query = f"{lang_str} {mood_query} official music video -jukebox songs"
        valid_videos = []
        seen_ids = set()

        try:
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
                raise ExternalAPIError("YouTube", "Quota exceeded. Try again later.")
            else:
                logger.error(f"YouTube search error: {e}")
                raise ExternalAPIError("YouTube", str(e))

        valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)
        return valid_videos[:20]
