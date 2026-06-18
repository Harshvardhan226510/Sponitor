import tensorflow as tf
from tensorflow.keras import layers, Model  # type: ignore

def build_specialized_transformer(window_size=30, num_features=3, name="Specialized_Brain"):
    """
    Constructs an isolated Transformer Autoencoder with an expanded internal 
    projection layer to eliminate oversaturation and false alarms.
    """
    # 1. INPUT LAYER
    inputs = layers.Input(shape=(window_size, num_features))
    
    # 2. FEATURE PROJECTION (Expands shallow input into a stable 32-dim deep attention channel)
    projected_inputs = layers.Dense(32)(inputs)
    
    # 3. POSITION EMBEDDING
    positions = tf.range(start=0, limit=window_size, delta=1)
    position_embedding = layers.Embedding(input_dim=window_size, output_dim=32)(positions)
    x = projected_inputs + position_embedding

    # 4. HIGH-CAPACITY TRANSFORMER ENCODER BLOCK
    attention_output = layers.MultiHeadAttention(
        num_heads=4, 
        key_dim=32
    )(x, x)
    x = layers.LayerNormalization(epsilon=1e-6)(x + attention_output)
    
    # Feed-Forward Network Layer
    ffn_output = layers.Dense(64, activation="relu")(x)
    ffn_output = layers.Dense(32)(ffn_output)
    x = layers.LayerNormalization(epsilon=1e-6)(x + ffn_output)
    
    # 5. LATENT BOTTLE-NECK RECONSTRUCTION
    flattened = layers.Flatten()(x)
    bottleneck = layers.Dense(64, activation="relu")(flattened)
    
    # Reconstruct back out to 30 timesteps x 32 projected dimensions
    decoder_output = layers.Dense(window_size * 32, activation="linear")(bottleneck)
    reshaped_decoder = layers.Reshape((window_size, 32))(decoder_output)
    
    # 6. OUTPUT PROJECTION (Compresses 32 internal channels cleanly back to your raw feature count)
    outputs = layers.Dense(num_features, activation="linear")(reshaped_decoder)
    
    # Compile Structural Model Configuration
    model = Model(inputs=inputs, outputs=outputs, name=name)
    model.compile(optimizer="adam", loss="mse")
    
    return model