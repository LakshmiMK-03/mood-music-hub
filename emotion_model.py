"""
Emotion Detection Module - Binary-Free Stable Version
Uses VADER + Keyword mapping for high reliability without native dependencies.
"""

import os
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Removed numpy and cv2 to prevent Access Violation crashes on this system.

analyzer = SentimentIntensityAnalyzer()

# Emotion labels
EMOTIONS = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']

# Stress keywords
STRESS_HIGH_KEYWORDS = ['overwhelmed', 'panic', 'can\'t cope', 'hopeless', 'exhausted', 'suicidal', 'rage']
STRESS_LOW_KEYWORDS = ['happy', 'relaxed', 'calm', 'peaceful', 'content', 'grateful']

def preprocess_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'(.)\1{2,}', r'\1\1', text) 
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves'}
    tokens = [t for t in tokens if t not in stop_words]
    return ' '.join(tokens)

def calculate_stress_score(text, emotion):
    text_lower = text.lower()
    scores = analyzer.polarity_scores(text)
    vader_impact = max(0.0, -float(scores['compound'])) 
    
    high_k = sum(1 for kw in STRESS_HIGH_KEYWORDS if kw in text_lower)
    low_k = sum(1 for kw in STRESS_LOW_KEYWORDS if kw in text_lower)
    keyword_impact = (high_k * 0.15) - (low_k * 0.15)
    
    # Base stress from emotion
    em_base = 0.5 if emotion in ['Sad', 'Angry', 'Fearful'] else 0.1
    
    final_score = (em_base * 0.4) + (vader_impact * 0.4) + (keyword_impact * 0.2)
    final_score = max(0.0, min(1.0, float(final_score))) * 100.0
    
    if final_score > 70: return 'High', float(f"{final_score:.1f}")
    elif final_score > 35: return 'Medium', float(f"{final_score:.1f}")
    else: return 'Low', float(f"{final_score:.1f}")

def analyze_text(text):
    text_lower = text.lower()
    text_norm = re.sub(r'(.)\1{2,}', r'\1\1', text_lower)
    
    # Keyword detection
    if any(k in text_norm for k in ['happy', 'joy', 'smile', 'bright', 'glad', 'awesome']): em = 'Happy'
    elif any(k in text_norm for k in ['sad', 'unhappy', 'lonely', 'cry', 'hurt', 'depressed']): em = 'Sad'
    elif any(k in text_norm for k in ['angry', 'mad', 'furious', 'rage', 'hate']): em = 'Angry'
    elif any(k in text_norm for k in ['scared', 'afraid', 'terrified', 'panic', 'anxious']): em = 'Fearful'
    else:
        # VADER fallback
        scores = analyzer.polarity_scores(text)
        comp = scores['compound']
        if comp > 0.4: em = 'Happy'
        elif comp < -0.4: em = 'Sad'
        else: em = 'Neutral'
    
    stress_level, stress_score = calculate_stress_score(text, em)
    
    return {
        'emotion': em,
        'stress_level': stress_level,
        'stress_score': stress_score,
        'confidence': 85.0
    }

def analyze_image_emotion(image_path):
    """Fallback version without CV2/Numpy."""
    return {
        'emotion': 'Neutral', 
        'stress_level': 'Low', 
        'confidence': 50.0, 
        'face_detected': False, 
        'msg': 'Image analysis requires binary libraries currently disabled for stability.'
    }
