import cv2
import mediapipe as mp
from datetime import datetime
from utils.logger import logger

mp_face_detection = mp.solutions.face_detection

def detect_face(frame):
    logger.info("Starting face detection")
    logs = []
    timestamp = str(datetime.now())
    
    try:
        # Initialize face detection with CPU
        face_detection = mp_face_detection.FaceDetection(
            min_detection_confidence=0.5,
            model_selection=0  # Use short-range model
        )
        
        # Process frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = face_detection.process(frame_rgb)
        
        if not face_results.detections:
            event = "Face not detected"
            logger.info(event)
            logs.append({"time": timestamp, "event": event})
        else:
            for detection in face_results.detections:
                bbox = detection.location_data.relative_bounding_box
                event = "Unusual face movement detected" if bbox.width > 0.5 else "Face detected"
                logger.info(f"{event} with confidence {detection.score[0]:.2f}")
                logs.append({"time": timestamp, "event": event})

    except Exception as e:
        logger.error(f"Face detection error: {str(e)}", exc_info=True)
        # Return empty logs on error to continue processing
        return []
    finally:
        # Cleanup
        if 'face_detection' in locals():
            face_detection.close()
    
    return logs
