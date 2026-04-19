import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')
print(f"Testing API Key: {api_key[:10]}...")

try:
    youtube = build('youtube', 'v3', developerKey=api_key)
    # Very safe search
    query = "Telugu new movie songs"
    request = youtube.search().list(
        part="snippet",
        maxResults=5,
        q=query,
        type="video"
    )
    response = request.execute()
    print(f"Results found: {len(response.get('items', []))}")
    for item in response.get('items', []):
        print(f" - {item['snippet']['title']}")
except Exception as e:
    print(f"API ERROR: {e}")
