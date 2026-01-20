# =============================================================================
# PYTHON FASTAPI DOCKERFILE
# =============================================================================
# Bu Dockerfile, Patient Management API'yi container'a paketler.
#
# Java Karşılaştırması:
# --------------------
# Java Dockerfile (multi-stage):
#
#   FROM maven:3.9-eclipse-temurin-17 AS build
#   COPY pom.xml .
#   RUN mvn dependency:go-offline
#   COPY src ./src
#   RUN mvn package -DskipTests
#
#   FROM eclipse-temurin:17-jre
#   COPY --from=build target/*.jar app.jar
#   ENTRYPOINT ["java", "-jar", "app.jar"]
#
# Python Dockerfile:
#
#   FROM python:3.11-slim
#   COPY requirements.txt .
#   RUN pip install -r requirements.txt
#   COPY app ./app
#   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
#
# Farklar:
# --------
# 1. Java'da build aşaması gerekli (compile), Python'da yok (interpreted)
# 2. Java'da JAR dosyası oluşur, Python'da kaynak kod doğrudan çalışır
# 3. Java'da JRE gerekli, Python'da Python runtime gerekli
# =============================================================================

# =============================================================================
# BASE IMAGE
# =============================================================================
# python:3.11-slim: Minimal Python image (debian tabanlı)
# - slim: Gereksiz araçlar çıkarılmış, daha küçük image
# - alpine da kullanılabilir ama bazı uyumluluk sorunları olabilir
FROM python:3.11-slim

# =============================================================================
# METADATA
# =============================================================================
# Image hakkında bilgiler
LABEL maintainer="Mehmet Aksahin"
LABEL description="Patient Management API - Snowflake to PostgreSQL ETL"
LABEL version="1.0.0"

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================
# Python optimizasyonları
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Uygulama dizini
ENV APP_HOME=/app
WORKDIR ${APP_HOME}

# =============================================================================
# SYSTEM DEPENDENCIES
# =============================================================================
# Bazı Python paketleri için gerekli sistem kütüphaneleri
# psycopg2 ve snowflake-connector için
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# PYTHON DEPENDENCIES
# =============================================================================
# Önce requirements.txt'i kopyala ve bağımlılıkları yükle
# Bu, Docker cache'inden faydalanmak için ayrı bir katman olarak yapılır
# (Java'da da pom.xml önce kopyalanır, dependency:go-offline çalıştırılır)
COPY requirements.txt .

# Bağımlılıkları yükle
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# APPLICATION CODE
# =============================================================================
# Uygulama kodunu kopyala
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

# =============================================================================
# NON-ROOT USER
# =============================================================================
# Güvenlik için root olmayan kullanıcı ile çalıştır
# Java'da da aynı practice uygulanır
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser ${APP_HOME}
USER appuser

# =============================================================================
# PORT
# =============================================================================
# Uygulamanın dinleyeceği port
# Java: EXPOSE 8080 (aynı)
EXPOSE 8080

# =============================================================================
# HEALTHCHECK
# =============================================================================
# Container sağlık kontrolü
# Docker/Kubernetes bu endpoint'i kullanarak container'ın sağlıklı olup olmadığını kontrol eder
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/actuator/health')" || exit 1

# =============================================================================
# ENTRYPOINT
# =============================================================================
# Uygulamayı başlat
# Java: ENTRYPOINT ["java", "-jar", "app.jar"]
# Python: Uvicorn ASGI server ile FastAPI uygulamasını çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
