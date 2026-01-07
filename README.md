#  Brain Tumor Classification AI

A state-of-the-art deep learning application for detecting and classifying brain tumors from MRI scans. Built with TensorFlow, Flask, and Docker.

![Project Theme](https://via.placeholder.com/800x200/0f0f23/2563eb?text=Brain+Scan+AI)

##  Features

- **Advanced AI Model**: Uses MobileNetV2 transfer learning to classify tumors into 4 categories:
  - Glioma
  - Meningioma
  - Pituitary Tumor
  - No Tumor
- **Modern UI**: Sleek Blue/Black dark theme with light mode toggle.
- **Smart Preprocessing**: Automatically enhances contrast and converts internet images to match medical MRI standards.
- **Prediction History**: Tracks all your past predictions with confidence scores and timestamps (stored in SQLite).
- **MLflow Integration**: Tracks experiments, metrics, and model versions automatically.
- **Dockerized**: Run the entire stack (App + MLflow + Training) with a single command.

---

##  Quick Start (Docker)

The easiest way to run the application.

### 1. Build the Image
```bash
docker build -t brain-tumor-app .
```

### 2. Run the Container
This starts both the Web App (Port 5000) and MLflow (Port 5001).
```bash
docker run -p 5000:5000 -p 5001:5001 brain-tumor-app
```

- **Web App**: [http://localhost:5000](http://localhost:5000)
- **MLflow UI**: [http://localhost:5001](http://localhost:5001)

> **Note**: If the model is missing, the container will automatically train a new one on startup!

---

##  Local Installation

If you prefer running it without Docker.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
or run env .\venv\Scripts\activate
```

### 2. Train the Model (Optional)
If you don't have `brain_tumor_model.h5` yet:
```bash
python train_model.py
```
*This will also log the run to MLflow.*

### 3. Run the App
```bash
python app.py
```
Visit [http://localhost:5000](http://localhost:5000)

---

##  MLflow Experiment Tracking

We use MLflow to track model performance.

To view your training history locally:
```bash
mlflow ui -p 5001
```

To log an existing model without retraining:
```bash
python log_existing_model.py
```

---

##  Project Structure

- `app.py`: Main Flask application.
- `train_model.py`: Training script with MLflow logging and MobileNetV2 architecture.
- `Dockerfile`: Container configuration.
- `entrypoint.sh`: Startup script for Docker.
- `templates/`: HTML files (Home, Predict, About, History).
- `static/`: CSS and JavaScript files.
- `predictions.db`: SQLite database for history.

---

##  Disclaimer
This tool is for educational purposes only. Always consult medical professionals for diagnosis.
