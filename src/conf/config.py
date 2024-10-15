from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Змінні з файлу .env
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    database_url: str
    jwt_secret_key: str
    algorithm: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    hashing_scheme: str
    use_https: bool
    redis_host: str
    redis_port: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
