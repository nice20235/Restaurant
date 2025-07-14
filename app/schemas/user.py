from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    phone_number: str = Field(..., description="User's phone number", min_length=10, max_length=20)
    is_admin: bool = Field(default=False, description="Whether user is an admin")
    is_active: bool = Field(default=True, description="Whether user account is active")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, description="User's phone number", min_length=10, max_length=20)
    is_admin: Optional[bool] = Field(None, description="Whether user is an admin")
    is_active: Optional[bool] = Field(None, description="Whether user account is active")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None and not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        return v

class UserInDB(UserBase):
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserResponse(UserInDB):
    """User response schema for API endpoints"""
    pass

class UserList(BaseModel):
    """Schema for list of users"""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of users skipped")
    limit: int = Field(..., description="Maximum number of users returned") 