#!/usr/bin/env python3
"""
Restaurant Order System - Complete Initialization Script
This script sets up the entire system including database, sample data, and admin user.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.db.database import init_db, AsyncSessionLocal
from app.models.user import User
from app.models.food import Category, Food
from app.crud.user import create_user, promote_to_admin
from app.crud.food import create_category, create_food
from app.schemas.user import UserCreate
from app.schemas.food import CategoryCreate, FoodCreate

# Sample data
SAMPLE_CATEGORIES = [
    {"name": "Appetizers", "description": "Start your meal with our delicious appetizers"},
    {"name": "Main Courses", "description": "Our signature main dishes"},
    {"name": "Desserts", "description": "Sweet endings to your meal"},
    {"name": "Beverages", "description": "Refreshing drinks and beverages"},
    {"name": "Salads", "description": "Fresh and healthy salad options"},
]

SAMPLE_FOODS = [
    # Appetizers
    {"name": "Bruschetta", "description": "Toasted bread with tomatoes and herbs", "price": 8.99, "category_name": "Appetizers"},
    {"name": "Mozzarella Sticks", "description": "Crispy breaded mozzarella with marinara", "price": 7.99, "category_name": "Appetizers"},
    {"name": "Garlic Bread", "description": "Fresh bread with garlic butter", "price": 4.99, "category_name": "Appetizers"},
    
    # Main Courses
    {"name": "Margherita Pizza", "description": "Classic pizza with tomato and mozzarella", "price": 16.99, "category_name": "Main Courses"},
    {"name": "Spaghetti Carbonara", "description": "Pasta with eggs, cheese, and pancetta", "price": 18.99, "category_name": "Main Courses"},
    {"name": "Grilled Salmon", "description": "Fresh salmon with seasonal vegetables", "price": 24.99, "category_name": "Main Courses"},
    {"name": "Beef Burger", "description": "Juicy beef burger with fries", "price": 14.99, "category_name": "Main Courses"},
    
    # Desserts
    {"name": "Tiramisu", "description": "Classic Italian coffee-flavored dessert", "price": 8.99, "category_name": "Desserts"},
    {"name": "Chocolate Cake", "description": "Rich chocolate cake with vanilla ice cream", "price": 7.99, "category_name": "Desserts"},
    {"name": "Cheesecake", "description": "New York style cheesecake", "price": 6.99, "category_name": "Desserts"},
    
    # Beverages
    {"name": "Coca Cola", "description": "Refreshing cola drink", "price": 2.99, "category_name": "Beverages"},
    {"name": "Orange Juice", "description": "Fresh squeezed orange juice", "price": 3.99, "category_name": "Beverages"},
    {"name": "Coffee", "description": "Freshly brewed coffee", "price": 2.49, "category_name": "Beverages"},
    
    # Salads
    {"name": "Caesar Salad", "description": "Romaine lettuce with Caesar dressing", "price": 9.99, "category_name": "Salads"},
    {"name": "Greek Salad", "description": "Fresh vegetables with feta cheese", "price": 10.99, "category_name": "Salads"},
]

async def create_sample_categories(db: AsyncSessionLocal):
    """Create sample categories"""
    print("📂 Creating sample categories...")
    categories = {}
    
    for cat_data in SAMPLE_CATEGORIES:
        category = CategoryCreate(**cat_data)
        db_category = await create_category(db, category)
        categories[cat_data["name"]] = db_category
        print(f"  ✅ Created category: {db_category.name}")
    
    return categories

async def create_sample_foods(db: AsyncSessionLocal, categories):
    """Create sample foods"""
    print("🍽️  Creating sample foods...")
    
    for food_data in SAMPLE_FOODS:
        category_name = food_data.pop("category_name")
        category = categories.get(category_name)
        
        if category:
            food_data["category_id"] = category.id
            food = FoodCreate(**food_data)
            db_food = await create_food(db, food)
            print(f"  ✅ Created food: {db_food.name} (${db_food.price})")
        else:
            print(f"  ⚠️  Category '{category_name}' not found for food: {food_data['name']}")

async def create_admin_user(db: AsyncSessionLocal):
    """Create default admin user"""
    print("👤 Creating admin user...")
    
    # You can change this phone number
    admin_phone = "+1234567890"
    
    # Check if admin already exists
    from app.crud.user import get_user_by_phone_number
    existing_admin = await get_user_by_phone_number(db, admin_phone)
    
    if existing_admin:
        if existing_admin.is_admin:
            print(f"  ✅ Admin user already exists: {admin_phone}")
            return existing_admin
        else:
            # Promote existing user to admin
            admin_user = await promote_to_admin(db, admin_phone)
            print(f"  ✅ Promoted user to admin: {admin_phone}")
            return admin_user
    else:
        # Create new admin user
        admin_data = UserCreate(
            phone_number=admin_phone,
            is_admin=True,
            is_active=True
        )
        admin_user = await create_user(db, admin_data)
        print(f"  ✅ Created admin user: {admin_phone}")
        return admin_user

async def main():
    """Main initialization function"""
    print("🚀 Initializing Restaurant Order System...")
    print("=" * 50)
    
    try:
        # Initialize database
        print("🗄️  Initializing database...")
        await init_db()
        print("  ✅ Database initialized successfully!")
        
        # Create sample data
        async with AsyncSessionLocal() as db:
            # Create categories
            categories = await create_sample_categories(db)
            
            # Create foods
            await create_sample_foods(db, categories)
            
            # Create admin user
            admin_user = await create_admin_user(db)
        
        print("\n" + "=" * 50)
        print("✅ System initialization completed successfully!")
        print("\n📋 Summary:")
        print(f"  • Database: restaurant.db")
        print(f"  • Categories: {len(categories)}")
        print(f"  • Foods: {len(SAMPLE_FOODS)}")
        if admin_user:
            print(f"  • Admin user: {admin_user.phone_number}")
        else:
            print(f"  • Admin user: Not created")
        
        print("\n🔧 Next steps:")
        print("  1. Start the FastAPI server: python -m uvicorn app.main:app --reload")
        print("  2. Access the API documentation: http://localhost:8000/docs")
        print("  3. Use the admin phone number to authenticate")
        print("  4. Test the Telegram bot for phone verification")
        
        print("\n📱 Telegram Bot Setup:")
        print("  1. Set TELEGRAM_BOT_TOKEN environment variable")
        print("  2. The bot will start automatically with the server")
        print("  3. Users can share their phone number to get verification codes")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 