from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List, Tuple

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.orders))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> Optional[User]:
    """Get user by phone number"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.orders))
        .where(User.phone_number == phone_number)
    )
    return result.scalar_one_or_none()

async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    is_admin: Optional[bool] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[User], int]:
    """Get users with pagination and filters"""
    # Build query
    query = select(User).options(selectinload(User.orders))
    
    # Apply filters
    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    result = await db.execute(query.offset(skip).limit(limit))
    users = result.scalars().all()
    
    return users, total

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Load relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.orders))
        .where(User.id == db_user.id)
    )
    return result.scalar_one()

async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate) -> User:
    """Update user"""
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Load relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.orders))
        .where(User.id == db_user.id)
    )
    return result.scalar_one()

async def delete_user(db: AsyncSession, db_user: User) -> bool:
    """Delete user"""
    await db.delete(db_user)
    await db.commit()
    return True

async def promote_to_admin(db: AsyncSession, phone_number: str) -> Optional[User]:
    """Promote user to admin by phone number"""
    user = await get_user_by_phone_number(db, phone_number)
    if not user:
        return None
    
    user.is_admin = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Load relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.orders))
        .where(User.id == user.id)
    )
    return result.scalar_one() 