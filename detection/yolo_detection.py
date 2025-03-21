import cv2
import torch
import os
from datetime import datetime

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(os.path.dirname(current_dir), "yolov5s.pt")

# Initialize model variable
model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    global model
    try:
        if not os.path.exists(model_path):
            # Download model if it doesn't exist
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            torch.save(model.state_dict(), model_path)
        else:
            # Load local model
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            model.load_state_dict(torch.load(model_path))
        
        model.to(device)
        model.eval()
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return None

def detect_yolo(frame):
    global model
    logs = []
    timestamp = str(datetime.now())

    try:
        if model is None:
            model = load_model()
            if model is None:
                return [{"time": timestamp, "event": "YOLO model not available"}]

        results = model(frame)
        for detection in results.xyxy[0]:
            if len(detection) >= 6:
                label = results.names[int(detection[5])]
                if label == "cell phone":
                    logs.append({"time": timestamp, "event": "Phone detected"})
                elif label == "person" and len(results.xyxy[0]) > 1:
                    logs.append({"time": timestamp, "event": "Background person detected"})
    except Exception as e:
        print(f"YOLO detection error: {e}")
        logs.append({"time": timestamp, "event": "YOLO detection failed"})

    return logs
