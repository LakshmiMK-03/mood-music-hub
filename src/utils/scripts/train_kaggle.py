import os
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset

# 1. Configuration (Updated for Kaggle)
# Change DATA_PATH to point to your uploaded dataset in Kaggle Inputs
DATA_PATH = "/kaggle/input/goemotions-mapped/goemotions_mapped.csv" 
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = "./sentiment_model_trained"
LOG_DIR = "./logs"

# Label mapping (Must match the Mood Music Hub system)
EMOTION_MAP = {
    'Neutral': 0,
    'Happy': 1,
    'Sad': 2,
    'Angry': 3,
    'Fearful': 4
}
ID_TO_EMOTION = {v: k for k, v in EMOTION_MAP.items()}

def train():
    print(f">>> 🚀 Starting Kaggle Training Pipeline for {MODEL_NAME}...")
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f">>> 💻 Training Device: {device.upper()}")

    # 2. Load and Prepare Data
    if not os.path.exists(DATA_PATH):
        print(f"!!! Error: Dataset not found at {DATA_PATH}. Make sure to add the CSV to Kaggle Inputs.")
        return

    df = pd.read_csv(DATA_PATH)
    print(f">>> 📊 Dataset loaded: {len(df)} rows.")

    df['label'] = df['emotion'].map(EMOTION_MAP)
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)

    # Split data (85% Train, 15% Eval)
    train_df, val_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df['label'])
    
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)

    # 3. Tokenization
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize_func(examples):
        return tokenizer(examples['text'], truncation=True, padding=True, max_length=128)

    print(">>> 🔤 Tokenizing dataset...")
    train_dataset = train_dataset.map(tokenize_func, batched=True)
    val_dataset = val_dataset.map(tokenize_func, batched=True)

    # 4. Model Initialization
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=len(EMOTION_MAP),
        id2label=ID_TO_EMOTION,
        label2id=EMOTION_MAP
    ).to(device)

    # 5. Training Arguments (Optimized for Kaggle GPU)
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16 if device == "cuda" else 8,
        per_device_eval_batch_size=16 if device == "cuda" else 8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=LOG_DIR,
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=True if device == "cuda" else False, # Mixed precision for faster GPU training
        report_to="none"
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # 6. Trainer API
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    # 7. Execute Training
    print(">>> 🏋️ Training model...")
    trainer.train()

    # 8. Save Final Model
    print(f">>> 💾 Saving best model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    # 9. ZIP the output (Easy to download from Kaggle)
    import shutil
    shutil.make_archive("sentiment_model_ready", 'zip', OUTPUT_DIR)
    print(">>> ✅ ZIP Archive created: sentiment_model_ready.zip")
    print(">>> 🎉 Training Complete!")

if __name__ == "__main__":
    train()
