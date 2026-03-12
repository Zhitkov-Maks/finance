FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN addgroup -S botgroup && \
    adduser -S botuser -G botgroup

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

WORKDIR ./finance_bot

COPY --chown=botuser:botgroup . .

CMD ["python", "-m", "main"]
