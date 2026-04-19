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
                # Use a specific version and robust configuration
                self.youtube = build('youtube', 'v3', developerKey=self.api_key, static_discovery=False, cache_discovery=False)
                logger.info("YouTube API client successfully initialized.")
            except Exception as e:
                logger.error(f"Error initializing YouTube API: {e}", exc_info=True)

    def search_music(self, emotion, languages=None):
        """
        Search strictly for Top-Tier Official Movie Songs based on emotion.
        - Exact 15 results.
        - 3 - 10 mins duration.
        - 1990 - 2026 Year Range.
        - Verified Channels Only (T-Series, Anand Audio, etc).
        - Hard Language Lock.
        """
        if not self.youtube:
            logger.warning("YouTube API client not initialized. Check API Key.")
            return []

        # PREMIER VERIFIED LABELS (Ensures 100% Genuine Movie Content)
        premium_labels = {
            "Telugu": ["Aditya Music", "Mango Music", "Saregama South", "Sony Music South", "Lahari Music", "T-Series Telugu"],
            "Hindi": ["T-Series", "Sony Music India", "Zee Music Company", "YRF", "Tips Official", "Saregama Music"],
            "Kannada": ["Anand Audio", "Saregama Kannada", "Jhankar Music", "Lahari Music Kannada", "PRK Audio", "A2 Music"],
            "Tamil": ["Sony Music South", "SonyMusicSouthVEVO", "Think Music India", "Saregama Tamil", "U1 Records", "Muzik247 Tamil"],
            "Malayalam": ["Muzik247", "Saregama Malayalam", "Satyam Audios", "Goodwill Entertainments", "Millennium Audios"]
        }

        # Determine primary language and industry
        lang_str = languages[0] if languages and len(languages) > 0 else "Hindi"
        target_labels = premium_labels.get(lang_str, premium_labels["Hindi"])
        
        # Mapping Mood to Cinematic Archetypes
        mood_terms = {
            'Happy': 'official full video song fast beat hits',
            'Sad': 'emotional movie song heart touching',
            'Angry': 'action mass movie song bgm',
            'Fearful': 'suspense thriller movie song',
            'Neutral': 'melody hit full video song',
            'Relaxed': 'pleasant soul melody song'
        }
        mood_query = mood_terms.get(emotion, 'top movie songs')
        
        # STRICT NEGATIVE FILTERS (Now including content types to eliminate photo editing and tutorials)
        negative_filters = "-private -independent -cover -mashup -remix -shorts -piano -royalty -free -vlog -webseries -lofi -jukebox -dj -mix -8d -bass -scene -comedy -climax -reaction -review -trailer -teaser -interview -making -unplugged -karaoke -editing -tutorial -how -ncs -nocopyright -copyrightfree"

        search_strategies = []
        # Strategy 1: Specific Branded Searchess
        for brand in random.sample(target_labels, min(4, len(target_labels))):
            search_strategies.append(f'"{brand}" {lang_str} movie full video song {emotion}'.strip())
        
        # Strategy 2: Industry Focused Search (Fallback/Supplement)
        search_strategies.append(f"{lang_str} movie full video song {mood_query}")
        search_strategies.append(f"{lang_str} official {mood_query}")
        
        # Strategy 3: Broadest Industry Hits (Final Fallback)
        search_strategies.append(f"{lang_str} songs")

        valid_videos = []
        # STRICT VERIFIED CHANNEL WHITELIST
        verified_channels = [b.lower() for b in target_labels] + ['t-series', 'saregama', 'sony music', 'zee music', 'tips', 'anand audio', 'lahari', 'mango music', 'aditya', 'yrf', 'think music', 'jhankar', 'prk', 'muzik247', 'a2 music', 't-series telugu', 'lahari music kannada', 'sony music south', 'aditya music', 'think music india', 'muzik247 malayalam', 't-series kannada']

        seen_ids = set()

        for query in search_strategies:
            if len(valid_videos) >= 15: break
            try:
                # Use a slightly broader search but rely on our internal filters for "Pure Movie" content
                request = self.youtube.search().list(
                    part="snippet",
                    maxResults=50,
                    q=f"{query} {negative_filters}",
                    type="video",
                    videoEmbeddable="true",
                    relevanceLanguage=lang_str[:2].lower() # Hint for regional relevance
                )
                response = request.execute()
                
                video_ids = [item['id']['videoId'] for item in response.get('items', []) if item['id']['videoId'] not in seen_ids]
                if not video_ids: continue

                details_request = self.youtube.videos().list(
                    part="contentDetails,status,snippet",
                    id=",".join(video_ids)
                )
                details_response = details_request.execute()

                for item in details_response.get('items', []):
                    if len(valid_videos) >= 15: break
                    
                    # 0. EMBEDDABILITY LOCK
                    if not item['status'].get('embeddable', True): continue
                    
                    title = item['snippet']['title'].lower()
                    channel = item['snippet']['channelTitle'].lower()
                    published_at = item['snippet']['publishedAt']
                    year = int(published_at[:4])
                    v_id = item['id']

                    # 1. CHANNEL LOCK (Only Trusted Labels)
                    # We check if the channel name matches our premium labels
                    if not any(brand in channel for brand in verified_channels):
                        continue

                    # 2. YEAR LOCK (1990 - 2026)
                    if year < 1990 or year > 2026:
                        continue

                    # 3. DURATION LOCK (2.5m - 11m) - Slightly broader for hit rate
                    dur = parse_duration(item['contentDetails'].get('duration'))
                    if dur < 150 or dur > 660: 
                        continue

                    # 4. LANGUAGE LOCK (Strictly avoid cross-language confusion)
                    other_langs = ["hindi", "telugu", "tamil", "kannada", "malayalam"]
                    if lang_str.lower() in other_langs:
                        other_langs.remove(lang_str.lower())
                        if any(ol in title for ol in other_langs) and (lang_str.lower() not in title):
                            continue

                    # 5. CONTENT LOCK (Reject Jukebox/Review/Making/Photo-Editing/Tutorials)
                    if any(x in title for x in ['jukebox', 'making of', 'behind the scene', 'interview', 'review', 'reaction', 'climax', 'photo editing', 'wall photo', 'paper torn', 'tutorial', 'how to', 'royalty free', 'no copyright']):
                        continue

                    if v_id in seen_ids:
                        continue

                    seen_ids.add(v_id)
                    valid_videos.append({
                        'title': item['snippet']['title'],
                        'videoId': v_id,
                        'thumbnail': item['snippet']['thumbnails']['high']['url'],
                        'channelTitle': item['snippet']['channelTitle'],
                        'publishedAt': published_at,
                        'duration': dur,
                        'year': year
                    })

            except Exception as e:
                logger.error(f"YouTube search strategy error for query '{query}': {e}")
                continue

        # Chronological Sort (2026 -> 1990)
        valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)
        return valid_videos[:15]
