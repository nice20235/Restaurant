from pydantic import BaseModel
from typing import Optional

class OrderBase(BaseModel):
    food_id: int
    quantity: int = 1

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    quantity: Optional[int] = None

class OrderInDB(OrderBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True 