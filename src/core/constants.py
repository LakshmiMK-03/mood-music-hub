# Emotion Mappings
EMOTION_MAP = {
    'Neutral': 0,
    'Happy': 1,
    'Sad': 2,
    'Angry': 3,
    'Fearful': 4,
    'Surprised': 5
}
ID_TO_EMOTION = {v: k for k, v in EMOTION_MAP.items()}

EMOJI_MAP = {
    'Happy': "😊",
    'Sad': "😟",
    'Angry': "😤",
    'Fearful': "😨",
    'Neutral': "😐",
    'Surprised': "😲"
}

# Relaxation and Feedback Data
RELAXATION_DATA = {
    'Happy': {
        'tips': [
            "Keep the momentum! Share your positive energy with someone today.",
            "Write down three things you are grateful for to anchor this feeling.",
            "Try a creative hobby like drawing or writing while you feel inspired."
        ],
        'affirmation': "I am deserving of this joy and I radiate positivity."
    },
    'Sad': {
        'tips': [
            "Acknowledge your feelings. It's okay to not be okay right now.",
            "Try Progressive Muscle Relaxation to release the physical weight of sadness.",
            "Reach out to a trusted friend or write your thoughts in a journal."
        ],
        'affirmation': "I am gentle with myself, and this feeling is temporary."
    },
    'Angry': {
        'tips': [
            "Use the 444 Breathing technique to lower your heart rate immediately.",
            "Chanel your energy into a physical activity like a brisk walk or workout.",
            "Try a 'Grounding' exercise: identify 5 things you see, 4 you feel, and 3 you hear."
        ],
        'affirmation': "I am in control of my reactions and I choose peace."
    },
    'Fearful': {
        'tips': [
            "Focus on the present moment. Anxiety lives in the future; peace lives now.",
            "Try Guided Visualization: imagine a 'safe haven' where you are completely protected.",
            "Reduce caffeine intake and try a warm, caffeine-free tea."
        ],
        'affirmation': "I am safe, I am grounded, and I am stronger than my fears."
    },
    'Neutral': {
        'tips': [
            "Take a short 'Digital Detox' break. Step away from screens for 15 minutes.",
            "Drink a glass of water—hydration is key to maintaining steady energy.",
            "Practice 'Mindful Observation': pick one object and notice every detail for a minute."
        ],
        'affirmation': "I am focused, calm, and ready for whatever the day brings."
    }
}
