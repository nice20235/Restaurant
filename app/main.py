from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os

from app.db.database import init_db, close_db
from app.api.endpoints import users, food, orders, categories
from app.auth.routes import auth_router
from app.telegram_bot import start_telegram_bot

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    print("🚀 Starting Restaurant Order System...")
    await init_db()
    print("📱 Starting Telegram bot...")
    start_telegram_bot()
    print("✅ Application started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_db()
    print("✅ Application shutdown complete!")

# Create FastAPI application
app = FastAPI(
    title="Restaurant Order System",
    description="A modern restaurant ordering system with phone-based authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error responses"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else "Something went wrong"
        }
    )

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(food.router, prefix="/foods", tags=["Foods"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Restaurant Order System is running"}

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Restaurant Order System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 