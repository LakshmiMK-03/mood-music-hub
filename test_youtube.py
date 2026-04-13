from dotenv import load_dotenv
load_dotenv()
from youtube_client import YouTubeClient
client = YouTubeClient()

q = '\"Aditya Music\" Tollywood Telugu hit video song -bhakti -god -private'

print("Query:", q)
request = client.youtube.search().list(part='snippet', maxResults=10, q=q, type='video', videoEmbeddable='true', order='relevance')
res = request.execute()

video_ids = [item['id']['videoId'] for item in res.get('items', [])]
if not video_ids: print('No videos found for query')
else:
    details_request = client.youtube.videos().list(part='contentDetails,status,snippet', id=','.join(video_ids))
    detail_res = details_request.execute()
    
    verified_channels = ['aditya', 'mango music', 'saregama', 'sony music', 't-series', 'lahari', 'zee music', 'think music', 'sillywood', 'sun nxt', 'gemini', 'bhavani', 'tips', 'anand audio']
    
    for item in detail_res.get('items', []):
        title = item['snippet']['title'].lower()
        channel = item['snippet']['channelTitle'].lower()
        dur = item['contentDetails'].get('duration', '')
        
        print('--')
        print(channel, '|', title, '| Dur:', dur)
