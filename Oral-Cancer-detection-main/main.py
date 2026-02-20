from tensorflow.keras.models import load_model
import numpy as np

# Load your model
model = load_model("oral_cancer_model.h5")

# Example: if your model expects 224x224 RGB images
# Create a dummy input (batch of 1 image)
dummy_input = np.random.rand(1, 224, 224, 3)

# Get prediction
y_pred = model.predict(dummy_input)
print("Prediction:", y_pred)
model.summary()