from fastapi import FastAPI, WebSocket, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from schemas.responses import ErrorResponse
from routers import auth, exam  # Add exam router import
import cv2
import numpy as np
from datetime import datetime
import json
from detection.face_detection import detect_face
from detection.hand_detection import detect_hands
from detection.face_mesh_detection import detect_face_mesh
from detection.yolo_detection import detect_yolo
from config.database import init_db, get_db
from models.logs import Log
from sqlalchemy.orm import Session

app = FastAPI()

# Initialize database and YOLO model on startup
@app.on_event("startup")
async def startup_event():
    # Initialize database
    init_db()
    # Initialize YOLO model
    from detection.yolo_detection import load_model
    load_model()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(exam.router, prefix="/api/v1/exam", tags=["exam"])  # Add exam router

# Add exception handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Add root endpoint
@app.get("/")
async def root():
    return {"message": "Proctoring AI API", "version": "1.0"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    print(f"WebSocket connection accepted for user {user_id}")

    try:
        while True:
            data = await websocket.receive_bytes()
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            logs = []

            # Face Detection
            face_logs = detect_face(frame)
            logs.extend(face_logs)

            # Hand Detection
            hand_logs = detect_hands(frame)
            logs.extend(hand_logs)

            # Face Mesh for Eye and Mouth Tracking
            face_mesh_logs = detect_face_mesh(frame)
            logs.extend(face_mesh_logs)

            # Phone and Person Detection (YOLOv5)
            yolo_logs = detect_yolo(frame)
            logs.extend(yolo_logs)

            # Store logs in database
            for log_entry in logs:
                db_log = Log(
                    log=log_entry["event"],
                    event_type=log_entry["event"].lower().replace(" ", "_"),
                    timestamp=datetime.strptime(log_entry["time"], "%Y-%m-%d %H:%M:%S.%f"),
                    user_id=user_id
                )
                db.add(db_log)
            
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error storing logs: {e}")

            # Send logs back to frontend
            if logs:
                await websocket.send_text(json.dumps({"logs": logs}))
                
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
