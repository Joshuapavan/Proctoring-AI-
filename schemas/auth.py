from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    message: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
