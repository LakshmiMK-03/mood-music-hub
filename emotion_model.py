"""
Emotion Detection Module
Uses Ensemble (Logistic Regression + Naive Bayes) + VADER for improved accuracy.
"""

import os
import pickle
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Paths to saved models
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
LR_MODEL_PATH = os.path.join(MODEL_DIR, 'lr_emotion_model.pkl')
NB_MODEL_PATH = os.path.join(MODEL_DIR, 'nb_emotion_model.pkl')
TFIDF_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

analyzer = SentimentIntensityAnalyzer()

# Emotion labels
EMOTIONS = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']

# Stress keywords for adjustment
STRESS_HIGH_KEYWORDS = ['overwhelmed', 'panic', 'can\'t cope', 'hopeless', 'exhausted', 'suicidal', 'rage']
STRESS_LOW_KEYWORDS = ['happy', 'relaxed', 'calm', 'peaceful', 'content', 'grateful']

def preprocess_text(text):
    """NLP preprocessing: lowercase, remove special chars, and normalize elongated words."""
    import re
    if not isinstance(text, str): return ""
    text = text.lower()
    
    # Normalize elongated words (e.g., "happyyyyy" -> "happy")
    # First, handle common cases like "ooo" -> "oo" (good -> good) but "yyyy" -> "y"
    # A safe way is to reduce any 3+ repeated chars to 1 or 2.
    # We'll use 1 for the keyword check and 2 for the ML model (to keep "good", "happy")
    text = re.sub(r'(.)\1{2,}', r'\1\1', text) 
    
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves'}
    tokens = [t for t in tokens if t not in stop_words]
    return ' '.join(tokens)

def get_vader_stress(text):
    """Calculate stress impact using VADER sentiment scores."""
    scores = analyzer.polarity_scores(text)
    # Compound score: -1 (very negative/stressed) to +1 (very positive)
    # We map negative compound to higher stress impact
    return max(0.0, -float(scores['compound'])) 

def calculate_stress_score(text, emotion_probas, emotion_labels):
    """Hybrid stress calculation joining VADER + ML + Keywords."""
    text_lower = text.lower()
    proba_dict = dict(zip(emotion_labels, emotion_probas))
    
    # 1. ML Contribution
    ml_base = (
        proba_dict.get('Fearful', 0) * 1.0 +
        proba_dict.get('Angry', 0) * 0.8 +
        proba_dict.get('Sad', 0) * 0.4 -
        proba_dict.get('Happy', 0) * 0.6
    )
    ml_norm = max(0.0, min(1.0, float((ml_base + 0.6) / 1.6)))
    
    # 2. VADER Contribution
    vader_impact = get_vader_stress(text)
    
    # 3. Keyword Contribution
    high_k = sum(1 for kw in STRESS_HIGH_KEYWORDS if kw in text_lower)
    low_k = sum(1 for kw in STRESS_LOW_KEYWORDS if kw in text_lower)
    keyword_impact = (high_k * 0.15) - (low_k * 0.15)
    
    final_score = (ml_norm * 0.5) + (vader_impact * 0.4) + (keyword_impact)
    final_score = max(0.0, min(1.0, float(final_score))) * 100.0
    
    if final_score > 70: return 'High', float(f"{final_score:.1f}")
    elif final_score > 35: return 'Medium', float(f"{final_score:.1f}")
    else: return 'Low', float(f"{final_score:.1f}")

def analyze_text(text):
    """
    Analyze text input using an ensemble of models and VADER.
    """
    processed = preprocess_text(text)

    if os.path.exists(LR_MODEL_PATH) and os.path.exists(NB_MODEL_PATH) and os.path.exists(TFIDF_PATH):
        try:
            with open(TFIDF_PATH, 'rb') as f: tfidf = pickle.load(f)
            with open(LR_MODEL_PATH, 'rb') as f: lr_model = pickle.load(f)
            with open(NB_MODEL_PATH, 'rb') as f: nb_model = pickle.load(f)

            features = tfidf.transform([processed])
            lr_probas = lr_model.predict_proba(features)[0]
            nb_probas = nb_model.predict_proba(features)[0]
            
            # Weighted average for Ensemble (LR gets slightly more weight)
            final_probas = (lr_probas * 0.6) + (nb_probas * 0.4)
            labels = lr_model.classes_
            
            # Find top emotion
            max_idx = np.argmax(final_probas)
            emotion = str(labels[max_idx])
            
            # --- Emotion Override / Boost Logic ---
            text_lower = text.lower()
            # Normalize to single chars to catch "happyyyyyy" as "hapy"
            import re
            text_keyword_norm = re.sub(r'(.)\1+', r'\1', text_lower)
            
            # Map normalized keywords to target emotions
            keyword_map = {
                'Happy': ['hapy', 'joy', 'smile', 'bright', 'glad', 'excite', 'awesom', 'wonder'],
                'Sad': ['sad', 'unhapy', 'lonely', 'cry', 'hurt', 'miser', 'depres'],
                'Angry': ['angry', 'mad', 'furious', 'rage', 'hate', 'irrit'],
                'Fearful': ['afraid', 'scare', 'terify', 'panic', 'anxi']
            }
            
            # Apply detection boost
            keyword_found = None
            for em_target, kws in keyword_map.items():
                if any(k in text_keyword_norm for k in kws):
                    # Boost the probability of this emotion
                    idx = list(labels).index(em_target)
                    final_probas[idx] += 0.4
                    keyword_found = em_target
            
            # Re-evaluate top emotion after boost
            max_idx = np.argmax(final_probas)
            emotion = str(labels[max_idx])
            
            # Initial Confidence based on ML probabilities
            sorted_probas = sorted(final_probas, reverse=True)
            gap = float(sorted_probas[0] - sorted_probas[1]) if len(sorted_probas) > 1 else float(sorted_probas[0])
            base_conf = (float(sorted_probas[0]) * 70) + (gap * 30)
            
            # --- Advanced Confidence Boost ---
            v_scores = analyzer.polarity_scores(text)
            compound = v_scores['compound']
            
            boost = 0
            if emotion == 'Happy' and compound > 0.2: boost += 20 * compound
            elif emotion in ['Sad', 'Angry', 'Fearful'] and compound < -0.2: boost += 20 * abs(compound)
            
            if keyword_found == emotion: boost += 15
            
            confidence = min(100.0, float(base_conf + boost))
            confidence = float(f"{confidence:.1f}")

            # --- Multi-Model Emotion Check ---
            if confidence < 50 and abs(compound) > 0.6:
                if compound > 0.6: emotion = "Happy"
                elif compound < -0.6: emotion = "Sad" 
                confidence = float(f"{abs(compound) * 100:.1f}")

            # Integrated Stress Calculation
            stress_level, stress_score = calculate_stress_score(text, final_probas, labels)

            return {
                'emotion': emotion,
                'stress_level': stress_level,
                'stress_score': stress_score,
                'confidence': confidence
            }
        except Exception as e:
            print(f"Prediction Error: {e}")
            return _keyword_fallback(text)
    return _keyword_fallback(text)

def _keyword_fallback(text):
    """Basic dictionary fallback with substring matching."""
    text_lower = text.lower()
    # Normalize for fallback check too
    import re
    text_norm = re.sub(r'(.)\1{2,}', r'\1\1', text_lower)
    
    if any(k in text_norm for k in ['happy', 'joy', 'smile', 'bright', 'glad']): em = 'Happy'
    elif any(k in text_norm for k in ['sad', 'unhappy', 'lonely', 'cry', 'hurt']): em = 'Sad'
    elif any(k in text_norm for k in ['angry', 'mad', 'furious', 'rage', 'hate']): em = 'Angry'
    elif any(k in text_norm for k in ['scared', 'afraid', 'terrified', 'panic']): em = 'Fearful'
    else: em = 'Neutral'
    
    return {
        'emotion': em,
        'stress_level': 'Medium' if em in ['Sad', 'Angry', 'Fearful'] else 'Low',
        'stress_score': 50.0,
        'confidence': 60.0
    }

def analyze_image_emotion(image_path):
    """
    Stay consistent with existing image analysis.
    """
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None: return {'error': 'Image not found', 'face_detected': False}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        if len(faces) == 0:
            return {'emotion': 'Neutral', 'stress_level': 'Low', 'confidence': 50.0, 'face_detected': False}
            
        (x, y, w, h) = faces[0]
        roi = gray[y:y+h, x:x+w]
        mean, std = float(np.mean(roi)), float(np.std(roi))
        
        if mean > 140 and std > 50: em = 'Happy'
        elif mean < 80: em = 'Sad'
        elif std > 60: em = 'Angry'
        elif std < 30: em = 'Fearful'
        else: em = 'Neutral'
        
        stress_map = {'Happy': 'Low', 'Neutral': 'Low', 'Sad': 'Medium', 'Fearful': 'High', 'Angry': 'High'}
        
        return {
            'emotion': em,
            'stress_level': stress_map.get(em, 'Medium'),
            'confidence': 75.0,
            'face_detected': True
        }
    except Exception as e:
        return {'emotion': 'Neutral', 'stress_level': 'Low', 'confidence': 50.0, 'face_detected': False, 'msg': str(e)}
