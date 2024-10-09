# PhotoShare

# based on poetry interpreter
poetry install(poetry update)

# docker
docker system prune -af
docker-compose up --build

# alembic migration
alembic init alembic
changes in alembic.ini(sqlalchemy.url)

# in a new cmd/terminal after "docker-compose up --build":
docker exec -it photoshare_app /bin/bash
poetry run alembic revision --autogenerate -m "Initial migration"
poetry run alembic upgrade head

# JWT_SECRET_KEY generation
import secrets
JWT_SECRET_KEY = secrets.token_urlsafe(32)
print(JWT_SECRET_KEY)

# black/flake8
poetry run black .
poetry run flake8 .

# pre-commit(every time when commit) - manual run
# poetry run pre-commit install
poetry run pre-commit run --all-files

# commit without pre-commit checks
git commit -m "commit message" --no-verify