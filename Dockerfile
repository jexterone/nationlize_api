# Dockerfile
FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "nationalize_api.wsgi:application"]