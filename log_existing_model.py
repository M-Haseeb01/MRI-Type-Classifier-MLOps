import mlflow
import mlflow.keras
from tensorflow import keras
import os
import json

# Configuration
MODEL_PATH = 'brain_tumor_model.h5'
CLASS_INDICES_PATH = 'class_indices.json'
HISTORY_PLOT_PATH = 'training_history.png'

def log_existing_model():
    print("Loading existing model...")
    if not os.path.exists(MODEL_PATH):
        print(f"Error: {MODEL_PATH} not found. Please train the model first.")
        return

    model = keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")

    # Set experiment
    mlflow.set_experiment("Brain Tumor Classification")

    print("Starting MLflow run...")
    with mlflow.start_run(run_name="Existing Model Import"):
        # Log the model
        print("Logging model to MLflow...")
        mlflow.keras.log_model(model, "model")
        
        # Log artifacts if they exist
        if os.path.exists(CLASS_INDICES_PATH):
            print(f"Logging {CLASS_INDICES_PATH}...")
            mlflow.log_artifact(CLASS_INDICES_PATH)
            
            # Try to log num_classes from indices
            with open(CLASS_INDICES_PATH, 'r') as f:
                indices = json.load(f)
                mlflow.log_param("num_classes", len(indices))
        
        if os.path.exists(HISTORY_PLOT_PATH):
            print(f"Logging {HISTORY_PLOT_PATH}...")
            mlflow.log_artifact(HISTORY_PLOT_PATH)

        print("\n" + "="*50)
        print("Success! Existing model logged to MLflow.")
        print("Run 'mlflow ui -p 5001' to view it.")
        print("="*50)

if __name__ == "__main__":
    log_existing_model()
