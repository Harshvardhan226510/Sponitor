import numpy as np

class TelemetryPipeline:
    def __init__(self, window_size=30):
        self.window_size = window_size
        # Out 5 core channels: oxygen, pressure, temperature, vibration, solar_intensity
        self.num_features = 5
        self.buffer = []
        
        # Min-Max Scaling Bounds (Nominal expected operating ceilings)
        # Shifting values cleanly into a 0.0 to 1.0 range prevents neural layers from exploding
        self.scaler_mins = np.array([0.0, 0.0, -50.0, 0.0, 0.0])
        self.scaler_maxs = np.array([100.0, 200.0, 100.0, 5.0, 1000.0])

    def scale_vector(self, raw_vector):
        """Normalizes a raw list of metrics into a stable 0-1 scale."""
        return (raw_vector - self.scaler_mins) / (self.scaler_maxs - self.scaler_mins)

    def process_incoming_packet(self, packet):
        """Appends a new streaming packet into the sliding memory buffer."""
        # Extract metrics in absolute strict channel order
        raw_vector = np.array([
            packet["oxygen"],
            packet["pressure"],
            packet["temperature"],
            packet["vibration"],
            packet["solar_intensity"]
        ])
        
        # Scale the data point
        scaled_vector = self.scale_vector(raw_vector)
        
        # Append to our in-memory timeline tracking
        self.buffer.append(scaled_vector)
        
        # Maintain our sliding window horizon boundary
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0)
            
        # Return True only if the timeline matrix is completely filled and ready for AI
        if len(self.buffer) == self.window_size:
            # Reshape into standard Deep Learning dimensions: (1, window_size, 5)
            return np.expand_dims(np.array(self.buffer), axis=0)
        return None