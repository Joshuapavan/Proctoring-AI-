from pydantic import BaseModel
from typing import Dict

class ExamSummary(BaseModel):
    total_duration: float  # in minutes
    face_detection_rate: float  # percentage of time face was detected
    suspicious_activities: Dict[str, int]  # count of each type of suspicious activity
    overall_compliance: float  # overall compliance percentage
