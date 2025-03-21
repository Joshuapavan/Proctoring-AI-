import cv2
import mediapipe as mp
from datetime import datetime

mp_face_detection = mp.solutions.face_detection

def detect_face(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)  # Use GPU if available
    face_results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    print(f"Face results: {face_results}")
    if not face_results.detections:
        logs.append({"time": timestamp, "event": "Face not detected"})
    else:
        for detection in face_results.detections:
            bbox = detection.location_data.relative_bounding_box
            print(f"Detection: {detection}, Bounding Box: {bbox}")
            if bbox.width > 0.5:  # Example condition for unusual face movement
                logs.append({"time": timestamp, "event": "Unusual face movement detected"})
            else:
                logs.append({"time": timestamp, "event": "Face detected"})
    return logs
