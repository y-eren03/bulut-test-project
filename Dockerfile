# STAGE 1: Build dependency
FROM python:3.11-slim AS builder

WORKDIR /app

# Poetry kurulumu
RUN pip install poetry==1.7.1

# Bağımlılıkları kopyala ve kur
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# STAGE 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Sadece gereken kütüphaneleri ilk aşamadan al (Sistem geneline kurulduğu için site-packages kopyalamak yerine builder mantığı)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Proje kodlarını kopyala
COPY src/ ./src/

# Port ve komut
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
