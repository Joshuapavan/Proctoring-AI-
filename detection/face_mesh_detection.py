import cv2
import mediapipe as mp
from datetime import datetime

mp_face_mesh = mp.solutions.face_mesh

# Define landmark indices
LEFT_EYE_INDICES = [33]  # Simplified to single point for example
RIGHT_EYE_INDICES = [263]  # Simplified to single point for example
MOUTH_INDICES = [0]  # Simplified to single point for example

def detect_face_mesh(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, refine_landmarks=True)  # Use GPU if available
    face_mesh_results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    print(f"Face mesh results: {face_mesh_results}")
    
    if face_mesh_results.multi_face_landmarks:
        for face_landmarks in face_mesh_results.multi_face_landmarks:
            try:
                # Get specific landmarks
                left_eye = face_landmarks.landmark[LEFT_EYE_INDICES[0]]
                right_eye = face_landmarks.landmark[RIGHT_EYE_INDICES[0]]
                mouth = face_landmarks.landmark[MOUTH_INDICES[0]]
                
                print(f"Left eye: {left_eye}, Right eye: {right_eye}, Mouth: {mouth}")
                
                if left_eye.y < 0.3 or right_eye.y < 0.3:
                    logs.append({"time": timestamp, "event": "Eye movement detected"})
                if mouth.y > 0.7:
                    logs.append({"time": timestamp, "event": "Mouth movement detected"})
            except IndexError as e:
                print(f"Error accessing landmarks: {e}")
                continue
    
    return logs
