from sqlalchemy import String, Integer, Boolean, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.order import Order

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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
    
    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_users_phone_number', 'phone_number'),
        Index('idx_users_admin', 'is_admin'),
        Index('idx_users_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, phone_number='{self.phone_number}', is_admin={self.is_admin})>" 