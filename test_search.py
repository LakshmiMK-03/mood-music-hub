import os
from googleapiclient.discovery import build
import json

def test_kannada_search():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("API KEY MISSING")
        return

    youtube = build('youtube', 'v3', developerKey=api_key)
    
    lang_str = "Kannada"
    emotion = "Sad"
    mood_terms = {
        'Happy': 'official full video song fast beat hits',
        'Sad': 'emotional movie song heart touching',
        'Angry': 'action mass movie song bgm',
        'Fearful': 'suspense thriller movie song',
        'Neutral': 'melody hit full video song',
        'Relaxed': 'pleasant soul melody song'
    }
    mood_query = mood_terms.get(emotion, 'top movie songs')
    
    # Try a broad query
    query = f"{lang_str} movie full video song {mood_query}"
    negative_filters = "-private -independent -cover -mashup -remix -shorts -piano -royalty -free -vlog -webseries -lofi -jukebox -dj -mix -8d -bass -scene -comedy -climax -reaction -review -trailer -teaser -interview -making -unplugged -karaoke"

    print(f"Testing Query: {query}")
    
    request = youtube.search().list(
        part="snippet",
        maxResults=20,
        q=f"{query} {negative_filters}",
        type="video",
        videoEmbeddable="true"
    )
    response = request.execute()
    
    for item in response.get('items', []):
        print(f"ID: {item['id']['videoId']} | Title: {item['snippet']['title']} | Channel: {item['snippet']['channelTitle']}")

if __name__ == "__main__":
    test_kannada_search()
