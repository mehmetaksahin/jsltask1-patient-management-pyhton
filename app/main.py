"""
FastAPI Uygulama Giriş Noktası

Bu dosya uygulamanın başlangıç noktasıdır.

Java Karşılaştırması:
--------------------
Java (PatientApplication.java):

    @SpringBootApplication
    public class PatientApplication {
        public static void main(String[] args) {
            SpringApplication.run(PatientApplication.class, args);
        }
    }

Python (main.py):

    app = FastAPI(title="Patient Management API")

    @app.on_event("startup")
    async def startup():
        # Veritabanı tablolarını oluştur
        pass

    if __name__ == "__main__":
        uvicorn.run("app.main:app", host="0.0.0.0", port=8080)

FastAPI Uygulama Yapısı:
-----------------------
1. FastAPI() instance oluştur
2. Router'ları ekle (include_router)
3. Middleware'leri ekle (CORS, logging vb.)
4. Event handler'ları tanımla (startup, shutdown)
5. Uvicorn ile çalıştır

Uvicorn Nedir?
-------------
ASGI (Asynchronous Server Gateway Interface) sunucusu.
Java'daki Tomcat/Jetty'ye karşılık gelir.
FastAPI uygulamasını HTTP isteklerini dinleyecek şekilde çalıştırır.

Swagger UI:
----------
FastAPI otomatik olarak Swagger UI sağlar:
- /docs -> Swagger UI (interaktif API dokümantasyonu)
- /redoc -> ReDoc (alternatif dokümantasyon)
- /openapi.json -> OpenAPI spesifikasyonu

Java'da SpringDoc veya Swagger annotation'ları gerekir,
Python FastAPI'de otomatik!
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import postgresql_engine, PostgreSQLBase
from app.controllers import patient_controller, health_controller

# =============================================================================
# LOGGING KONFİGÜRASYONU
# =============================================================================
# Java'daki logback.xml veya application.yml logging ayarlarına karşılık gelir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # Java format: %d{yyyy-MM-dd HH:mm:ss} - %logger{36} - %msg%n
)

# Bazı kütüphanelerin log seviyesini ayarla (Java'daki logging.level.xxx gibi)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("snowflake.connector").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# =============================================================================
# LIFESPAN EVENTS (Başlatma ve Kapatma)
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama yaşam döngüsü yönetimi.

    Java Karşılığı:
        @EventListener(ApplicationReadyEvent.class)
        public void onApplicationReady() {
            // Başlatma işlemleri
        }

        @PreDestroy
        public void onShutdown() {
            // Kapatma işlemleri
        }

    asynccontextmanager Nedir?
    -------------------------
    Python'da "async with" kullanılan context manager.
    yield öncesi: startup işlemleri
    yield sonrası: shutdown işlemleri
    """
    # =========================================================================
    # STARTUP - Uygulama başlarken
    # =========================================================================
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)

    # Veritabanı tablolarını oluştur (Alembic yoksa)
    # Java'daki hibernate.hbm2ddl.auto=create-drop gibi
    # Ama production'da Alembic/Flyway kullanılmalı
    try:
        logger.info("Creating database tables...")
        PostgreSQLBase.metadata.create_all(bind=postgresql_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Hata olsa bile başlat (tablo zaten var olabilir)

    logger.info(f"Server running on http://{settings.server_host}:{settings.server_port}")
    logger.info("Swagger UI available at: /docs")
    logger.info("ReDoc available at: /redoc")
    logger.info("=" * 60)

    yield  # Uygulama çalışıyor

    # =========================================================================
    # SHUTDOWN - Uygulama kapanırken
    # =========================================================================
    logger.info("Shutting down application...")
    logger.info("Goodbye!")


# =============================================================================
# FASTAPI UYGULAMA OLUŞTURMA
# =============================================================================
# Java'daki @SpringBootApplication annotation'ının karşılığı

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Patient Management API

    Snowflake'den PostgreSQL'e hasta verisi aktarımı yapan ETL uygulaması.

    ### Özellikler:
    * **Patient CRUD**: Hasta kayıtlarını yönet
    * **ETL Migration**: Snowflake'den PostgreSQL'e veri aktarımı
    * **Health Check**: Sistem sağlık kontrolü

    ### Teknolojiler:
    * FastAPI (Python web framework)
    * SQLAlchemy (ORM)
    * PostgreSQL (hedef veritabanı)
    * Snowflake (kaynak veritabanı)
    """,
    lifespan=lifespan,  # Yaşam döngüsü yönetimi

    # OpenAPI/Swagger ayarları
    openapi_tags=[
        {
            "name": "Patients",
            "description": "Patient CRUD operations"
        },
        {
            "name": "Health & Info",
            "description": "Health check and application info (Actuator-like)"
        }
    ]
)


# =============================================================================
# CORS MIDDLEWARE
# =============================================================================
# Cross-Origin Resource Sharing - Farklı domain'lerden isteklere izin ver
# Java'da @CrossOrigin veya WebMvcConfigurer ile yapılır

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik origin'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, vb.
    allow_headers=["*"],
)


# =============================================================================
# ROUTER'LARI EKLE
# =============================================================================
# Java'daki @ComponentScan ile controller'ların otomatik bulunmasına karşılık gelir
# Python'da manuel olarak ekliyoruz

app.include_router(patient_controller.router)
app.include_router(health_controller.router)


# =============================================================================
# ROOT ENDPOINT
# =============================================================================
@app.get("/", tags=["Root"])
def root():
    """
    Ana sayfa - API bilgisi döner.

    Java'da genellikle static bir sayfa veya redirect olur.
    Burada basit bir JSON döndürüyoruz.

    Returns:
        dict: API bilgisi
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/actuator/health"
    }


# =============================================================================
# UYGULAMA ÇALIŞTIRMA
# =============================================================================
# Java'daki main metoduna karşılık gelir

if __name__ == "__main__":
    """
    Doğrudan çalıştırma: python -m app.main

    Java Karşılığı:
        java -jar patient-management.jar

    veya

        mvn spring-boot:run

    Uvicorn Parametreleri:
    ---------------------
    - "app.main:app": Modül yolu ve uygulama değişkeni
    - host: Dinlenecek IP adresi (0.0.0.0 = tüm interface'ler)
    - port: Dinlenecek port
    - reload: Kod değişikliklerinde otomatik yeniden başlat (development için)
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug  # Debug modunda auto-reload
    )
