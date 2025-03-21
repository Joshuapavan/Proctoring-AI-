import cv2
import mediapipe as mp
from datetime import datetime

mp_hands = mp.solutions.hands

def detect_hands(frame):
    logs = []
    timestamp = str(datetime.now())  # Use system's timestamp
    hands_detection = mp_hands.Hands(min_detection_confidence=0.5)  # Use GPU if available
    hand_results = hands_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    print(f"Hand results: {hand_results}")
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            print(f"Hand landmarks: {hand_landmarks}")
        logs.append({"time": timestamp, "event": "Hand detected"})
    return logs
