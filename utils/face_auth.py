import face_recognition
import numpy as np
import io
from PIL import Image
import cv2

def compare_faces(known_image, unknown_image, tolerance=0.6):
    """
    Compare known and unknown face images
    Args:
        known_image: Stored user image (bytes)
        unknown_image: Live captured image (bytes)
        tolerance: Face recognition tolerance (lower is more strict)
    """
    try:
        # Convert stored image to face encoding
        known_image_np = face_recognition.load_image_file(io.BytesIO(known_image))
        known_encodings = face_recognition.face_encodings(known_image_np)
        
        if not known_encodings:
            return False, "No face found in stored image"
        
        # Convert live captured image to face encoding
        unknown_image_np = face_recognition.load_image_file(io.BytesIO(unknown_image))
        unknown_encodings = face_recognition.face_encodings(unknown_image_np)
        
        if not unknown_encodings:
            return False, "No face found in captured image"
            
        # Compare faces with tolerance
        results = face_recognition.compare_faces(
            [known_encodings[0]], 
            unknown_encodings[0],
            tolerance=tolerance
        )
        
        # Calculate face distance for confidence measure
        face_distance = face_recognition.face_distance([known_encodings[0]], unknown_encodings[0])
        confidence = 1 - float(face_distance)
        
        return results[0], {
            "match": results[0],
            "confidence": round(confidence * 100, 2),
            "tolerance": tolerance
        }
        
    except Exception as e:
        return False, f"Face comparison error: {str(e)}"
