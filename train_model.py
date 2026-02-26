"""
Train and save the text emotion classification model using GoEmotions dataset.
Trains an ensemble: Logistic Regression + Multinomial Naive Bayes.
"""

import os
import pickle
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re

DATA_FILE = "data/goemotions_mapped.csv"
MODEL_DIR = "models"

def preprocess_text(text):
    """NLP preprocessing pipeline: lowercase and remove special chars."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
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

def train():
    """Train the emotion classification models and save to disk."""
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Run download_data.py first.")
        return

    print(f"Loading data from {DATA_FILE}...")
    texts = []
    labels = []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(preprocess_text(row["text"]))
            labels.append(row["emotion"])

    print(f"Loaded {len(texts)} samples.")

    # TF-IDF Feature Extraction
    print("Extracting TF-IDF features...")
    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X = tfidf.fit_transform(texts)

    # Split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # 1. Train Logistic Regression
    print("Training Model 1: Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    print("LR Accuracy:", lr_model.score(X_test, y_test))

    # 2. Train Naive Bayes
    print("Training Model 2: Multinomial Naive Bayes...")
    nb_model = MultinomialNB()
    nb_model.fit(X_train, y_train)
    print("NB Accuracy:", nb_model.score(X_test, y_test))

    # Save models
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(os.path.join(MODEL_DIR, 'lr_emotion_model.pkl'), 'wb') as f:
        pickle.dump(lr_model, f)
    with open(os.path.join(MODEL_DIR, 'nb_emotion_model.pkl'), 'wb') as f:
        pickle.dump(nb_model, f)
    with open(os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl'), 'wb') as f:
        pickle.dump(tfidf, f)

    print(f"\n✅ Models saved to {MODEL_DIR}/")

if __name__ == '__main__':
    train()
