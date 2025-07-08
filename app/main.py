from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.food import router as food_router
from app.api.endpoints.orders import router as orders_router
from app.db.database import engine, Base
from app.models import user, food, order
import asyncio
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# Allow your frontend origin here (or allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("Please check your DATABASE_URL in .env file")
        print("For development, you can use: DATABASE_URL=sqlite+aiosqlite:///./restaurant.db")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(food_router, prefix="/foods", tags=["foods"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])

@app.get("/")
def root():
    
    return {"msg": "Restaurant API is running"} 