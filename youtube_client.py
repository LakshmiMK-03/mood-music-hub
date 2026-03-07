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
        Search for music videos based on emotion and optional languages.
        """
        if not self.youtube:
            print("YouTube API key not found or invalid.")
            return []

        # QUALITY LABELS
        premium_labels = ["Mango Music", "Zee Music South", "Aditya Music", "T-Series", "Saregama", "Sony Music South", "Lahari Music", "Tips"]
        label = random.choice(premium_labels)

        # MOOD TERMS (Strictly Movie focused)
        mood_terms = {
            'Happy': 'upbeat happy movie songs official',
            'Sad': 'emotional sad movie songs lyrical',
            'Angry': 'action movie background score OST',
            'Fearful': 'thriller suspense movie score',
            'Neutral': 'peaceful movie melodies',
            'Relaxed': 'relaxing film background score'
        }
        mood_query = mood_terms.get(emotion, 'movie songs')
        lang_str = " ".join(languages) if languages else ""
        # MULTI-PHASE SEARCH LOGIC
        industry = "Tollywood" if "Telugu" in lang_str else ("Kollywood" if "Tamil" in lang_str else ("Sandalwood" if "Kannada" in lang_str else "Bollywood"))
        
        # IRON-CLAD FILTERS (YouTube Side)
        # Use slightly fewer negative keywords in query to avoid 0 results, but keep the strongest ones
        negative_filters = "-bhakti -god -private -independent -cover -live -mashup -remix -shorts -republic"
        
        if "Telugu" in lang_str and "Hindi" not in lang_str:
            negative_filters += " -hindi -bollywood"

        # USER REQUEST: 2010 to 2025
        year_options = ['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2015', '2010', '']
        year = random.choice(year_options)

        # Broad strategies to ensure we ALWAYS find something
        search_strategies = [
            f"{label} {industry} {lang_str} {mood_query} {year}".strip(),
            f"{industry} {lang_str} official movie songs {mood_query} {random.choice(['2025', '2024'])}".strip(),
            f"{lang_str} film cinema {mood_query} songs".strip(),
            f"{industry} movie hits {lang_str}".strip() # Ultima fallback
        ]

        debug_log_path = os.path.join(os.path.dirname(__file__), 'youtube_debug.log')
        with open(debug_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n--- Iron-Clad Optimized Search ({emotion}) ---\n")

        valid_videos = []
        
        # MANDATORY TERMS: Must be a movie/official channel content
        cinema_whitelist = ['movie', 'film', 'cinema', 'tollywood', 'bollywood', 'kollywood', 'sandalwood', 'soundtrack', 'ost', 'official', 'original', 't-series', 'mango', 'zee', 'aditya', 'sony', 'lahari']
        
        # PROHIBITED TERMS: No matter what, these are blocked
        prohibited_blacklist = ['private', 'independent', 'indie', 'cover', 'instrumental', 'remake', 'bhakti', 'god', 'mashup', 'remix', 'dj']
        
        strict_telugu = ("Telugu" in lang_str and "Hindi" not in lang_str)

        for query in search_strategies:
            try:
                with open(debug_log_path, 'a', encoding='utf-8') as f:
                    f.write(f"Trying Query: {query}\n")

                request = self.youtube.search().list(
                    part="snippet",
                    maxResults=50,
                    q=f"{query} {negative_filters}",
                    type="video",
                    videoEmbeddable="true",
                    order="relevance" # Relevance is safer than 'date' for zero-results
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

                    # 1. Mandatory Cinema Check (Strict)
                    if not any(word in title or word in channel for word in cinema_whitelist):
                        continue

                    # 2. Strict Blacklist
                    if any(word in title for word in prohibited_blacklist):
                        continue
                    
                    # 3. Language Check
                    if strict_telugu and "hindi" in title and "telugu" not in title:
                        continue

                    # USER REQUEST: Year Check (2010-2025)
                    published_at = item['snippet']['publishedAt']
                    year_val = int(published_at[:4])
                    if year_val < 2010 or year_val > 2025: continue

                    # Duration Check (180s - 600s or 3m - 10m)
                    dur = parse_duration(item['contentDetails'].get('duration'))
                    if dur < 180 or dur > 600: continue

                    valid_videos.append({
                        'title': item['snippet']['title'],
                        'videoId': item['id'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channelTitle': item['snippet']['channelTitle'],
                        'publishedAt': published_at,
                        'duration': dur
                    })

                if len(valid_videos) >= 20: 
                    break 

            except Exception as e:
                with open(debug_log_path, 'a', encoding='utf-8') as f:
                    f.write(f"Query ERROR: {e}\n")
                continue

        # FINAL CHRONOLOGY LOGIC: Strictly 2025 -> 2010
        valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)

        # Variety Sampling while keeping it "Trending" (Top 50 newest/highest relevance)
        if len(valid_videos) > 18:
            pool = valid_videos[:50] 
            valid_videos = random.sample(pool, 18)
            # Re-sort to ensure descending order after sampling
            valid_videos.sort(key=lambda x: x['publishedAt'], reverse=True)

        # Logging for Verification
        with open(debug_log_path, 'a', encoding='utf-8') as f:
            f.write(f"Strict Sorted Results (Count: {len(valid_videos)}):\n")
            for i, v in enumerate(valid_videos):
                f.write(f" {i+1}. [{v['publishedAt'][:10]}] {v['title']}\n")

        return valid_videos
