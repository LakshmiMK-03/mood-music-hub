from emotion_model import analyze_text
import os

# Set dummy env vars if needed
os.environ['HF_TOKEN'] = 'dummy'

try:
    print("Testing analyze_text...")
    result = analyze_text("I am feeling very happy today")
    print("Result:", result)
except Exception as e:
    print("Error in analyze_text:", e)
