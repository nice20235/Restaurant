from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.food import FoodInDB, FoodCreate, FoodUpdate
from app.crud.food import get_foods, get_food, create_food, update_food, delete_food
from app.auth.dependencies import get_current_admin

router = APIRouter()

@router.get("/", response_model=list[FoodInDB])
async def list_foods(db: AsyncSession = Depends(get_db)):
    return await get_foods(db)

@router.post("/", response_model=FoodInDB)
async def create_food_endpoint(food: FoodCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    return await create_food(db, food)

@router.put("/{food_id}", response_model=FoodInDB)
async def update_food_endpoint(food_id: int, food_update: FoodUpdate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    db_food = await get_food(db, food_id)
    if not db_food:
        raise HTTPException(status_code=404, detail="Food not found")
    return await update_food(db, db_food, food_update)

@router.delete("/{food_id}")
async def delete_food_endpoint(food_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    db_food = await get_food(db, food_id)
    if not db_food:
        raise HTTPException(status_code=404, detail="Food not found")
    await delete_food(db, db_food)
    return {"msg": "Food deleted"} 