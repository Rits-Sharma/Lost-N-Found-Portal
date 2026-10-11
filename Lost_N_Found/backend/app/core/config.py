from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "lost_found_portal"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    API_TITLE: str = "College Lost & Found Portal"
    API_VERSION: str = "1.0.0"

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()