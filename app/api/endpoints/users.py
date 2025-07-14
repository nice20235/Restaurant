from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.user import UserInDB
from app.crud.user import get_users, get_user, delete_user
from app.auth.dependencies import get_current_admin

import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=list[UserInDB])
async def list_users(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """
    List all users. Admin-only endpoint.
    """
    logger.info(f"Admin {admin.phone_number} listing all users")
    return await get_users(db)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """
    Get user details by ID. Admin-only endpoint.
    """
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Admin {admin.phone_number} viewing user details: {user.phone_number}")
    return user

@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """
    Delete a user by ID. Admin-only endpoint.
    """
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user.id == admin.id:
        logger.warning(f"Admin {admin.phone_number} attempted to delete themselves")
        raise HTTPException(
            status_code=400, 
            detail="You cannot delete your own account"
        )
    
    logger.info(f"Admin {admin.phone_number} deleting user: {user.phone_number}")
    await delete_user(db, user)
    return {"msg": "User deleted"} 