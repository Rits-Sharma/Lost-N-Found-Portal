"""Pydantic schemas for user models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema for user registration."""
    name: str = Field(...,min_length=1,max_length=255)
    email: EmailStr
    password: str = Field(...,min_length=6)
    phone: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@college.edu",
                "password": "securepassword123",
                "phone": "+1234567890"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@college.edu",
                "password": "securepassword123"
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user response (public info)."""
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@college.edu",
                "phone": "+1234567890",
                "role": "STUDENT",
                "created_at": "2024-01-15T10:30:00"
            }
        }
    )


class UserInDB(UserResponse):
    """Schema for user in database (includes sensitive info)."""
    password_hash: str


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse