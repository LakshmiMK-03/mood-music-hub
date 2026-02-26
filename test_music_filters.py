import os
from dotenv import load_dotenv
from youtube_client import YouTubeClient

load_dotenv()

client = YouTubeClient()
emotions = ["Happy", "Sad"]
languages_to_test = ["Telugu", "Kannada"]

for lang in languages_to_test:
    for emotion in emotions:
        print(f"\n--- Testing: {lang} | {emotion} ---")
        results = client.search_music(emotion, languages=[lang])
        print(f"Total videos found: {len(results)}")
        
        for i, v in enumerate(results[:5]): # Show top 5
            print(f"  {i+1}. {v['title']}")

print("\nFinal Verification Complete.")
