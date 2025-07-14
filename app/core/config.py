from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/restaurant"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TELEGRAM_BOT_TOKEN: str = "8045814472:AAEuenV-dYJi8v-AhKKX7lX9RquEz6nQelY"  # <-- Add this line

    class Config:
        env_file = ".env"

settings = Settings() 