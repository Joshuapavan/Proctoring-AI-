from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from models.logs import Log
from schemas.exam import ExamSummary
from datetime import datetime, timedelta
from sqlalchemy import func
from typing import Dict

router = APIRouter()

@router.get("/summary/{user_id}", response_model=ExamSummary)
async def get_exam_summary(user_id: int, db: Session = Depends(get_db)):
    """
    Get exam summary for a user
    """
    # Get all logs for the user
    logs = db.query(Log).filter(Log.user_id == user_id).all()
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No exam logs found for this user"
        )
    
    # Calculate duration
    start_time = min(log.timestamp for log in logs)
    end_time = max(log.timestamp for log in logs)
    duration = (end_time - start_time).total_seconds() / 60  # in minutes
    
    # Count suspicious activities
    suspicious_activities: Dict[str, int] = {}
    total_checks = len(logs)
    face_detections = 0
    
    for log in logs:
        if log.event_type == "face_detected":
            face_detections += 1
        elif log.event_type in suspicious_activities:
            suspicious_activities[log.event_type] += 1
        else:
            suspicious_activities[log.event_type] = 1
    
    # Calculate compliance
    face_detection_rate = (face_detections / total_checks) * 100 if total_checks > 0 else 0
    
    # Calculate overall compliance
    # More weight to face detection, less to suspicious activities
    suspicious_weight = sum(suspicious_activities.values())
    overall_compliance = max(0, face_detection_rate - (suspicious_weight / total_checks * 20))
    
    return ExamSummary(
        total_duration=round(duration, 2),
        face_detection_rate=round(face_detection_rate, 2),
        suspicious_activities=suspicious_activities,
        overall_compliance=round(overall_compliance, 2)
    )
