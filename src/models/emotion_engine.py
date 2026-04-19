import os
import re
import hashlib
import requests
import base64
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.core.config import Config
from src.utils.logger import setup_logging

logger = setup_logging("emotion_engine")

# Global instances for reuse
analyzer = SentimentIntensityAnalyzer()
MP_DETECTOR = None
IMAGE_INFERENCE_CACHE = {}

# MediaPipe configuration from Config
MP_MODEL_PATH = os.path.join(Config.BASE_DIR, "models", "face_landmarker.task")
MP_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

# --- Initialization Utilities ---

def download_mediapipe_model():
    """Downloads the MediaPipe Face Landmarker model if not present."""
    if os.path.exists(MP_MODEL_PATH): return True
    
    os.makedirs(os.path.dirname(MP_MODEL_PATH), exist_ok=True)
    logger.info(f"Downloading MediaPipe model to {MP_MODEL_PATH}...")
    try:
        response = requests.get(MP_MODEL_URL, timeout=30)
        if response.status_code == 200:
            with open(MP_MODEL_PATH, "wb") as f:
                f.write(response.content)
            logger.info("MediaPipe model successfully downloaded.")
            return True
        return False
    except Exception as e:
        logger.error(f"Error downloading MediaPipe model: {e}")
        return False

def get_mediapipe_detector():
    """Lazily initialize the MediaPipe Face Landmarker."""
    global MP_DETECTOR
    if MP_DETECTOR is not None: return MP_DETECTOR
        
    try:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        
        if not download_mediapipe_model(): return None
            
        base_options = python.BaseOptions(model_asset_path=MP_MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            num_faces=1
        )
        MP_DETECTOR = vision.FaceLandmarker.create_from_options(options)
        return MP_DETECTOR
    except Exception as e:
        logger.error(f"Failed to initialize MediaPipe: {e}")
        return None

# --- Helper Functions ---

def get_image_hash(image_path):
    hash_md5 = hashlib.md5()
    try:
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception: return None

def calculate_stress_score(text_or_emotion, emotion):
    """Refactored stress score logic."""
    scores = analyzer.polarity_scores(text_or_emotion)
    vader_impact = max(0.0, -float(scores['compound'])) 
    
    # Base stress from emotion
    em_base = 0.5 if emotion in ['Sad', 'Angry', 'Fearful'] else 0.1
    
    final_score = (em_base * 0.6) + (vader_impact * 0.4)
    final_score = max(0.0, min(1.0, float(final_score))) * 100.0
    
    if final_score > 70: level = 'High'
    elif final_score > 35: level = 'Medium'
    else: level = 'Low'
    
    return level, float(f"{final_score:.1f}")

# --- Primary Analysis Functions ---

def analyze_text(text):
    """Performs text-based emotion and stress analysis."""
    try:
        if not text or not text.strip():
            return {'emotion': 'Neutral', 'stress_level': 'Low', 'stress_score': 0.0, 'confidence': 0.0}
            
        scores = analyzer.polarity_scores(text)
        comp = scores.get('compound', 0)
        
        if comp > 0.4: 
            em = 'Happy'
            confidence = 75.0
        elif comp < -0.4: 
            em = 'Sad'
            confidence = 75.0
        else:
            em = 'Neutral'
            confidence = 50.0
            
        stress_level, stress_score = calculate_stress_score(text, em)
        
        return {
            'emotion': em,
            'stress_level': stress_level,
            'stress_score': stress_score,
            'confidence': confidence
        }
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        return {'emotion': 'Neutral', 'stress_level': 'Low', 'stress_score': 0.0, 'confidence': 0.0}

def analyze_image_emotion(image_path):
    """Cloud-offloaded image analysis using local MediaPipe fallback."""
    img_hash = get_image_hash(image_path)
    if img_hash and img_hash in IMAGE_INFERENCE_CACHE:
        return IMAGE_INFERENCE_CACHE[img_hash]

    detector = get_mediapipe_detector()
    if detector:
        try:
            import mediapipe as mp
            import cv2
            abs_path = os.path.abspath(image_path)
            
            try:
                img_mp = mp.Image.create_from_file(abs_path)
            except Exception:
                # Fallback to OpenCV if MediaPipe's direct loading fails
                cv_img = cv2.imread(abs_path)
                if cv_img is None:
                    raise ValueError(f"Could not read image from {abs_path}")
                cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                img_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_img)
                
            detection_result = detector.detect(img_mp)
            
            if detection_result.face_blendshapes:
                blendshapes = {b.category_name: b.score for b in detection_result.face_blendshapes[0]}
                
                scores = {
                    'Happy': max(blendshapes.get('mouthSmileLeft', 0), blendshapes.get('mouthSmileRight', 0)),
                    'Sad': (blendshapes.get('mouthFrownLeft', 0) + blendshapes.get('mouthFrownRight', 0) + blendshapes.get('browInnerUp', 0)) / 3,
                    'Angry': (blendshapes.get('browDownLeft', 0) + blendshapes.get('browDownRight', 0) + blendshapes.get('mouthPressLeft', 0)) / 3,
                    'Fearful': (blendshapes.get('browInnerUp', 0) + blendshapes.get('eyeWideLeft', 0) + blendshapes.get('eyeWideRight', 0)) / 3
                }
                
                winner = max(scores, key=scores.get)
                confidence = scores[winner]
                
                if confidence < 0.25:
                    winner = 'Neutral'
                    confidence = 1.0 - max(scores.values())
                
                stress_level, stress_score = calculate_stress_score(winner, winner)
                
                result = {
                    'emotion': winner, 'stress_level': stress_level, 'stress_score': stress_score,
                    'confidence': float(f"{confidence * 100:.1f}"), 'face_detected': True,
                    'message': 'Analysis Complete.'
                }
                if img_hash: IMAGE_INFERENCE_CACHE[img_hash] = result
                return result
        except Exception as e:
            logger.error(f"MediaPipe Inference Error: {e}")

    # Final Fallback
    return {
        'emotion': 'Neutral', 'stress_level': 'Low', 'stress_score': 10.0,
        'confidence': 50.0, 'face_detected': False, 'message': 'Detection unavailable.'
    }

def analyze_image_base64(base64_str):
    """Analyzes an image provided as a Base64 string."""
    try:
        if ',' in base64_str: base64_str = base64_str.split(',')[1]
        image_data = base64.b64decode(base64_str)
        content_hash = hashlib.md5(image_data).hexdigest()
        temp_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_str_{content_hash[:10]}.jpg")
        
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        with open(temp_path, "wb") as f: f.write(image_data)
            
        try:
            return analyze_image_emotion(temp_path)
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)
    except Exception as e:
        logger.error(f"Base64 Image error: {e}")
        return {'emotion': 'Neutral', 'stress_level': 'Low', 'confidence': 0.0}
