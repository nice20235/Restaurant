from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.food import Food
from app.schemas.food import FoodCreate, FoodUpdate

async def get_food(db: AsyncSession, food_id: int):
    result = await db.execute(select(Food).where(Food.id == food_id))
    return result.scalar_one_or_none()

async def get_foods(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Food).offset(skip).limit(limit))
    return result.scalars().all()

async def create_food(db: AsyncSession, food: FoodCreate):
    db_food = Food(**food.dict())
    db.add(db_food)
    await db.commit()
    await db.refresh(db_food)
    return db_food

async def update_food(db: AsyncSession, db_food: Food, food_update: FoodUpdate):
    for field, value in food_update.dict(exclude_unset=True).items():
        setattr(db_food, field, value)
    db.add(db_food)
    await db.commit()
    await db.refresh(db_food)
    return db_food

async def delete_food(db: AsyncSession, db_food: Food):
    await db.delete(db_food)
    await db.commit() 