from pydantic import BaseModel
from typing import Optional

class FoodBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    available: bool = True

class FoodCreate(FoodBase):
    pass

class FoodUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None

class FoodInDB(FoodBase):
    id: int
    class Config:
        from_attributes = True 