from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate

async def get_order(db: AsyncSession, order_id: int):
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Order).offset(skip).limit(limit))
    return result.scalars().all()

async def get_orders_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Order).where(Order.user_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_order(db: AsyncSession, user_id: int, order: OrderCreate):
    db_order = Order(user_id=user_id, **order.dict())
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def update_order(db: AsyncSession, db_order: Order, order_update: OrderUpdate):
    for field, value in order_update.dict(exclude_unset=True).items():
        setattr(db_order, field, value)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def delete_order(db: AsyncSession, db_order: Order):
    await db.delete(db_order)
    await db.commit() 