from fastapi import (
    FastAPI, WebSocket, HTTPException, Request, 
    Depends, WebSocketDisconnect, status, Security
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
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
from models.users import User
from routers.auth import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session
import asyncio
from starlette.websockets import WebSocketState
import base64
from typing import Dict
from utils.connection import manager  # Import manager from new module
from utils.logger import logger
from services.detection_service import DetectionService
from services.log_service import LogService
from utils.image_utils import decode_image_data
from utils.mediapipe_config import configure_mediapipe

# Security schemes
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/password")

# Add auth helper functions
async def get_current_user_ws(token: str, db: Session) -> User:
    credentials_exception = WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

class WebSocketException(Exception):
    def __init__(self, code: int):
        self.code = code

app = FastAPI()

# Initialize database and models on startup
@app.on_event("startup")
async def startup_event():
    # Configure MediaPipe
    configure_mediapipe()
    
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
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    logger.info(f"WebSocket connection attempt for user {user_id}")
    connection_established = False
    
    try:
        # Token validation
        token = websocket.query_params.get('token')
        if not token:
            logger.warning(f"No token provided for user {user_id}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # User validation
        try:
            current_user = await get_current_user_ws(token, db)
            if current_user.id != user_id:
                logger.warning(f"Token user ID mismatch for user {user_id}")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except WebSocketException as e:
            logger.error(f"Token validation failed for user {user_id}: {str(e)}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connect
        if not await manager.connect(websocket, user_id):
            logger.error(f"Failed to establish WebSocket connection for user {user_id}")
            return
            
        connection_established = True
        logger.info(f"WebSocket connection established for user {user_id}")

        # Main processing loop
        try:
            while True:
                try:
                    # Check connection state
                    if websocket.application_state != WebSocketState.CONNECTED:
                        logger.info(f"WebSocket disconnected for user {user_id}")
                        break

                    # Receive data
                    data = await websocket.receive()
                    
                    if data["type"] == "websocket.disconnect":
                        logger.info(f"Client initiated disconnect for user {user_id}")
                        break

                    raw_data = data.get("text") or data.get("bytes")
                    if not raw_data:
                        continue

                    # Process frame
                    frame = decode_image_data(raw_data)
                    if frame is None:
                        continue

                    # Process detections
                    logs = await DetectionService.process_frame(frame)
                    if logs:
                        stored_logs = await LogService.store_logs(db, user_id, logs)
                        if stored_logs and websocket.application_state == WebSocketState.CONNECTED:
                            await websocket.send_text(json.dumps({
                                "type": "logs",
                                "data": [{"event": log.log, "time": str(log.timestamp)} for log in stored_logs],
                                "stored": True
                            }))

                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Frame processing error: {str(e)}")
                    if "close message" in str(e) or "disconnected" in str(e).lower():
                        break
                    continue

        finally:
            await manager.disconnect(user_id)
            db.close()

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        
    finally:
        if connection_established:
            logger.info(f"Cleaning up connection for user {user_id}")
            await manager.disconnect(user_id)
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
