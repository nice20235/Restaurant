from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.order import OrderInDB, OrderCreate, OrderUpdate
from app.crud.order import get_orders, get_orders_by_user, get_order, create_order, update_order, delete_order
from app.auth.dependencies import get_current_user, get_current_admin
from app.models.user import UserRole

router = APIRouter()

@router.post("/", response_model=OrderInDB)
async def create_order_endpoint(order: OrderCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await create_order(db, user.id, order)

@router.get("/", response_model=list[OrderInDB])
async def list_orders(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if user.role == UserRole.admin:
        return await get_orders(db)
    return await get_orders_by_user(db, user.id)

@router.put("/{order_id}", response_model=OrderInDB)
async def update_order_endpoint(order_id: int, order_update: OrderUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    db_order = await get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user.role != UserRole.admin and db_order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await update_order(db, db_order, order_update)

@router.delete("/{order_id}")
async def delete_order_endpoint(order_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    db_order = await get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user.role != UserRole.admin and db_order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await delete_order(db, db_order)
    return {"msg": "Order deleted"} 