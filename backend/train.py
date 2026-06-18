import os
import pandas as pd
import numpy as np
import tensorflow as tf
from model.brain import build_transformer_autoencoder
from model.pipeline import TelemetryPipeline

def execute_model_training():
    print("==============================================")
    print("     SPONITOR: AI CORE TRAINING PIPELINE      ")
    print("==============================================")
    
    # 1. Load the recorded nominal training dataset
    csv_path = os.path.join(os.path.dirname(__file__), "data", "healthy_telemetry.csv")
    if not os.path.exists(csv_path):
        print(f"[ERROR] Training dataset not found at {csv_path}. Run generate_training_data.py first!")
        return
        
    df = pd.read_csv(csv_path)
    print(f"[INFO] Successfully loaded {len(df)} lines of baseline telemetry.")
    
    # 2. Convert CSV rows into sequential rolling window blocks
    pipeline = TelemetryPipeline(window_size=30)
    processed_sequences = []
    
    print("[PROCESSING] Shifting data vectors into 30-step temporal matrices...")
    for _, row in df.iterrows():
        packet = row.to_dict()
        sequence_block = pipeline.process_incoming_packet(packet)
        if sequence_block is not None:
            # Strip out the extra batch dimension for training array alignment
            processed_sequences.append(sequence_block[0])
            
    X_train = np.array(processed_sequences)
    print(f"[INFO] Training tensor shape finalized: {X_train.shape}")
    
    # 3. Instantiate and compile our Transformer model structure
    print("[INITIALIZING] Building Time-Series Transformer Autoencoder...")
    model = build_transformer_autoencoder(window_size=30, num_features=5)
    
    # 4. Fit the weights
    # Both input and target are X_train because it's reconstructing its own input!
    print("[TRAINING] Starting neural network optimization loops...")
    model.fit(
        X_train, 
        X_train, 
        epochs=10, 
        batch_size=64, 
        validation_split=0.1,
        verbose=1
    )
    
    # 5. Export the trained binary weights safely to disk
    model_dir = os.path.join(os.path.dirname(__file__), "saved_model")
    os.makedirs(model_dir, exist_ok=True)
    model.save(os.path.join(model_dir, "transformer_brain.keras"))
    print(f"\n[SUCCESS] AI Transformer weights trained and exported cleanly to {model_dir}/transformer_brain.keras")

if __name__ == "__main__":
    execute_model_training()