from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.auth.jwt import decode_access_token
from app.models.user import User
from app.crud.user import get_user_by_phone_number
from sqlalchemy.future import select
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Note: This will need to be updated when authentication endpoints are added
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify-code")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        logger.warning("Invalid JWT token or missing subject")
        raise credentials_exception
    phone_number: str = payload["sub"]
    user = await get_user_by_phone_number(db, phone_number)
    if user is None:
        logger.warning(f"User not found: {phone_number}")
        raise credentials_exception
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {phone_number}")
        raise HTTPException(status_code=400, detail="Inactive user")
    logger.info(f"User authenticated successfully: {phone_number} (Admin: {user.is_admin})")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        logger.warning(f"Non-admin user attempted admin access: {current_user.phone_number} (Admin: {current_user.is_admin})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin access required. You don't have permission to access this resource."
        )
    logger.info(f"Admin access granted: {current_user.phone_number}")
    return current_user

async def get_current_user_or_admin(current_user: User = Depends(get_current_user)):
    return current_user 