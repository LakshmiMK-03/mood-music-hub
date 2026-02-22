"""
Emotion Detection Module
Uses TF-IDF + Scikit-learn for text-based emotion classification.
Uses OpenCV + a simple model for facial emotion recognition.
"""

import os
import pickle
import numpy as np

# Paths to saved models
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
TEXT_MODEL_PATH = os.path.join(MODEL_DIR, 'text_emotion_model.pkl')
TFIDF_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

# Emotion labels
EMOTIONS = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']

# Stress keywords mapping
STRESS_HIGH_KEYWORDS = [
    'overwhelmed', 'panic', 'can\'t cope', 'breaking down', 'hopeless',
    'exhausted', 'desperate', 'terrified', 'crisis', 'burnout',
    'suicidal', 'depressed', 'anxious', 'unbearable', 'suffering',
    'miserable', 'devastated', 'furious', 'rage', 'breaking point'
]

STRESS_MEDIUM_KEYWORDS = [
    'stressed', 'worried', 'nervous', 'tense', 'pressure',
    'frustrated', 'annoyed', 'upset', 'uncertain', 'confused',
    'tired', 'restless', 'uneasy', 'struggle', 'difficult',
    'bothered', 'irritated', 'unhappy', 'concerned', 'anxious'
]

STRESS_LOW_KEYWORDS = [
    'happy', 'relaxed', 'calm', 'peaceful', 'content',
    'joyful', 'grateful', 'excited', 'wonderful', 'great',
    'fine', 'good', 'okay', 'well', 'comfortable',
    'cheerful', 'optimistic', 'hopeful', 'confident', 'relieved'
]


def preprocess_text(text):
    """
    NLP preprocessing pipeline:
    1. Lowercasing
    2. Tokenization
    3. Stop-word removal
    """
    import re

    # Step 1: Lowercasing
    text = text.lower()

    # Step 2: Remove special characters (keep only letters and spaces)
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Step 3: Tokenization
    tokens = text.split()

    # Step 4: Stop-word removal (common English stop words)
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
        'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
        'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
        'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
        'against', 'between', 'through', 'during', 'before', 'after',
        'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
        'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
    }
    tokens = [t for t in tokens if t not in stop_words]

    return ' '.join(tokens)


def predict_stress_level(text):
    """
    Predict stress level based on keyword analysis.
    Returns: 'Low', 'Medium', or 'High'
    """
    text_lower = text.lower()

    high_count = sum(1 for kw in STRESS_HIGH_KEYWORDS if kw in text_lower)
    medium_count = sum(1 for kw in STRESS_MEDIUM_KEYWORDS if kw in text_lower)
    low_count = sum(1 for kw in STRESS_LOW_KEYWORDS if kw in text_lower)

    if high_count >= 2 or (high_count >= 1 and medium_count >= 2):
        return 'High'
    elif medium_count >= 2 or (medium_count >= 1 and high_count >= 1):
        return 'Medium'
    elif high_count >= 1:
        return 'Medium'
    else:
        return 'Low'


def analyze_text(text):
    """
    Analyze text input for emotion and stress.
    Uses trained TF-IDF + ML model if available, otherwise falls back to keyword-based.

    Returns: dict with emotion, stress_level, confidence
    """
    # Preprocess
    processed = preprocess_text(text)

    # Try to use trained model
    if os.path.exists(TEXT_MODEL_PATH) and os.path.exists(TFIDF_PATH):
        try:
            with open(TFIDF_PATH, 'rb') as f:
                tfidf = pickle.load(f)
            with open(TEXT_MODEL_PATH, 'rb') as f:
                model = pickle.load(f)

            features = tfidf.transform([processed])
            emotion = model.predict(features)[0]

            # Get confidence from probability
            probas = model.predict_proba(features)[0]
            confidence = round(float(max(probas)) * 100, 1)

        except Exception as e:
            print(f"Model prediction error: {e}")
            emotion, confidence = _keyword_emotion(processed)
    else:
        emotion, confidence = _keyword_emotion(processed)

    # Predict stress
    stress = predict_stress_level(text)

    return {
        'emotion': emotion,
        'stress_level': stress,
        'confidence': confidence
    }


def _keyword_emotion(text):
    """
    Fallback keyword-based emotion detection.
    """
    emotion_keywords = {
        'Happy': ['happy', 'joy', 'excited', 'wonderful', 'great', 'awesome',
                   'love', 'amazing', 'fantastic', 'cheerful', 'delighted',
                   'glad', 'pleased', 'thrilled', 'ecstatic', 'blessed',
                   'grateful', 'optimistic', 'smile', 'laugh', 'fun',
                   'celebrate', 'proud', 'confident', 'bright'],
        'Sad': ['sad', 'depressed', 'unhappy', 'miserable', 'heartbroken',
                'lonely', 'grief', 'sorrow', 'crying', 'tears', 'lost',
                'hopeless', 'gloomy', 'down', 'blue', 'disappointed',
                'devastated', 'hurt', 'pain', 'suffering', 'empty'],
        'Angry': ['angry', 'furious', 'mad', 'irritated', 'annoyed',
                  'frustrated', 'rage', 'hate', 'disgusted', 'outraged',
                  'livid', 'hostile', 'bitter', 'resentful', 'aggressive',
                  'infuriated', 'provoked', 'offended', 'enraged'],
        'Fearful': ['afraid', 'scared', 'terrified', 'anxious', 'worried',
                    'nervous', 'panic', 'frightened', 'dread', 'horror',
                    'phobia', 'uneasy', 'alarmed', 'threatened', 'insecure',
                    'overwhelmed', 'stress', 'tension', 'fear', 'trembling'],
    }

    text_lower = text.lower()
    scores = {}

    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[emotion] = score

    max_score = max(scores.values())

    if max_score == 0:
        return 'Neutral', 72.0

    detected = max(scores, key=scores.get)
    # Confidence based on how many keywords matched
    confidence = min(65 + (max_score * 8), 98)

    return detected, float(confidence)


def analyze_image_emotion(image_path):
    """
    Analyze facial emotion from image using OpenCV for face detection.
    Uses a simple approach: OpenCV Haar Cascade for face detection +
    keyword-based fallback (in production, a CNN model would be used).

    Returns: dict with emotion, stress_level, confidence, face_detected
    """
    try:
        import cv2

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return {'error': 'Could not read image', 'face_detected': False}

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        if len(faces) == 0:
            return {
                'emotion': 'Neutral',
                'stress_level': 'Low',
                'confidence': 50.0,
                'face_detected': False,
                'message': 'No face detected in the image. Please upload a clear face photo.'
            }

        # Face detected - analyze facial features
        # In a full implementation, the face ROI would be passed to a CNN model
        # For demo, we use a simple brightness/contrast heuristic
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]

        # Analyze face characteristics
        mean_val = np.mean(face_roi)
        std_val = np.std(face_roi)

        # Simple heuristic based on face brightness and contrast
        if mean_val > 140 and std_val > 50:
            emotion = 'Happy'
            confidence = 78.0
        elif mean_val < 80:
            emotion = 'Sad'
            confidence = 72.0
        elif std_val > 60:
            emotion = 'Angry'
            confidence = 70.0
        elif std_val < 30:
            emotion = 'Fearful'
            confidence = 68.0
        else:
            emotion = 'Neutral'
            confidence = 75.0

        # Stress from emotion
        stress_map = {
            'Happy': 'Low', 'Neutral': 'Low',
            'Sad': 'Medium', 'Fearful': 'High', 'Angry': 'High'
        }

        return {
            'emotion': emotion,
            'stress_level': stress_map.get(emotion, 'Medium'),
            'confidence': confidence,
            'face_detected': True,
            'faces_count': len(faces)
        }

    except ImportError:
        return {
            'emotion': 'Neutral',
            'stress_level': 'Low',
            'confidence': 60.0,
            'face_detected': False,
            'message': 'OpenCV is not installed. Install it with: pip install opencv-python'
        }
    except Exception as e:
        return {
            'emotion': 'Neutral',
            'stress_level': 'Low',
            'confidence': 50.0,
            'face_detected': False,
            'message': f'Error analyzing image: {str(e)}'
        }
