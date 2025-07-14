from sqlalchemy import String, Integer, Float, Boolean, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship with foods
    foods: Mapped[list["Food"]] = relationship("Food", back_populates="category", cascade="all, delete-orphan")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_categories_name', 'name'),
        Index('idx_categories_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Food(Base):
    __tablename__ = "foods"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("categories.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship with category
    category: Mapped[Category] = relationship("Category", back_populates="foods")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_foods_name', 'name'),
        Index('idx_foods_price', 'price'),
        Index('idx_foods_available', 'available'),
        Index('idx_foods_category', 'category_id'),
    )
    
    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.name}', price={self.price})>" 