from typing import List, Dict
from datetime import datetime
from utils.logger import logger
import cv2
from detection.face_detection import detect_face
from detection.hand_detection import detect_hands
from detection.face_mesh_detection import detect_face_mesh
from detection.yolo_detection import detect_yolo

class DetectionService:
    @staticmethod
    async def process_frame(frame) -> List[Dict]:
        logger.info("Processing new frame")
        all_logs = []
        
        try:
            # Process each detection type
            detections = [
                ("Face", detect_face(frame)),
                ("Hand", detect_hands(frame)), 
                ("Face Mesh", detect_face_mesh(frame)),
                ("YOLO", detect_yolo(frame))
            ]

            # Collect logs from all detections
            for detector_name, logs in detections:
                if logs:
                    logger.info(f"{detector_name} detection found {len(logs)} events")
                    all_logs.extend(logs)
                else:
                    logger.debug(f"No {detector_name} detections")

            if all_logs:
                logger.info(f"Total events detected: {len(all_logs)}")
            
        except Exception as e:
            logger.error(f"Error in frame processing: {str(e)}", exc_info=True)
        
        return all_logs
