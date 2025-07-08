from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.user import UserInDB
from app.crud.user import get_users, get_user, delete_user
from app.auth.dependencies import get_current_admin
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=list[UserInDB])
async def list_users(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    return await get_users(db)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user(db, user)
    return {"msg": "User deleted"} 