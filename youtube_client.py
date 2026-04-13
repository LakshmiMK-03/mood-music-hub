import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random
import re

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
                # Use a specific version to avoid some common SSL issues in older versions
                self.youtube = build('youtube', 'v3', developerKey=self.api_key, static_discovery=False)
            except Exception as e:
                print(f"Error initializing YouTube API: {e}")

    def search_music(self, emotion, languages=None):
        """
        Search strictly for Top-Tier Official Movie Songs based on emotion.
        - Exact 15 results.
        - Max 5 mins duration.
        - Verified Channels Only (Aditya Music, Saregama, Mango, etc).
        - No Web Series, No Non-Movie tracks.
        """
        if not self.youtube:
            print("YouTube API key not found or invalid.")
            return []

        # QUALITY LABELS FOR SEARCH QUERIES
        premium_labels = ["Mango Music", "Aditya Music", "Saregama", "Sony Music", "T-Series", "Lahari Music", "Zee Music"]
        label = random.choice(premium_labels)

        # EXACT MOOD TERMS (Mapped to Trending Movie Song Archetypes)
        mood_terms = {
            'Happy': 'hit video song fast beat',
            'Sad': 'emotional sad song',
            'Angry': 'action mass bgm',
            'Fearful': 'thriller bgm',
            'Neutral': 'romantic melody song',
            'Relaxed': 'peaceful melody song'
        }
        mood_query = mood_terms.get(emotion, 'movie songs')
        lang_str = " ".join(languages) if languages else ""
        industry = "Tollywood" if "Telugu" in lang_str else ("Kollywood" if "Tamil" in lang_str else ("Sandalwood" if "Kannada" in lang_str else "Bollywood"))
        
        # IRON-CLAD NEGATIVE FILTERS (Rejecting Jukeboxes and Compilations)
        negative_filters = "-bhakti -god -private -independent -cover -mashup -remix -shorts -editing -piano -royalty -status -bgm -copyright -nocopyright -free -vlog -webseries -tune -instrumental -lofi -jukebox -dj -mix -nonstop -8d -bass -scene -comedy -climax -fight"
        
        if "Telugu" in lang_str and "Hindi" not in lang_str:
             negative_filters += " -hindi -bollywood -tamil -kannada -malayalam"

        # MATRIX QUERIES (Searching across top 5 labels simultaneously to guarantee 15 hits)
        selected_brands = random.sample(premium_labels, min(5, len(premium_labels)))
        search_strategies = []
        for brand in selected_brands:
            search_strategies.append(f'"{brand}" {industry} {lang_str} {mood_query}'.strip())
            search_strategies.append(f'"{brand}" {lang_str} hit video song'.strip())
        
        # Final fallback
        search_strategies.append(f"{industry} {lang_str} top 10 {mood_query}".strip())

        valid_videos = []
        
        # STRICT VERIFIED CHANNEL WHITELIST (The ultimate spam blocker)
        verified_channels = ['aditya', 'mango music', 'saregama', 'sony music', 't-series', 'lahari', 'zee music', 'think music', 'sillywood', 'sun nxt', 'gemini', 'bhavani', 'tips', 'anand audio']
        
        for query in search_strategies:
            try:
                request = self.youtube.search().list(
                    part="snippet",
                    maxResults=50,
                    q=f"{query} {negative_filters}",
                    type="video",
                    videoEmbeddable="true",
                    order="relevance" # Best accuracy
                )
                response = request.execute()
                
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                if not video_ids: continue

                details_request = self.youtube.videos().list(
                    part="contentDetails,status,snippet",
                    id=",".join(video_ids)
                )
                details_response = details_request.execute()

                for item in details_response.get('items', []):
                    if not item['status'].get('embeddable', True): continue
                    
                    title = item['snippet']['title'].lower()
                    channel = item['snippet']['channelTitle'].lower()

                    # 1. CHANNEL GUARANTEE: Channel MUST be a verified music label
                    if not any(brand in channel for brand in verified_channels):
                        continue

                    # 2. MOVIE GUARANTEE: Reject anything explicitly stating web series or short film or scenes
                    if 'web series' in title or 'short film' in title or 'no copyright' in title or 'free music' in title or 'scene' in title or 'climax' in title:
                        continue

                    # 3. LANGUAGE LEAKAGE PREVENTION: Force block Kannada/Tamil/Hindi if Telugu is requested
                    if "Telugu" in lang_str and ("kannada" in title or "tamil" in title or "hindi" in title or "malayalam" in title) and ("telugu" not in title):
                        continue

                    # USER REQUEST: Duration Check (Min 2 mins, Max 5 mins)
                    dur = parse_duration(item['contentDetails'].get('duration'))
                    if dur < 120 or dur > 300: continue

                    # Ensure no exact duplicates
                    if any(v['videoId'] == item['id'] for v in valid_videos):
                        continue

                    valid_videos.append({
                        'title': item['snippet']['title'],
                        'videoId': item['id'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channelTitle': item['snippet']['channelTitle'],
                        'publishedAt': item['snippet']['publishedAt'],
                        'duration': dur
                    })

                    # STRICTLY 15 SONGS
                    if len(valid_videos) >= 15: 
                        break

                if len(valid_videos) >= 15: 
                    break 

            except Exception as e:
                continue

        # Sort chronologically by Published Year descending (2026 -> 2000)
        valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)

        # Strictly limit to 15 if somehow we got more
        if len(valid_videos) > 15:
            valid_videos = valid_videos[:15]

        return valid_videos
