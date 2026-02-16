"""
Train and save the text emotion classification model.
Uses TF-IDF feature extraction + Support Vector Machine (SVM) classifier.

Run this script once to generate the model files in the 'models/' directory.
Usage: python train_model.py
"""

import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Training data - labeled text samples for each emotion
training_data = [
    # Happy
    ("I am so happy today, everything is going great!", "Happy"),
    ("This is the best day of my life, I feel wonderful", "Happy"),
    ("I got promoted at work and I am thrilled", "Happy"),
    ("Feeling excited about the upcoming vacation", "Happy"),
    ("Love spending time with family, it makes me joyful", "Happy"),
    ("I passed my exam with flying colors, so proud", "Happy"),
    ("The weather is beautiful and I feel cheerful", "Happy"),
    ("My friends threw me a surprise party, I am delighted", "Happy"),
    ("Just got married, feeling blessed and grateful", "Happy"),
    ("Won the competition, feeling on top of the world", "Happy"),
    ("I feel so grateful for everything in my life", "Happy"),
    ("Laughing with friends always makes my day better", "Happy"),
    ("I love this sunny day, it makes me smile", "Happy"),
    ("Just received great news, I am ecstatic", "Happy"),
    ("Everything is falling into place, life is good", "Happy"),
    ("Having a wonderful time celebrating with loved ones", "Happy"),
    ("I feel confident and optimistic about the future", "Happy"),
    ("Such a fun and exciting experience today", "Happy"),
    ("My hard work finally paid off, feeling accomplished", "Happy"),
    ("I am at peace and content with everything around me", "Happy"),

    # Sad
    ("I feel so sad and alone today", "Sad"),
    ("Lost my beloved pet, I am heartbroken", "Sad"),
    ("Nothing seems to go right, feeling very down", "Sad"),
    ("I miss my family so much, feeling lonely", "Sad"),
    ("Failed the interview, feeling disappointed and upset", "Sad"),
    ("I am going through a difficult breakup", "Sad"),
    ("Feeling empty inside, nothing brings me joy anymore", "Sad"),
    ("My best friend moved away and I feel lost", "Sad"),
    ("I am grieving the loss of someone dear", "Sad"),
    ("Everything feels dark and hopeless right now", "Sad"),
    ("I can't stop crying, the pain is too much", "Sad"),
    ("I feel like nobody understands how I am feeling", "Sad"),
    ("The loneliness is overwhelming and suffocating", "Sad"),
    ("I feel worthless and like a failure", "Sad"),
    ("My heart aches and I feel so blue", "Sad"),
    ("I am really struggling with this loss", "Sad"),
    ("Today has been a terrible day, I feel miserable", "Sad"),
    ("Nothing excites me anymore, everything feels pointless", "Sad"),
    ("I feel abandoned and forgotten by everyone", "Sad"),
    ("The world feels cold and uncaring right now", "Sad"),

    # Angry
    ("I am so angry right now, this is unacceptable", "Angry"),
    ("People keep disrespecting me and I am furious", "Angry"),
    ("This situation makes me want to scream in rage", "Angry"),
    ("I hate being treated unfairly, it makes me mad", "Angry"),
    ("Someone lied to me and I am livid", "Angry"),
    ("I can't believe how rude that person was", "Angry"),
    ("This injustice makes my blood boil", "Angry"),
    ("I am frustrated with the system, nothing works properly", "Angry"),
    ("Stop bothering me, I am extremely irritated", "Angry"),
    ("They betrayed my trust and I am outraged", "Angry"),
    ("I feel so provoked by their behavior", "Angry"),
    ("Everything is going wrong because of their incompetence", "Angry"),
    ("I am disgusted by the way they handled this", "Angry"),
    ("Why can't people just do their job properly", "Angry"),
    ("I am fed up with all the lies and deception", "Angry"),
    ("This is infuriating and completely unacceptable", "Angry"),
    ("I want to punch something, I am so mad", "Angry"),
    ("Their arrogance and disrespect makes me hostile", "Angry"),
    ("I am bitter about how things turned out", "Angry"),
    ("People like them deserve no sympathy, so selfish", "Angry"),

    # Neutral
    ("Today was a normal day, nothing special happened", "Neutral"),
    ("I went to the store and bought groceries", "Neutral"),
    ("The meeting was okay, discussed some projects", "Neutral"),
    ("Weather is cloudy today, might rain later", "Neutral"),
    ("Had lunch and now working on assignments", "Neutral"),
    ("Just finished reading a chapter of my book", "Neutral"),
    ("Watching television while waiting for dinner", "Neutral"),
    ("The traffic was moderate on my way home", "Neutral"),
    ("Completed my daily routine as usual", "Neutral"),
    ("Nothing out of the ordinary happened today", "Neutral"),
    ("I woke up and had breakfast this morning", "Neutral"),
    ("Working on my project, it is going as expected", "Neutral"),
    ("I attended the lecture and took some notes", "Neutral"),
    ("The day was uneventful but productive enough", "Neutral"),
    ("I scheduled a meeting for tomorrow afternoon", "Neutral"),
    ("Checked my email and replied to a few messages", "Neutral"),
    ("The food was decent, nothing remarkable", "Neutral"),
    ("I organized my desk and filed some documents", "Neutral"),
    ("It was an average day at the office", "Neutral"),
    ("Waiting for the bus, should arrive in ten minutes", "Neutral"),

    # Fearful
    ("I am terrified about the upcoming surgery", "Fearful"),
    ("The dark alley scared me, I felt unsafe", "Fearful"),
    ("I have severe anxiety about my exam results", "Fearful"),
    ("The thunder and lightning frightened me badly", "Fearful"),
    ("I am worried about losing my job next month", "Fearful"),
    ("The pandemic makes me feel extremely anxious", "Fearful"),
    ("I dread going to the dentist, it scares me", "Fearful"),
    ("I feel threatened by the aggressive stranger", "Fearful"),
    ("Heights make me feel dizzy and panicked", "Fearful"),
    ("I am nervous about the presentation tomorrow", "Fearful"),
    ("I feel overwhelmed and trapped by everything", "Fearful"),
    ("The uncertainty of the future terrifies me", "Fearful"),
    ("I am afraid of failing and letting everyone down", "Fearful"),
    ("The nightmare last night left me shaken", "Fearful"),
    ("I feel insecure about my abilities and skills", "Fearful"),
    ("Something feels off and I am alarmed", "Fearful"),
    ("The stress is building up and I feel like panicking", "Fearful"),
    ("I am scared of being alone in this situation", "Fearful"),
    ("Every small noise makes me jump with fear", "Fearful"),
    ("I feel a constant sense of dread and unease", "Fearful"),
]


def preprocess_text(text):
    """Simple preprocessing: lowercase and remove special chars."""
    import re
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
    """Train the emotion classification model and save to disk."""

    # Prepare data
    texts = [preprocess_text(t) for t, _ in training_data]
    labels = [l for _, l in training_data]

    # TF-IDF Feature Extraction
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    X = tfidf.fit_transform(texts)

    # Split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # Train SVM classifier
    model = SVC(kernel='linear', probability=True, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {model.score(X_test, y_test) * 100:.1f}%")

    # Save models
    os.makedirs('models', exist_ok=True)
    with open('models/text_emotion_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf, f)

    print("\n✅ Model saved to models/text_emotion_model.pkl")
    print("✅ TF-IDF vectorizer saved to models/tfidf_vectorizer.pkl")

    # Test a few examples
    print("\n=== Quick Test ===")
    test_texts = [
        "I am so happy and excited today!",
        "I feel sad and lonely",
        "This makes me angry and frustrated",
        "I went to the store today",
        "I am terrified about the exam"
    ]
    for text in test_texts:
        processed = preprocess_text(text)
        features = tfidf.transform([processed])
        emotion = model.predict(features)[0]
        proba = max(model.predict_proba(features)[0])
        print(f"  \"{text}\" → {emotion} ({proba * 100:.0f}%)")


if __name__ == '__main__':
    train()
