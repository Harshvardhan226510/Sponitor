import os
import numpy as np
import tensorflow as tf
from model.brain import build_specialized_transformer

# 1. GENERATE SYNTHETIC NOMINAL TRAINING DATA (1000 timesteps of clean flight)
print("📥 Generating clean nominal training dataset...")
np.random.seed(42)
timesteps = 1000
window_size = 30

raw_o2    = np.random.normal(21.04, 0.05, timesteps)
raw_press = np.random.normal(101.32, 0.2, timesteps)
raw_temp  = np.random.normal(22.15, 0.05, timesteps)
raw_vibe  = np.random.normal(0.021, 0.002, timesteps)
raw_solar = 453.0 + np.sin(np.linspace(0, 20, timesteps)) * 14.0 + np.random.normal(0, 0.5, timesteps)

# 2. SEPARATE SCALING LOGIC NATIVELY
# Brain 1: Atmospheric Metrics (Strict 0.0 to 1.0 limits based ONLY on their own max ranges)
atmos_raw = np.column_stack([raw_o2, raw_press, raw_temp])
atmos_min, atmos_max = np.array([10.0, 60.0, 0.0]), np.array([35.0, 140.0, 50.0])
atmos_scaled = (atmos_raw - atmos_min) / (atmos_max - atmos_min)

# Brain 2: External Environment Metrics
ext_raw = np.column_stack([raw_vibe, raw_solar])
ext_min, ext_max = np.array([0.0, 300.0]), np.array([0.5, 1100.0])
ext_scaled = (ext_raw - ext_min) / (ext_max - ext_min)

# 3. CREATE SLIDING WINDOW ARRAYS FOR TRAINING
def create_windows(data, window_size):
    windows = []
    for i in range(len(data) - window_size + 1):
        windows.append(data[i:i+window_size])
    return np.array(windows)

X_atmos = create_windows(atmos_scaled, window_size)
X_ext   = create_windows(ext_scaled, window_size)

# 4. BUILD AND TRAIN THE TWIN NEURAL ENSEMBLE
os.makedirs("saved_model", exist_ok=True)

print("🧠 Training Atmospheric Capsule Brain...")
atmos_brain = build_specialized_transformer(window_size, num_features=3, name="Atmos_Brain")
atmos_brain.fit(X_atmos, X_atmos, epochs=15, batch_size=32, verbose=0)
atmos_brain.save("saved_model/atmos_brain.keras")
print("✅ Saved model weights to saved_model/atmos_brain.keras")

print("🧠 Training External Environment Brain...")
ext_brain = build_specialized_transformer(window_size, num_features=2, name="Ext_Brain")
ext_brain.fit(X_ext, X_ext, epochs=15, batch_size=32, verbose=0)
ext_brain.save("saved_model/ext_brain.keras")
print("✅ Saved model weights to saved_model/ext_brain.keras")

# Save calibration footprints safely for the backend server
print("💾 Saving structural anchor arrays...")
np.savez("saved_model/ensemble_anchors.npz", 
         atmos_min=atmos_min, atmos_max=atmos_max,
         ext_min=ext_min, ext_max=ext_max)
print("🚀 Training complete! Run your server script next.")