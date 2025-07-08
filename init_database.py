#!/usr/bin/env python3
"""
Database initialization script
Run this to create all database tables
"""

import asyncio
from app.db.database import engine, Base
from app.models import user, food, order

async def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("Tables created:")
    print("- users")
    print("- foods") 
    print("- orders")

if __name__ == "__main__":
    asyncio.run(init_database()) 