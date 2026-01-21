ARG PYTHON_VERSION=3.13.3
FROM node:22-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
RUN ls -la /frontend/  # Debug: see what was created


# Python stage
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY backend/requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=backend/requirements.txt,target=requirements.txt \
    apt-get update && apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    python -m pip install -r requirements.txt


RUN mkdir -p in out && chown appuser:appuser in out

COPY backend/ ./api-scripts

# Copy built frontend from Node build stage
COPY --from=frontend-build /frontend/dist ./static

RUN chown -R appuser:appuser /app

WORKDIR /app/api-scripts

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host=0.0.0.0", "--port=8000"]
