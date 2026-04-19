from flask import Blueprint, request, jsonify
from src.services import youtube_service
from src.core.exceptions import ValidationError

music_bp = Blueprint('music', __name__)

@music_bp.route('/api/music/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    emotion = data.get('emotion', 'Neutral')
    languages = data.get('languages', [])
    
    videos = youtube_service.search_music(emotion, languages)
    return jsonify({'videos': videos})
