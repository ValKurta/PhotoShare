# Stage 1: Build stage to extract dependencies from Poetry to requirements.txt
FROM python:3.12-alpine as stage1

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes 
    
FROM python:3.12-alpine as final

ENV APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apk update \
    && apk upgrade \
    && apk add bash

# Copying the requirements.txt file
COPY --from=stage1 /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

# # Ensure the script is executable
RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
