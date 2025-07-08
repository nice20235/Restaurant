from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.crud.user import get_user_by_username, create_user, verify_password, get_user_by_email, get_password_hash
from app.auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.models.user import UserRole
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = await get_user_by_email(db, user.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_obj = await create_user(db, user)
    return {"msg": "User registered successfully", "user_id": user_obj.id}

@router.post("/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/reset-password")
async def reset_password(email: str, new_password: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    return {"msg": "Password reset successful"}

@router.post("/logout")
async def logout():
    # JWT logout is handled client-side by deleting the token
    return {"msg": "Logout successful."}

@router.post("/refresh")
async def refresh_token_endpoint(refresh_token: str = Body(..., embed=True)):
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    username = payload.get("sub")
    role = payload.get("role", "user")
    access_token = create_access_token(data={"sub": username, "role": role})
    return {"access_token": access_token, "token_type": "bearer"} 