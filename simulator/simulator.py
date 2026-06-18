import time
import random
import math
import websockets

# =====================================================================
# 1. CORE ENVIRONMENTAL BASELINES (NOMINAL STATE)
# =====================================================================
BASE_O2 = 21.0          # Target percentage of Oxygen in the cabin air
BASE_PRESSURE = 101.3    # Target atmospheric pressure in kPa (Sea Level)
BASE_TEMP = 22.0        # Target internal temperature in Celsius
BASE_VIBRATION = 0.02   # Baseline structural background vibration in mm/s
BASE_SOLAR = 135.0      # Average solar ray intensity baseline in mW/cm²

# =====================================================================
# 2. TACTICAL FAULT STATES (Supports multi-directional anomalies)
# =====================================================================
# Modes available: "nominal", "high", "low"
fault_pressure = "nominal"
fault_temp = "nominal"
fault_o2 = "nominal"

# Momentary/Single-direction events
fault_structural_impact = False  # True when meteoroid hits
fault_solar_burst = False        # True during a solar flare

# =====================================================================
# 3. DYNAMIC DRIFT MODIFIERS (Track how much damage has accumulated)
# =====================================================================
drift_time_counter = 0  # Tracks how long a fault has been active
structural_ring_decay = 0.0  # Controls the shaking fade-out after an impact

# =====================================================================
# 4. ENVIRONMENTAL MATH & MULTI-DIRECTIONAL FAULT INJECTION
# =====================================================================
def generate_telemetry_packet(step):
    global drift_time_counter, structural_ring_decay
    global fault_pressure, fault_temp, fault_o2, fault_structural_impact, fault_solar_burst

    # Check if ANY continuous drift fault is active
    if fault_pressure != "nominal" or fault_temp != "nominal" or fault_o2 != "nominal" or fault_solar_burst:
        drift_time_counter += 1
    else:
        drift_time_counter = 0  # Reset if systems are completely nominal

    # -----------------------------------------------------------------
    # CHANNEL 1: OXYGEN (O2) MIX
    # -----------------------------------------------------------------
    if fault_o2 == "low":
        # Slow linear degradation: drops by 0.05% per step
        o2_drift = drift_time_counter * 0.05
        current_o2 = max(0.0, BASE_O2 - o2_drift)
    elif fault_o2 == "high":
        # Oxygen enrichment fault (Massive fire hazard)
        o2_drift = drift_time_counter * 0.04
        current_o2 = min(100.0, BASE_O2 + o2_drift)
    else:
        current_o2 = BASE_O2
    # Add minor sensor jitter (+/- 0.02%)
    current_o2 += random.uniform(-0.02, 0.02)

    # -----------------------------------------------------------------
    # CHANNEL 2: INTERNAL PRESSURE
    # -----------------------------------------------------------------
    if fault_pressure == "low":
        # Exponential leak decay: drops progressively faster over time
        pressure_drift = 0.1 * (drift_time_counter ** 1.1)
        current_pressure = max(0.0, BASE_PRESSURE - pressure_drift)
    elif fault_pressure == "high":
        # Over-pressurization build up (Tank/Hull strain)
        pressure_drift = 0.08 * (drift_time_counter ** 1.05)
        current_pressure = BASE_PRESSURE + pressure_drift
    else:
        current_pressure = BASE_PRESSURE
    # Add minor atmospheric jitter (+/- 0.05 kPa)
    current_pressure += random.uniform(-0.05, 0.05)

    # -----------------------------------------------------------------
    # CHANNEL 3: LIFE SUPPORT TEMPERATURE
    # -----------------------------------------------------------------
    if fault_temp == "high":
        # Steady runaway thermal climb: adds 0.15 degrees per step
        temp_drift = drift_time_counter * 0.15
        current_temp = BASE_TEMP + temp_drift
    elif fault_temp == "low":
        # Environmental deep-freeze drop: drops by 0.12 degrees per step
        temp_drift = drift_time_counter * 0.12
        current_temp = BASE_TEMP - temp_drift
    else:
        current_temp = BASE_TEMP
    # Add HVAC system flutter (+/- 0.1°C)
    current_temp += random.uniform(-0.1, 0.1)

    # -----------------------------------------------------------------
    # CHANNEL 4: STRUCTURAL INTEGRITY VIBRATION
    # -----------------------------------------------------------------
    current_vibration = BASE_VIBRATION
    
    # Cascade physics: BOTH a pressure leak or extreme pressure build-up strains the pipes
    if fault_pressure != "nominal":
        current_vibration += (drift_time_counter * 0.002)

    # Core Impact Event Logic
    if fault_structural_impact:
        # If the impact just happened, set peak kinetic energy shock wave
        if structural_ring_decay == 0.0:
            structural_ring_decay = 2.5  # Heavy structural shudder (mm/s)
        
        current_vibration += structural_ring_decay
        # Physics exponential decay: the ringing fades out by 15% every 500ms
        structural_ring_decay *= 0.85
        
        # Once the shaking drops near baseline, turn off the momentary event
        if structural_ring_decay < 0.001:
            structural_ring_decay = 0.0
            fault_structural_impact = False
            
    # Add structural engine floor vibration noise (+/- 0.003 mm/s)
    current_vibration += random.uniform(-0.003, 0.003)
    current_vibration = max(0.0, current_vibration)

    # -----------------------------------------------------------------
    # CHANNEL 5: SOLAR RAY INTENSITY
    # -----------------------------------------------------------------
    # Normal orbital physics: smooth sine wave cycles over time
    orbital_cycle = math.sin(step * 0.05) * 25.0
    
    if fault_solar_burst:
        # High-frequency radiative explosion breaking standard orbit parameters
        solar_anomaly_noise = random.uniform(400.0, 750.0)
        current_solar = BASE_SOLAR + orbital_cycle + solar_anomaly_noise
    else:
        current_solar = BASE_SOLAR + orbital_cycle
        # Add basic cosmic background radiation noise (+/- 0.5 mW/cm²)
        current_solar += random.uniform(-0.5, 0.5)
        
    current_solar = max(0.0, current_solar)

    # Return data package rounded to clean decimals for network efficiency
    return {
        "timestamp": time.time(),
        "oxygen": round(current_o2, 2),
        "pressure": round(current_pressure, 2),
        "temperature": round(current_temp, 2),
        "vibration": round(current_vibration, 4),
        "solar_intensity": round(current_solar, 2)
    }


# =====================================================================
# 5. ASYNCHRONOUS NETWORK COMMUNICATOR & COMMAND LISTENER
# =====================================================================
async def receive_commands(websocket):
    """Listens concurrently for incoming fault triggers from the React UI."""
    global fault_pressure, fault_temp, fault_o2, fault_structural_impact, fault_solar_burst
    
    try:
        async for message in websocket:
            command = json.loads(message)
            print(f"\n[NETWORK ALERT] Intercepted Mission Control Command: {command}")
            
            # Extract tactical injection directives
            action = command.get("action")
            system = command.get("system")
            state = command.get("state")
            
            if action == "inject_fault":
                if system == "pressure":
                    fault_pressure = state
                elif system == "temp":
                    fault_temp = state
                elif system == "o2":
                    fault_o2 = state
                elif system == "structural" and state == "high":
                    fault_structural_impact = True
                elif system == "solar" and state == "high":
                    fault_solar_burst = True
                    
                print(f"[ENGINE STATUS] Physics model shifted. P:{fault_pressure} | T:{fault_temp} | O2:{fault_o2} | Impact:{fault_structural_impact} | Solar Flare:{fault_solar_burst}")
                
    except websockets.exceptions.ConnectionClosed:
        pass

async def stream_telemetry():
    """Maintains a persistent websocket pipe and streams live lunar telemetry."""
    uri = "ws://127.0.0.1:8000/ws/simulator"
    
    print("==============================================")
    print("  SPONITOR: LUNAR DIGITAL TWIN SENSOR SYSTEM  ")
    print("  Connecting to Central FastAPI Relay Station...")
    print("==============================================")
    
    # Establish a persistent live network connection to the server
    async with websockets.connect(uri) as websocket:
        print("[SUCCESS] Connected to server pipeline. Initializing telemetry broadcast...")
        
        # Spawn the command intercept listener concurrently in the background
        listener_task = asyncio.create_task(receive_commands(websocket))
        
        step_counter = 0
        try:
            while True:
                # Generate our math packet
                packet = generate_telemetry_packet(step_counter)
                
                # Convert packet dictionary to clear JSON string data
                payload = json.dumps(packet)
                
                # Fire the data package down the network pipe instantly
                await websocket.send(payload)
                
                # Keep a localized terminal log for verification
                print(f"Streaming Packet {step_counter:04d} | O2: {packet['oxygen']}% | Pres: {packet['pressure']} kPa", end="\r")
                
                step_counter += 1
                await asyncio.sleep(0.5)  # Yield timeline control cleanly for 500ms
                
        except KeyboardInterrupt:
            print("\n[HALT] Halting telemetry broadcast safely...")
        finally:
            # Clean up our listener task when exiting
            listener_task.cancel()

if __name__ == "__main__":
    import asyncio
    import json
    # Run our network streaming framework inside an active async event loop
    asyncio.run(stream_telemetry())