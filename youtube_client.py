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
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                print(f"Error initializing YouTube API: {e}")

    def search_music(self, emotion, languages=None):
        """
        Search for music videos based on emotion and optional languages.
        Returns a list of video dicts: {title, videoId, thumbnail, channelTitle}
        """
        if not self.youtube:
            print("YouTube API key not found or invalid.")
            return []

        # Map emotions to search queries
        queries = {
            'Happy': 'upbeat pop music happy vibes -sad -depressing -angry -dark',
            'Sad': 'sad acoustic songs piano -happy -upbeat -party -dance',
            'Angry': 'heavy metal rock aggressive music -calm -relaxing -soothing',
            'Fearful': 'calming ambient music for anxiety comfort -scary -horror -loud',
            'Neutral': 'lofi hip hop radio study relax -heavy -loud',
            'Relaxed': 'meditation music relaxation -rock -metal -techno'
        }

        query = queries.get(emotion, 'relaxing music')
        
        # Add languages to query if provided
        if languages and isinstance(languages, list):
            valid_langs = [l for l in languages if isinstance(l, str) and l.strip()]
            if valid_langs:
                lang_str = " ".join(valid_langs)
                query += f" {lang_str}"
        
        # Refine query to ensure songs, not shorts/reels
        query += ' "official audio" -shorts -reel'
        
        try:
            # Call YouTube Search API
            request = self.youtube.search().list(
                part="snippet",
                maxResults=15,
                q=query,
                type="video",
                videoEmbeddable="true",
                videoCategoryId="10",
                regionCode="IN" # Restrict to India to avoid geo-blocked content for the user
            )
            # Perform Search
            search_response = request.execute()

            # Extract Video IDs
            video_ids = []
            search_items = search_response.get('items', [])
            for item in search_items:
                video_ids.append(item['id']['videoId'])

            if not video_ids:
                return []

            # Step 2: Verify Details (Deep Filtering)
            # Fetch contentDetails and status to check for age restriction and embeddability
            details_request = self.youtube.videos().list(
                part="contentDetails,status,snippet",
                id=",".join(video_ids)
            )
            details_response = details_request.execute()

            valid_videos = []
            for item in details_response.get('items', []):
                # Check Embeddable
                if not item['status'].get('embeddable', True):
                    continue
                
                # Check Age Restriction
                content_rating = item['contentDetails'].get('contentRating', {})
                if 'ytAgeRestricted' in content_rating:
                    continue
                
                # Check Duration (2m to 7m)
                duration_str = item['contentDetails'].get('duration')
                duration_seconds = parse_duration(duration_str)
                if duration_seconds < 120 or duration_seconds > 420:
                    continue

                video = {
                    'title': item['snippet']['title'],
                    'videoId': item['id'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'channelTitle': item['snippet']['channelTitle'],
                    'duration': duration_seconds # Optional: specific for debugging or UI
                }
                valid_videos.append(video)
            
            # Shuffle to give variety
            random.shuffle(valid_videos)
            return valid_videos[:10] # Return top 10 valid ones

        except HttpError as e:
            print(f"An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
