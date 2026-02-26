from emotion_model import analyze_text

def run_real_world_test():
    """
    Test the model with a diverse set of real-world samples 
    extracted from the GoEmotions dataset + custom stress scenarios.
    """
    test_cases = [
        # --- Happy / Positive ---
        ("Happy", "This is so wholesome and sweet, I love it!"),
        ("Happy", "I'm so proud of you and all your hard work!"),
        ("Happy", "Everything is going perfectly today!"),
        
        # --- Sad / Low Sentiment ---
        ("Sad", "I lost my dog yesterday and I can't stop crying."),
        ("Sad", "It hurts so much to see them go."),
        ("Sad", "I feel so lonely and empty inside."),
        
        # --- Angry / High Arousal ---
        ("Angry", "I am so sick and tired of this constant disrespect!"),
        ("Angry", "This is absolutely unacceptable and I am furious!"),
        ("Angry", "Stop annoying me before I lose my temper!"),
        
        # --- Fearful / High Stress ---
        ("Fearful", "I'm absolutely terrified of what might happen next."),
        ("Fearful", "My house is shaking and I am freaking out!"),
        ("Fearful", "I have a panic attack every time I think about the exam."),
        
        # --- Stress Level Specifics ---
        ("Low Stress", "I am enjoying a peaceful afternoon in the park."),
        ("Medium Stress", "I have so much to do and not enough time, I'm getting worried."),
        ("High Stress", "I'm at my breaking point, I can't breathe, everything is too much!"),
    ]
    
    print(f"{'Target':<15} | {'Emotion':<10} | {'Stress':<8} | {'Conf %':<7} | {'Input Text'}")
    print("-" * 100)
    
    for target, text in test_cases:
        res = analyze_text(text)
        emotion = res.get('emotion', 'N/A')
        stress = res.get('stress_level', 'N/A')
        conf = res.get('confidence', 0.0)
        
        print(f"{target:<15} | {emotion:<10} | {stress:<8} | {conf:<7} | {text}")

if __name__ == "__main__":
    print("=== Real-World Emotional Detection Verification ===\n")
    run_real_world_test()
