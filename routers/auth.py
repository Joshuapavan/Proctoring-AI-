from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from config.database import get_db
from models.users import User
from utils.face_auth import compare_faces
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import io
from pydantic import BaseModel, EmailStr
import imghdr
import face_recognition
from schemas.auth import UserResponse, Token

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "018f3fefcbec0e190492e48855d8e301699953689567d1323704a3fdf77382a530383845fb07dce529a5a7e44ba0194620455c7a3dcc3f52a9ce88dd1b355dbf9ad764d110131961b9419ac2fe9b2c3e2029d20fdc4f2b62a39b38132f8fa1bd2787b225ea5f20fc939bd763f9384bd79d00efffd3a41b3be936742c35d99c3fe40bdd998a46b5225948818b1b2eae891d46f8d9ca1d02afec657f9b5b68f7bbcb5ce24e5b50328abf66db0cccc083bc28cdd016e49f152d62803075e7ed94518efc8147ab33fbc58b2101322d1e65f3b79c6fec4b39bfdad3565684638bae390fd4626aafff6ab71167c77265a269b2f71bae44b407e219c3d0274e60a28b70"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup", response_model=UserResponse)
async def signup(
    email: str = Form(..., description="User email"),
    password: str = Form(..., description="User password"),
    image: UploadFile = File(..., description="User face image (JPEG/PNG)"),
    db: Session = Depends(get_db)
):
    """
    Register a new user with email, password and face image.
    """
    # Validate content type first
    if not image.content_type in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are supported"
        )

    # Basic validations
    if not "@" in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Check if user exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Read image data once
        image_data = await image.read()
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        # Detect face in the image
        image_array = face_recognition.load_image_file(io.BytesIO(image_data))
        face_locations = face_recognition.face_locations(image_array)
        
        if not face_locations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image"
            )
        
        if len(face_locations) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiple faces detected. Please provide an image with a single face"
            )
        
        # Hash password
        hashed_password = pwd_context.hash(password)
        
        # Create new user
        db_user = User(
            email=email,
            password=hashed_password,
            image=image_data
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse(
            id=db_user.id,
            email=email,
            message="User registered successfully"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login/password", response_model=Token)
async def login_password(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login with email and password using form data
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(
        access_token=access_token, 
        token_type="bearer",
        user_id=user.id
    )

@router.post("/login/face", response_model=Token)
async def login_face(
    image: UploadFile = File(..., description="Live captured face image"),
    db: Session = Depends(get_db)
):
    """
    Login with face recognition using a live captured image
    """
    try:
        image_data = await image.read()
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        # Check against all users
        for user in db.query(User).all():
            match, result = compare_faces(user.image, image_data)
            if match:
                access_token = create_access_token(data={"sub": user.email})
                return Token(
                    access_token=access_token,
                    token_type="bearer",
                    user_id=user.id
                )
            elif isinstance(result, str):
                # If result is an error message
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result
                )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Face not recognized"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Face authentication failed: {str(e)}"
        )
