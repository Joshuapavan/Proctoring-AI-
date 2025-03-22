import cv2
import mediapipe as mp
from datetime import datetime
from utils.logger import logger

mp_hands = mp.solutions.hands

def detect_hands(frame):
    logs = []
    timestamp = str(datetime.now())
    
    try:
        hands_detection = mp_hands.Hands(
            static_image_mode=True,  # Force CPU mode
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = hands_detection.process(frame_rgb)
        
        if hand_results.multi_hand_landmarks:
            logs.append({"time": timestamp, "event": "Hand detected"})
            logger.info("Hand detected")
            
    except Exception as e:
        logger.error(f"Hand detection error: {str(e)}", exc_info=True)
        return []
    finally:
        if 'hands_detection' in locals():
            hands_detection.close()
            
    return logs
