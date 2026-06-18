import asyncio
import json
import math
import os
import random
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Disable extra runtime tracking print statements from TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore

app = FastAPI()

# --- 📂 HYBRID PATH ANCHORING ENGINE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")

# Smart Fallback Tracker: Checks if 'saved_model' exists; if not, reads from backend root
PRIMARY_MODEL_DIR = os.path.join(BASE_DIR, "saved_model")
if os.path.exists(os.path.join(PRIMARY_MODEL_DIR, "ensemble_anchors.npz")):
    SAVED_MODEL_DIR = PRIMARY_MODEL_DIR
    print("📂 Rooted target folder located at: backend/saved_model/")
else:
    SAVED_MODEL_DIR = BASE_DIR
    print("📂 Subfolder missing; fallback engaged to: backend/ root directory")

# --- 🚀 TELEMETRY SIMULATION SIMULATOR CONTROL CORE ---
TARGETS = {
    "oxygen": 21.04, "pressure": 101.32, "temperature": 22.15, "vibration": 0.021, "solar_flux": 453.0
}
active_anomalies = {
    "o2_rise": False, "o2_fall": False, "press_rise": False, "press_fall": False,
    "temp_rise": False, "temp_fall": False, "vibration": False, "solar": False
}
system_metrics = {
    "oxygen": 21.04, "pressure": 101.32, "temperature": 22.15, "vibration": 0.021, "solar_flux": 453.0,
    "transformer_loss": 0.0, "accumulated_damage": 0.0
}

WINDOW_SIZE = 30
atmos_buffer, ext_buffer = [], []

print("🧠 Loading Trained Twin-Brain Transformer Models via Absolute Anchoring...")
anchors = np.load(os.path.join(SAVED_MODEL_DIR, "ensemble_anchors.npz"))
atmos_min, atmos_max = anchors["atmos_min"], anchors["atmos_max"]
ext_min, ext_max     = anchors["ext_min"], anchors["ext_max"]

atmos_brain = load_model(os.path.join(SAVED_MODEL_DIR, "atmos_brain.keras"))
ext_brain   = load_model(os.path.join(SAVED_MODEL_DIR, "ext_brain.keras"))
print("✅ Neural architectures verified and operational.")

def evaluate_ensemble_intelligence():
    global atmos_buffer, ext_buffer
    raw_atmos = np.array([system_metrics["oxygen"], system_metrics["pressure"], system_metrics["temperature"]])
    scaled_atmos = (raw_atmos - atmos_min) / (atmos_max - atmos_min)

    raw_ext = np.array([system_metrics["vibration"], system_metrics["solar_flux"]])
    scaled_ext = (raw_ext - ext_min) / (ext_max - ext_min)

    atmos_buffer.append(scaled_atmos)
    ext_buffer.append(scaled_ext)

    if len(atmos_buffer) > WINDOW_SIZE: atmos_buffer.pop(0)
    if len(ext_buffer) > WINDOW_SIZE: ext_buffer.pop(0)

    if len(atmos_buffer) < WINDOW_SIZE:
        system_metrics["transformer_loss"] = 0.0
        return

    tensor_atmos = np.expand_dims(np.array(atmos_buffer), axis=0)
    tensor_ext   = np.expand_dims(np.array(ext_buffer), axis=0)

    recon_atmos = atmos_brain(tensor_atmos, training=False)
    loss_atmos  = float(np.mean((tensor_atmos - recon_atmos.numpy()) ** 2))

    recon_ext   = ext_brain(tensor_ext, training=False)
    loss_ext    = float(np.mean((tensor_ext - recon_ext.numpy()) ** 2))

    loss_token_atmos = (loss_atmos - 0.005) * 45.0 if loss_atmos > 0.005 else 0.0
    loss_token_ext   = (loss_ext - 0.008) * 35.0 if loss_ext > 0.008 else 0.0

    system_metrics["transformer_loss"] = loss_token_atmos + loss_token_ext

def advance_physics_frame():
    if active_anomalies["o2_rise"]: system_metrics["oxygen"] = min(30.0, system_metrics["oxygen"] + 0.015)
    elif active_anomalies["o2_fall"]: system_metrics["oxygen"] = max(12.0, system_metrics["oxygen"] - 0.018)
    else: system_metrics["oxygen"] += (TARGETS["oxygen"] - system_metrics["oxygen"]) * 0.03

    if active_anomalies["press_rise"]: system_metrics["pressure"] = min(125.0, system_metrics["pressure"] + 0.05)
    elif active_anomalies["press_fall"]: system_metrics["pressure"] = max(75.0, system_metrics["pressure"] - 0.06)
    else: system_metrics["pressure"] += (TARGETS["pressure"] - system_metrics["pressure"]) * 0.03

    if active_anomalies["temp_rise"]: system_metrics["temperature"] = min(40.0, system_metrics["temperature"] + 0.02)
    elif active_anomalies["temp_fall"]: system_metrics["temperature"] = max(8.0, system_metrics["temperature"] - 0.022)
    else: system_metrics["temperature"] += (TARGETS["temperature"] - system_metrics["temperature"]) * 0.03

    if active_anomalies["vibration"]:
        system_metrics["vibration"] = 0.22
        active_anomalies["vibration"] = False 
    else: 
        vibe_deviation = system_metrics["vibration"] - TARGETS["vibration"]
        system_metrics["vibration"] = TARGETS["vibration"] + (vibe_deviation * 0.85)

    orbital_wave = math.sin(asyncio.get_event_loop().time() * 0.05) * 14.0
    cosmic_noise = random.uniform(-1.0, 1.0)
    if active_anomalies["solar"]: system_flux_target = min(920.0, system_metrics["solar_flux"] + 1.5)
    else: system_flux_target = TARGETS["solar_flux"] + orbital_wave + cosmic_noise
    system_metrics["solar_flux"] += (system_flux_target - system_metrics["solar_flux"]) * 0.03

    system_metrics["oxygen"] += random.uniform(-0.002, 0.002)
    system_metrics["pressure"] += random.uniform(-0.01, 0.01)
    system_metrics["temperature"] += random.uniform(-0.003, 0.003)
    system_metrics["vibration"] += random.uniform(-0.0005, 0.0005)

    if system_metrics["transformer_loss"] > 0.0:
        system_metrics["accumulated_damage"] = min(0.45, system_metrics["accumulated_damage"] + 0.001)
    else:
        system_metrics["accumulated_damage"] = max(0.0, system_metrics["accumulated_damage"] - 0.0006)

# --- 📡 FASTAPI WEB NETWORK EXPOSURE ROUTING ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 Secure WebSocket Connection Opened.")
    try:
        while True:
            try:
                data_msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                data = json.loads(data_msg)
                if "command" in data:
                    cmd = data["command"]
                    if cmd == "nominal":
                        for key in active_anomalies: active_anomalies[key] = False
                        atmos_buffer.clear()
                        ext_buffer.clear()
                    elif cmd in active_anomalies: active_anomalies[cmd] = True
                    elif cmd.startswith("clear_"):
                        target_key = cmd.replace("clear_", "")
                        if target_key in active_anomalies: active_anomalies[target_key] = False
            except asyncio.TimeoutError:
                pass

            advance_physics_frame()
            evaluate_ensemble_intelligence()

            payload = {
                "oxygen": round(system_metrics["oxygen"], 2), "pressure": round(system_metrics["pressure"], 2),
                "temperature": round(system_metrics["temperature"], 2), "vibration": round(system_metrics["vibration"], 3),
                "solar_flux": int(system_metrics["solar_flux"]), "transformer_loss": float(system_metrics["transformer_loss"]),
                "accumulated_damage": float(system_metrics["accumulated_damage"]), "active_matrix": active_anomalies
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("🔌 WebSocket Connection Terminated Cleanly.")

# Mount and serve compiled React files automatically from static index structures
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST_DIR, "assets")), name="assets")

@app.get("/{catchall:path}")
async def serve_react_frontend(catchall: str):
    file_path = os.path.join(FRONTEND_DIST_DIR, catchall)
    if catchall and os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(FRONTEND_DIST_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
