"""
Emotion Detection Module - Binary-Free Stable Version
Uses VADER + Keyword mapping for high reliability without native dependencies.
"""

import os
import re
import hashlib
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    from PIL import Image
except ImportError:
    Image = None

# In-memory inference cache mapping: SHA256 -> Emotion Data
IMAGE_INFERENCE_CACHE = {}

def get_image_hash(image_path):
    hash_md5 = hashlib.md5()
    try:
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

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
    """
    Cloud-offloaded image analysis using HuggingFace Inference API.
    Fault Tolerant: Caching, Auto-Resize (Payload Compression), and Timeout Fallbacks.
    """
    # 1. Cryptographic Memoization (Caching)
    img_hash = get_image_hash(image_path)
    if img_hash and img_hash in IMAGE_INFERENCE_CACHE:
        print(f">>> ✅ Image Hash matched in CACHE! Bypassing API delay.")
        return IMAGE_INFERENCE_CACHE[img_hash]

    # 2. Payload Compression (Resize to 224x224 JPEG)
    try:
        if Image:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img = img.resize((224, 224), Image.LANCZOS)
                img.save(image_path, "JPEG", quality=85)
                print(">>> 📉 Image successfully shrunk to 224x224.")
    except Exception as e:
        print(f"PIL Resize Error: {e}")

    # 3. Cloud API Inference Execution w/ Timeout
    HF_API_URL = "https://api-inference.huggingface.co/models/dima806/facial_emotions_image_detection"
    headers = {}
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
        
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        print(">>> 🌐 Sending payload to HuggingFace API...")
        response = requests.post(HF_API_URL, headers=headers, data=image_bytes, timeout=20)
        
        if response.status_code == 200:
            predictions = response.json()
            if isinstance(predictions, list) and len(predictions) > 0 and isinstance(predictions[0], list):
                 predictions = predictions[0]

            if predictions and len(predictions) > 0:
                top_pred = predictions[0]
                label = top_pred.get("label", "neutral").lower()
                score = top_pred.get("score", 0.5)
                
                em = 'Neutral'
                if any(k in label for k in ['happ', 'joy']): em = 'Happy'
                elif any(k in label for k in ['sad', 'disgust', 'sorrow']): em = 'Sad'
                elif any(k in label for k in ['ang', 'mad']): em = 'Angry'
                elif any(k in label for k in ['fear', 'scare', 'surprise']): em = 'Fearful'
                
                stress_level, stress_score = calculate_stress_score(em, em)
                
                result = {
                    'emotion': em,
                    'stress_level': stress_level,
                    'stress_score': stress_score,
                    'confidence': float(f"{score * 100:.1f}"),
                    'face_detected': True
                }
                
                # Store in Cache
                if img_hash:
                    IMAGE_INFERENCE_CACHE[img_hash] = result
                    
                return result
        else:
            print(f"HF API Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Image API Timeout or System Error: {e}")
        
    # 4. Graceful Fallback
    return {
        'emotion': 'Neutral', 
        'stress_level': 'Low',
        'stress_score': 10.0,
        'confidence': 50.0, 
        'face_detected': False, 
        'msg': 'Image API timeout or rate limit exceeded. Falling back to Neutral.'
    }
