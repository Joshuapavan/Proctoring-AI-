import cv2
import torch
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to yolov5s.pt
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yolov5s.pt")
logger.info(f"Using YOLO model at: {model_path}")

# Initialize model variable
model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    global model
    try:
        if os.path.exists(model_path):
            logger.info("Loading local YOLO model...")
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
        else:
            logger.info("Local model not found, loading from hub...")
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        
        model.to(device)
        model.eval()
        logger.info("YOLO model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading YOLO model: {e}")
        return None

def detect_yolo(frame):
    global model
    logs = []
    timestamp = str(datetime.now())

    try:
        # Ensure model is loaded
        if model is None:
            logger.info("Model not loaded, attempting to load...")
            model = load_model()
        
        if model is None:
            return [{"time": timestamp, "event": "YOLO model initialization failed"}]

        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(frame_rgb)
        
        # Process detections
        for detection in results.xyxy[0]:
            if len(detection) >= 6:
                label = results.names[int(detection[5])]
                confidence = float(detection[4])
                
                if label == "cell phone" and confidence > 0.3:
                    logs.append({"time": timestamp, "event": "Phone detected"})
                elif label == "person" and len(results.xyxy[0]) > 1:
                    logs.append({"time": timestamp, "event": "Background person detected"})
                    
    except Exception as e:
        logger.error(f"YOLO detection error: {e}")
        logs.append({"time": timestamp, "event": "YOLO detection error occurred"})

    return logs
