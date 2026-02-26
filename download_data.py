import os
import requests
import csv

# Dataset URLs from Google Research
URLS = [
    "https://storage.googleapis.com/gresearch/goemotions/data/full_dataset/goemotions_1.csv",
    "https://storage.googleapis.com/gresearch/goemotions/data/full_dataset/goemotions_2.csv",
    "https://storage.googleapis.com/gresearch/goemotions/data/full_dataset/goemotions_3.csv"
]

# Mapping GoEmotions labels to project labels
# Project labels: Happy, Sad, Angry, Fearful, Neutral
LABEL_MAPPING = {
    # Happy
    "admiration": "Happy",
    "amusement": "Happy",
    "approval": "Happy",
    "caring": "Happy",
    "excitement": "Happy",
    "gratitude": "Happy",
    "joy": "Happy",
    "love": "Happy",
    "optimism": "Happy",
    "pride": "Happy",
    "relief": "Happy",
    
    # Sad
    "sadness": "Sad",
    "disappointment": "Sad",
    "grief": "Sad",
    "remorse": "Sad",
    
    # Angry
    "anger": "Angry",
    "annoyance": "Angry",
    "disapproval": "Angry",
    "disgust": "Angry",
    
    # Fearful
    "fear": "Fearful",
    "nervousness": "Fearful",
    
    # Neutral
    "neutral": "Neutral"
}

# The goemotions CSV has columns: text, emotion1, emotion2, ... (binary 0/1)
# We need to find which column corresponds to which emotion.
EMOTION_COLUMNS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", 
    "confusion", "curiosity", "desire", "disappointment", "disapproval", 
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief", 
    "joy", "love", "nervousness", "optimism", "pride", "realization", 
    "relief", "remorse", "sadness", "surprise", "neutral"
]

DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "goemotions_raw.csv")
MAPPED_FILE = os.path.join(DATA_DIR, "goemotions_mapped.csv")

def download_files():
    """Download all 3 GoEmotions CSV files and combine them."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(RAW_FILE):
        print(f"File {RAW_FILE} already exists. Skipping download.")
        return

    print("Downloading GoEmotions dataset (this may take a minute)...")
    headers_written = False
    with open(RAW_FILE, "w", encoding="utf-8", newline="") as combined_file:
        writer = csv.writer(combined_file)
        for url in URLS:
            print(f"Fetching {url}...")
            response = requests.get(url)
            response.raise_for_status()
            
            # Use csv module to handle potential quoting issues
            lines = response.text.strip().split('\n')
            reader = csv.reader(lines)
            
            header = next(reader)
            if not headers_written:
                writer.writerow(header)
                headers_written = True
            
            for row in reader:
                writer.writerow(row)
    
    print(f"Dataset downloaded and saved to {RAW_FILE}")

def map_labels():
    """Map the 27 GoEmotions to our 5 project labels."""
    print("Mapping labels...")
    
    with open(RAW_FILE, "r", encoding="utf-8") as f_in, \
         open(MAPPED_FILE, "w", encoding="utf-8", newline="") as f_out:
        
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=["text", "emotion"])
        writer.writeheader()
        
        counts = {"Happy": 0, "Sad": 0, "Angry": 0, "Fearful": 0, "Neutral": 0, "Skipped": 0}
        
        for row in reader:
            text = row["text"]
            mapped_emotion = None
            
            # Find the first emotion that is set to '1' and has a mapping
            for em in EMOTION_COLUMNS:
                if row.get(em) == "1" and em in LABEL_MAPPING:
                    mapped_emotion = LABEL_MAPPING[em]
                    break
            
            if mapped_emotion:
                writer.writerow({"text": text, "emotion": mapped_emotion})
                counts[mapped_emotion] += 1
            else:
                counts["Skipped"] += 1
                
    print(f"Mapping complete. Saved to {MAPPED_FILE}")
    print("Statistics:")
    for label, count in counts.items():
        print(f"  {label}: {count}")

if __name__ == "__main__":
    try:
        download_files()
        map_labels()
    except Exception as e:
        print(f"An error occurred: {e}")
