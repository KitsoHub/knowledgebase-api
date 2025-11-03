
# ----------------------------
# Stage 1: Builder
# ----------------------------
FROM python:3.9-slim-bullseye as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY ./app /app
WORKDIR /app

# Install system dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libopenjp2-7-dev

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-warn-script-location -r requirements.txt
# ----------------------------
# Stage 2: Runtime
# ----------------------------
FROM python:3.9-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/django-user/.local/bin:$PATH" \
    PYTHONPATH="/app"

# Create non-root user
RUN groupadd -g 1000 django-user && \
    useradd -u 1000 -g django-user -d /home/django-user django-user && \
    mkdir -p /home/django-user/app && \
    mkdir -p /vol/web/media /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# Install runtime dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62 \
    zlib1g && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER django-user
WORKDIR /app

# Copy installed dependencies
COPY --from=builder --chown=django-user:django-user /root/.local /home/django-user/.local

# Copy application code
COPY --chown=django-user:django-user . .

EXPOSE 8000
