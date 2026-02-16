from youtube_client import YouTubeClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_language_search():
    client = YouTubeClient()
    
    if not client.youtube:
        print("Skipping test: No valid API key found.")
        return

    emotion = "Happy"
    languages = ["Hindi", "Punjabi"]
    
    print(f"Searching for {emotion} music in {languages}...")
    videos = client.search_music(emotion, languages)
    
    if videos:
        print(f"\nFound {len(videos)} videos:")
        for v in videos[:5]:
            duration = v.get('duration', 'N/A')
            try:
                print(f"- {v['title']} ({v['channelTitle']}) - {duration}s")
            except UnicodeEncodeError:
                safe_title = v['title'].encode('ascii', 'ignore').decode('ascii')
                safe_channel = v['channelTitle'].encode('ascii', 'ignore').decode('ascii')
                print(f"- {safe_title} ({safe_channel}) - {duration}s")
    else:
        print("No videos found.")

if __name__ == "__main__":
    test_language_search()
