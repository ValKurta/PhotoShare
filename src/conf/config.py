from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
