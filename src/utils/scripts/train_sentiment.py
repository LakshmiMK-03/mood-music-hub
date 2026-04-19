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

# 1. Configuration
DATA_PATH = "data/goemotions_mapped.csv"
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = "models/sentiment_model"
LOG_DIR = "./logs"

# Label mapping to ensure consistency
EMOTION_MAP = {
    'Neutral': 0,
    'Happy': 1,
    'Sad': 2,
    'Angry': 3,
    'Fearful': 4
}
ID_TO_EMOTION = {v: k for k, v in EMOTION_MAP.items()}

def train():
    print(f">>> 🚀 Starting Training Pipeline for {MODEL_NAME}...")

    # 2. Load and Prepare Data
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f">>> 📊 Dataset loaded: {len(df)} rows.")

    # Convert labels to IDs
    df['label'] = df['emotion'].map(EMOTION_MAP)
    
    # Drop any rows with unmapped emotions if they exist
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)

    # Split data
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
    )

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=LOG_DIR,
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to="none" # Disable wandb etc for local runs
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
    print(">>> 🏋️ Training model (this may take a while)...")
    trainer.train()

    # 8. Save Final Model
    print(f">>> 💾 Saving best model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(">>> ✅ Training Complete!")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(os.path.dirname(OUTPUT_DIR), exist_ok=True)
    train()
