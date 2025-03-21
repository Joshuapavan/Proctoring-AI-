import cv2
import mediapipe as mp
import torch
from datetime import datetime  # Add this import

# Mediapipe setup
mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

# Load YOLO model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True).to(device)

def detect_face(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)  # Use GPU if available
    face_results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if not face_results.detections:
        logs.append({"time": timestamp, "event": "Face not detected"})
    else:
        for detection in face_results.detections:
            bbox = detection.location_data.relative_bounding_box
            if bbox.width > 0.5:  # Example condition for unusual face movement
                logs.append({"time": timestamp, "event": "Unusual face movement detected"})
    return logs

def detect_hands(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    hands_detection = mp_hands.Hands(min_detection_confidence=0.5)  # Use GPU if available
    hand_results = hands_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if hand_results.multi_hand_landmarks:
        logs.append({"time": timestamp, "event": "Hand detected"})
    return logs

def detect_face_mesh(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, refine_landmarks=True)  # Use GPU if available
    face_mesh_results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if face_mesh_results.multi_face_landmarks:
        for face_landmarks in face_mesh_results.multi_face_landmarks:
            # Example conditions for eye and mouth tracking
            left_eye = face_landmarks.landmark[mp_face_mesh.FACEMESH_LEFT_EYE]
            right_eye = face_landmarks.landmark[mp_face_mesh.FACEMESH_RIGHT_EYE]
            mouth = face_landmarks.landmark[mp_face_mesh.FACEMESH_LIPS]
            if left_eye.y < 0.3 or right_eye.y < 0.3:
                logs.append({"time": timestamp, "event": "Eye movement detected"})
            if mouth.y > 0.7:
                logs.append({"time": timestamp, "event": "Mouth movement detected"})
    return logs

def detect_yolo(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    results = model(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    for detection in results.xyxy[0]:
        label = results.names[int(detection[5])]
        if label == "cell phone":
            logs.append({"time": timestamp, "event": "Phone detected"})
        elif label == "person" and len(results.xyxy[0]) > 1:
            logs.append({"time": timestamp, "event": "Background person detected"})
    return logs
