from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., description="Category name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Category description", max_length=255)
    is_active: bool = Field(default=True, description="Whether category is active")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Category name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Category description", max_length=255)
    is_active: Optional[bool] = Field(None, description="Whether category is active")

class CategoryInDB(CategoryBase):
    id: int = Field(..., description="Category ID")
    created_at: datetime = Field(..., description="Category creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CategoryResponse(CategoryInDB):
    """Category response schema for API endpoints"""
    pass

# Food schemas
class FoodBase(BaseModel):
    name: str = Field(..., description="Food name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Food description", max_length=500)
    price: float = Field(..., description="Food price", gt=0)
    available: bool = Field(default=True, description="Whether food is available")
    category_id: Optional[int] = Field(None, description="Category ID")

class FoodCreate(FoodBase):
    pass

class FoodUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Food name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Food description", max_length=500)
    price: Optional[float] = Field(None, description="Food price", gt=0)
    available: Optional[bool] = Field(None, description="Whether food is available")
    category_id: Optional[int] = Field(None, description="Category ID")

class FoodInDB(FoodBase):
    id: int = Field(..., description="Food ID")
    created_at: datetime = Field(..., description="Food creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    category: Optional[CategoryInDB] = Field(None, description="Associated category")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FoodResponse(FoodInDB):
    """Food response schema for API endpoints"""
    pass

class FoodList(BaseModel):
    """Schema for list of foods"""
    foods: List[FoodResponse] = Field(..., description="List of foods")
    total: int = Field(..., description="Total number of foods")
    skip: int = Field(..., description="Number of foods skipped")
    limit: int = Field(..., description="Maximum number of foods returned") 