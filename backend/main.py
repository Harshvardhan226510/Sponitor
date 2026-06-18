import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import numpy as np
import tensorflow as tf
from model.pipeline import TelemetryPipeline

# =====================================================================
# CORE AI INTELLECT INITIALIZATION
# =====================================================================
# Initialize our runtime data processing sliding window
pipeline = TelemetryPipeline(window_size=30)

# Load our trained Transformer model weights from disk
MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model", "transformer_brain.keras")
try:
    transformer_brain = tf.keras.models.load_model(MODEL_PATH)
    print("[SERVER STATUS] Time-Series Transformer Brain loaded successfully into memory.")
except Exception as e:
    print(f"[SERVER ERROR] Failed to load Transformer weights: {e}")
    transformer_brain = None

# Initialize the core FastAPI application
app = FastAPI(title="Sponitor: Lunar Digital Twin Backend")

# =====================================================================
# 1. CORS CONFIGURATION (Cross-Origin Resource Sharing)
# =====================================================================
# Why? Our React frontend will run on a different port (e.g., localhost:5173) 
# than our FastAPI server (localhost:8000). Modern browsers block web apps 
# from talking across different ports unless the server explicitly allows it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all connections (perfect for local development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all types of HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all network headers
)

# =====================================================================
# 2. ACTIVE CONNECTION POOLS
# =====================================================================
# These sets will act as an in-memory database keeping track of who is 
# currently connected to our space communication hub.
active_clients = set()       # Keeps track of all open React dashboard tabs
active_simulators = set()    # Keeps track of our active telemetry simulator


# =====================================================================
# 3. SIMULATOR TELEMETRY INGEST ENDPOINT
# =====================================================================
# This endpoint opens a dedicated pipe for our Python data generator.
@app.websocket("/ws/simulator")
async def websocket_simulator_endpoint(websocket: WebSocket):
    # Accept the incoming network handshake from the simulator
    await websocket.accept()
    active_simulators.add(websocket)
    print("[SERVER] Lunar Simulator telemetry link established.")
    
    try:
        while True:
            # Wait asynchronously for the simulator to drop off a 500ms packet
            raw_data = await websocket.receive_text()
            
            # Parse the string text into a structured Python dictionary
            data_packet = json.loads(raw_data)
            
            # ---------------------------------------------------------
            # DEVELOPER NOTE: This is exactly where our future 
            # Transformer model will intercept the live sliding window!
            # ---------------------------------------------------------
            
            # ---------------------------------------------------------
            # AI INFERENCE GRID: TRANSFORMER RECONSTRUCTION
            # ---------------------------------------------------------
            # Pass our dictionary telemetry into our sliding window pipeline
            sliding_window_tensor = pipeline.process_incoming_packet(data_packet)
            
            # Default fallback values while our 30-step history window is filling up
            recon_error = 0.0
            health_score = 100.0
            
            # The moment our sliding window buffer hits exactly 30 steps, start AI scoring
            if sliding_window_tensor is not None and transformer_brain is not None:
                # Perform an asynchronous-safe forward pass prediction through our model
                reconstructed_tensor = transformer_brain(sliding_window_tensor, training=False).numpy()
                
                # Calculate Mean Squared Error (MSE) between original window and rebuilt window
                # We focus specifically on the very last timestep in our sequence grid
                original_step = sliding_window_tensor[0, -1, :]
                reconstructed_step = reconstructed_tensor[0, -1, :]
                
                recon_error = float(np.mean((original_step - reconstructed_step) ** 2))
                
                # Map our reconstruction loss dynamically to a readable 0-100 UI Health Score
                # Normal healthy fluctuations sit below 0.001. Anything spiking toward 0.1 indicates a disaster.
                # Using a soft logarithmic mapping gives us clean, steady tracking
                health_score = max(0.0, min(100.0, 100.0 - (recon_error * 1000.0)))
            
            # Inject our real, live math scores right back into the streaming telemetry bundle
            data_packet["reconstruction_error"] = recon_error
            data_packet["ai_health_score"] = int(health_score)
            
            # Broadcast this telemetry packet instantly to all open React dashboards
            if active_clients:
                # Convert the modified packet back into a string string for transit
                broadcast_message = json.dumps(data_packet)
                
                # Gather all dashboard broadcast tasks and execute them concurrently
                await asyncio.gather(
                    *[client.send_text(broadcast_message) for client in active_clients]
                )
                
    except WebSocketDisconnect:
        print("[SERVER] Warning: Lunar Simulator disconnected unexpectedly.")
    finally:
        # Clean up our connection pool if the wire drops
        active_simulators.remove(websocket)


# =====================================================================
# 4. CLIENT DASHBOARD BROADCAST & TRIGGER ENDPOINT
# =====================================================================
# This endpoint opens a persistent pipe for our React frontend instances.
@app.websocket("/ws/client")
async def websocket_client_endpoint(websocket: WebSocket):
    # Accept the network handshake from the React UI dashboard
    await websocket.accept()
    active_clients.add(websocket)
    print(f"[SERVER] Client dashboard instance connected. Total clients: {len(active_clients)}")
    
    try:
        while True:
            # Listen for inbound messages from the React UI (like button clicks)
            raw_client_message = await websocket.receive_text()
            client_command = json.loads(raw_client_message)
            
            print(f"[SERVER] Operational Command Received from UI: {client_command}")
            
            # Forward this fault injection command down to our active simulator
            if active_simulators:
                forward_payload = json.dumps(client_command)
                await asyncio.gather(
                    *[sim.send_text(forward_payload) for sim in active_simulators]
                )
            else:
                print("[SERVER] Warning: Command dropped. No active simulator connected.")
                
    except WebSocketDisconnect:
        active_clients.remove(websocket)
        print(f"[SERVER] Client dashboard instance disconnected. Remaining clients: {len(active_clients)}")