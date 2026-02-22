from youtube_client import YouTubeClient
import os

# Ensure dummy key if not set
if not os.getenv('YOUTUBE_API_KEY'):
    os.environ['YOUTUBE_API_KEY'] = 'YOUR_API_KEY_HERE'

client = YouTubeClient()
print(f"API Key present: {bool(client.api_key)}")

results = client.search_music('Happy')
print(f"Results for 'Happy': {results}")

if not results:
    print("✅ Correctly returned empty list (expected without valid API key)")
else:
    print("⚠️ Returned results (unexpected if key is invalid)")
