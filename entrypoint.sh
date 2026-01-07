#!/bin/bash

# 1. Start MLflow UI in the background
echo "Starting MLflow UI on port 5001..."
mlflow ui --host 0.0.0.0 --port 5001 &

# 2. Check if we need to train the model
# Train if "brain_tumor_model.h5" is missing OR if FORCE_TRAIN is set to "true"
if [ ! -f "brain_tumor_model.h5" ] || [ "$FORCE_TRAIN" = "true" ]; then
    echo "Model not found or FORCE_TRAIN=true. Starting training..."
    python train_model.py
else
    echo "Model found. Skipping training."
fi

# 3. Start Flask App
echo "Starting Flask App on port 5000..."
python app.py
