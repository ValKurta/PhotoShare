# PhotoShare

# based on poetry interpreter
poetry install(poetry update)

# docker
docker-compose up --build

#JWT_SECRET_KEY generation
import secrets
JWT_SECRET_KEY = secrets.token_urlsafe(32)
print(JWT_SECRET_KEY)

