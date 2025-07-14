from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.auth.jwt import create_access_token, decode_access_token
from app.crud.user import get_user_by_phone_number, create_user
from app.schemas.user import UserCreate, UserInDB
from app.telegram_bot import validate_telegram_code
from app.auth.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter()

@auth_router.post("/verify-code")
async def verify_code(
    phone_number: str,
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify phone number with Telegram code and return JWT token
    """
    # Validate the code
    if not validate_telegram_code(phone_number, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification code"
        )
    
    # Check if user exists
    user = await get_user_by_phone_number(db, phone_number)
    if not user:
        # Create new user
        user_data = UserCreate(
            phone_number=phone_number,
            is_admin=False,
            is_active=True
        )
        user = await create_user(db, user_data)
        logger.info(f"Created new user: {phone_number}")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.phone_number})
    
    logger.info(f"User authenticated successfully: {phone_number}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone_number": user.phone_number,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }
    }

@auth_router.post("/register")
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user (admin only)
    """
    # Check if user already exists
    existing_user = await get_user_by_phone_number(db, user_data.phone_number)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    # Create new user
    user = await create_user(db, user_data)
    logger.info(f"Admin created new user: {user.phone_number}")
    
    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "phone_number": user.phone_number,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }
    }

@auth_router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "phone_number": current_user.phone_number,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active
    } 