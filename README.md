# SPONITOR: Lunar Capsule Digital Twin Matrix Dashboard

SPONITOR is an enterprise-grade, real-time digital twin telemetry simulation dashboard for a lunar capsule. The system models structural and atmospheric physics frames and uses a trained ensemble architecture of Deep Learning Transformer networks to track anomalies, evaluate capsule structural integrity, and flag system degradation dynamically based on neural reconstruction loss.

---

## 🛠️ Technical Architecture & Stack

The platform is engineered as a decoupled, multi-layer reactive ecosystem:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND UI LAYER (React)                    │
│   • Vite / Tailwind CSS         • Recharts Telemetry Streams    │
│   • Lucide Instrumentation      • Cockpit Audio Siren Engine    │
└────────────────────────────────┬────────────────────────────────┘
                                 ▲
                     Bi-directional WebSockets
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BACKEND SIMULATION ENGINE (FastAPI)             │
│   • Async Event Loop            • 10Hz Continuous Physics Frame │
│   • WebSocket Ingestion Pipeline • Dynamic Fault Injector Hooks │
└────────────────────────────────┬────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ENSEMBLE AI CORE (TensorFlow)                   │
│   • Atmos Brain (Transformer)   • Ext Brain (Transformer)       │
│   • 30-Step Sliding Window      • Reconstruction Loss Anchors   │
└─────────────────────────────────────────────────────────────────┘
```
- **Frontend UI Layer:** Built with React and bundled via Vite. UI styling is driven by Tailwind CSS, real-time high-frequency telemetry tracking is handled by Recharts, and aerospace instrumentation symbology is rendered via Lucide React. An integrated web audio engine handles synchronized cockpit alarms.

- **Backend Simulation Engine:** Powered by FastAPI utilizing an asynchronous WebSocket data pipeline executing a continuous mathematical physics engine at a strict operational frame rate of 10Hz (100ms tick intervals).

- **Ensemble AI / Core Intelligence:** Built using TensorFlow/Keras. It runs two independent, trained deep neural network architectures—Atmos Brain and Ext Brain (Transformer models)—to calculate structural and atmospheric anomaly scores against baseline configuration vectors (.npz/.keras).

- **Infrastructure & Deployment:** Fully containerized via a production-grade Multi-Stage Dockerfile optimized for minimal layer caching and hosted in an isolated space sandbox.

## 📁 Repository Blueprint
```
├── backend/
│   ├── data/
│   │   └── healthy_telemetry.csv    # Target baseline telemetry reference datasets
│   ├── model/
│   │   ├── brain.py                 # Transformer network definition and matrix configurations
│   │   └── pipeline.py              # Anomaly analytics and feature engineering pipelines
│   ├── saved_model/
│   │   ├── atmos_brain.keras        # Atmospheric prediction neural network
│   │   ├── ext_brain.keras          # Structural integrity Transformer weights
│   │   ├── transformer_brain.keras  # Combined system classification model
│   │   └── ensemble_anchors.npz     # Matrix normalization weights & mathematical anchors
│   ├── main.py                      # Multi-stage training orchestration entrypoint
│   ├── server.py                    # FastAPI server gateway & asynchronous WebSocket loop
│   ├── train.py                     # Primary model training configurations
│   ├── train_ensemble.py            # Ensemble aggregation and evaluation routines
│   └── requirements.txt             # Backend Python package manifest
├── frontend/
│   ├── public/                      # Static assets, textures, and UI files
│   ├── src/                         # React component structure, hooks, and views
│   ├── eslint.config.js             # Codebase quality linting configurations
│   ├── index.html                   # Core web application container
│   ├── package.json                 # Node environment dependencies manifest
│   └── vite.config.js               # Vite compilation and bundler pipelines
├── simulator/
│   ├── simulator.py                 # Local standalone terminal physics engine daemon
│   └── generate_training_data.py    # Synthetic operational variance compilation script
└── Dockerfile                       # Multi-stage production container build schema
```

## 🚀 Core Simulation Features
```
📡 Real-Time Data Streaming
Bi-directional WebSockets push high-frequency time-series telemetry metrics to the UI layer at 10Hz. Monitored indicators include:

Oxygen Concentration & Cabin Pressure (Atmospheric Frame)

Core Temperature & Structural Vibration (Hz) (Physical Frame)

Solar Radiation Intensity (W/m²) (Environmental Frame)

🚨 Dynamic Anomaly Injectors
The interactive instrument console contains hardcoded hazard buttons enabling real-time fault injection. Users can dynamically trigger critical system failures, including O2 leaks, unexpected cabin pressure decompression, thermal vector spikes, and cosmic solar flux radiation waves.

🧠 Deep Learning AI Diagnostics
The trained Transformer networks evaluate streaming state vectors over a sliding 30-step historical window size. By computing real-time neural reconstruction loss deviations against pre-compiled baseline anchors, the ensemble core dynamically evaluates and updates a Master Cognitive Status Indicator and an Accumulated Structural Damage Tracker.

🔊 Cockpit Audio Synchronization
An automated web audio mapping interface synchronizes cockpit audio systems with neural telemetry alerts. Anomaly threshold crossings instantly switch background tracking systems into emergency mode, playing audible warning sirens and graph traversal warning blips directly mapped to system integrity values.
```
## ⚙️ Environment Configuration & Installation
```
Prerequisite Verifications
Ensure your workstation has the following system wrappers installed:
  Python 3.10 or higher
  Node.js v18 or higher (with npm)

🐍 Backend Service Setup
Navigate to the backend ecosystem directory:
  cd backend

Initialize your virtual platform layer and source it:
# Linux/macOS
  python3 -m venv env
  source env/bin/activate

# Windows
  python -m venv env
  env\Scripts\activate

Install the dependencies manifest:
  pip install -r requirements.txt

Launch the FastAPI WebSocket Gateway Server:
  python server.py

The backend service will boot up locally at http://127.0.0.1:8000.

⚛️ Frontend User Interface Setup
Navigate to the frontend dashboard directory:
  cd ../frontend

Install the Node module package tree:
  npm install

Compile and execute the Vite development server:
  npm run dev
```
