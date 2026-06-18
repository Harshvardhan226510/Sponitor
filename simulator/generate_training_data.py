import csv
import os
from simulator import generate_telemetry_packet

def build_nominal_dataset(total_rows=10000):
    """Runs the simulation engine in a rapid nominal loop to compile training records."""
    # Build target file path pointing to the backend folder so our model can find it easily
    target_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
    os.makedirs(target_dir, exist_ok=True)
    csv_file_path = os.path.join(target_dir, "healthy_telemetry.csv")
    
    print("==============================================")
    print("      SPONITOR: TRAINING DATA GENERATOR       ")
    print(f"  Compiling {total_rows} nominal timesteps...")
    print("==============================================")
    
    headers = ["oxygen", "pressure", "temperature", "vibration", "solar_intensity"]
    
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        for step in range(total_rows):
            # Generate pure nominal telemetry (no fault variables are altered)
            packet = generate_telemetry_packet(step)
            
            # Prune out the timestamp for data training uniformity
            row = {
                "oxygen": packet["oxygen"],
                "pressure": packet["pressure"],
                "temperature": packet["temperature"],
                "vibration": packet["vibration"],
                "solar_intensity": packet["solar_intensity"]
            }
            writer.writerow(row)
            
            if step % 2000 == 0 and step > 0:
                print(f"[PROGRESS] Written {step} operational timesteps safely...")
                
    print(f"\n[SUCCESS] Dataset created perfectly at: {csv_file_path}")

if __name__ == "__main__":
    build_nominal_dataset()