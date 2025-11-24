from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = "Gestor de Personal y Operaciones"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./app.db"
    JWT_SECRET_KEY: str = "CAMBIA_ESTA_CLAVE_POR_ALGO_MAS_LARGO"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 horas


settings = Settings()
