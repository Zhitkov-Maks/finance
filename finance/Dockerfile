# Stage 1: Builder
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Установка зависимостей для сборки
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    openssl-dev

WORKDIR /build

# Копирование requirements и установка пакетов в временную директорию
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.13-alpine

# Создание пользователя
RUN addgroup -g 1000 -S financegroup && \
    adduser -S financeuser -u 1000 -G financegroup

# Установка runtime зависимостей
RUN apk add --no-cache \
    libpq \
    curl \
    bash

# Копирование установленных пакетов из билдера
COPY --from=builder /install /usr/local

WORKDIR /finance

# Создание необходимых директорий
RUN mkdir -p /finance/staticfiles \
    /finance/media \
    /finance/logs \
    && chown -R financeuser:financegroup /finance

# Копирование приложения
COPY --chown=financeuser:financegroup . .

# Права на entrypoint
RUN chmod +x /finance/entrypoint.sh 2>/dev/null || true

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health/ || exit 1

USER financeuser

EXPOSE 8001

# Использование entrypoint если есть
ENTRYPOINT ["/finance/entrypoint.sh"]
