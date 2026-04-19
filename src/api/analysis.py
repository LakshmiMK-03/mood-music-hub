from flask import Blueprint, request, jsonify, session
import os
import re
from src.services import supabase_service
from src.models import emotion_engine
from src.core.config import Config
from src.core.exceptions import ValidationError, AuthError
from src.utils.logger import setup_logging

logger = setup_logging("analysis_api")
analysis_bp = Blueprint('analysis', __name__)

def is_gibberish(text):
    alpha_text = ''.join(filter(str.isalpha, text))
    if not alpha_text: return False
    if re.search(r'[^aeiouyAEIOUY]{6,}', alpha_text): return True
    if not re.search(r'[aeiouyAEIOUY]', alpha_text): return True
    return False

def require_auth():
    user = session.get('user')
    if not user:
        raise AuthError("Please sign in to use the analyzer.")
    return user

@analysis_bp.route('/api/analyze/text', methods=['POST'])
def analyze_text_route():
    user = require_auth()
    data = request.get_json() or {}
    text = data.get('text', '').strip()

    if not text:
        raise ValidationError("Text cannot be empty")
        
    if is_gibberish(text):
        raise ValidationError("Invalid input; please enter a valid sentence.")

    result = emotion_engine.analyze_text(text)
    
    supabase_service.log_analysis(
        user.get('id'), 'text', text, 
        result['emotion'], result['stress_level'], 
        result['confidence'], result.get('stress_score', 0.0)
    )
    
    session['last_emotion'] = result['emotion']
    return jsonify(result)

@analysis_bp.route('/api/analyze/image', methods=['POST'])
def analyze_image_route():
    user = require_auth()
    if 'image' not in request.files:
        raise ValidationError("No image provided")

    file = request.files['image']
    if file.filename == '':
        raise ValidationError("No image selected")

    temp_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_{user['id']}.jpg")
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(temp_path)

    try:
        result = emotion_engine.analyze_image_emotion(temp_path)
        if result.get('face_detected'):
            supabase_service.log_analysis(
                user.get('id'), 'image', None, 
                result['emotion'], result['stress_level'], 
                result['confidence'], result.get('stress_score', 0.0)
            )
            session['last_emotion'] = result['emotion']
        return jsonify(result)
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@analysis_bp.route('/api/analyze/image_string', methods=['POST'])
def analyze_image_string_route():
    user = require_auth()
    data = request.get_json() or {}
    img_data = data.get('image')

    if not img_data:
        raise ValidationError("No image data provided")

    result = emotion_engine.analyze_image_base64(img_data)
    supabase_service.log_analysis(
        user.get('id'), 'image_camera', None, 
        result['emotion'], result['stress_level'], 
        result['confidence'], result.get('stress_score', 0.0)
    )
    session['last_emotion'] = result['emotion']
    return jsonify(result)
