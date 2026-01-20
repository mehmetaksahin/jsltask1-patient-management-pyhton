"""
Health Controller - Sağlık Kontrolü Endpoint'leri

Bu dosya Spring Boot Actuator benzeri health check endpoint'lerini sağlar.

Java Karşılaştırması:
--------------------
Spring Boot Actuator otomatik olarak şu endpoint'leri sağlar:
- GET /actuator/health -> Sistem sağlığı
- GET /actuator/info   -> Uygulama bilgileri

Python'da bu endpoint'leri manuel oluşturuyoruz.

Health Check Neden Önemli?
-------------------------
1. Kubernetes/Docker health probe'ları için
2. Load balancer'ların sunucu durumunu kontrol etmesi için
3. Monitoring sistemleri için
4. Uygulama bağımlılıklarının durumunu izlemek için

Snowflake SPCS'de:
-----------------
patient-service-spec.yaml dosyasında health probe tanımlanabilir.
Bu endpoint'ler container'ın sağlıklı olup olmadığını kontrol eder.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.database import get_postgresql_db, snowflake_session
from app.config.settings import settings
from app.schemas.patient import HealthResponse, InfoResponse

# Logger
logger = logging.getLogger(__name__)

# Router - /actuator prefix'i ile (Spring Boot Actuator gibi)
router = APIRouter(
    prefix="/actuator",
    tags=["Health & Info"]  # Swagger'da kategori
)


def check_postgresql_health(db: Session) -> Dict[str, str]:
    """
    PostgreSQL bağlantısını kontrol eder.

    SELECT 1 sorgusu ile veritabanının erişilebilir olduğunu doğrular.

    Args:
        db (Session): PostgreSQL session

    Returns:
        dict: {"status": "UP"} veya {"status": "DOWN", "error": "..."}
    """
    try:
        # Basit bir sorgu ile bağlantıyı test et
        # Java'da da benzer bir kontrol yapılabilir
        db.execute(text("SELECT 1"))
        return {"status": "UP"}
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return {"status": "DOWN", "error": str(e)}


def check_snowflake_health() -> Dict[str, str]:
    """
    Snowflake bağlantısını kontrol eder.

    SELECT 1 sorgusu ile Snowflake'in erişilebilir olduğunu doğrular.

    Returns:
        dict: {"status": "UP"} veya {"status": "DOWN", "error": "..."}
    """
    try:
        with snowflake_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        return {"status": "UP"}
    except Exception as e:
        logger.error(f"Snowflake health check failed: {e}")
        return {"status": "DOWN", "error": str(e)}


# =============================================================================
# GET /actuator/health - Sistem Sağlık Kontrolü
# =============================================================================
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the health status of the application and its dependencies"
)
def health_check(db: Session = Depends(get_postgresql_db)):
    """
    Sistem sağlık kontrolü.

    Java Karşılığı:
        Spring Boot Actuator: GET /actuator/health

        Response:
        {
            "status": "UP",
            "components": {
                "db": {"status": "UP"},
                "diskSpace": {"status": "UP"}
            }
        }

    Bu endpoint:
    1. PostgreSQL bağlantısını kontrol eder
    2. Snowflake bağlantısını kontrol eder (opsiyonel)
    3. Genel durumu döner

    Args:
        db (Session): PostgreSQL session

    Returns:
        HealthResponse: Sağlık durumu
    """
    logger.info("GET /actuator/health - Checking system health")

    # Bileşen durumlarını kontrol et
    components = {
        "postgresql": check_postgresql_health(db)
    }

    # Snowflake kontrolü (opsiyonel - hata verse de UP olabilir)
    try:
        components["snowflake"] = check_snowflake_health()
    except Exception:
        components["snowflake"] = {"status": "UNKNOWN", "error": "Could not check"}

    # Genel durum - herhangi biri DOWN ise genel de DOWN
    overall_status = "UP"
    for component_name, component_status in components.items():
        if component_status.get("status") == "DOWN":
            overall_status = "DOWN"
            break

    logger.info(f"Health check result: {overall_status}")

    return HealthResponse(
        status=overall_status,
        components=components
    )


# =============================================================================
# GET /actuator/info - Uygulama Bilgileri
# =============================================================================
@router.get(
    "/info",
    response_model=InfoResponse,
    summary="Application Info",
    description="Returns information about the application"
)
def application_info():
    """
    Uygulama bilgilerini döner.

    Java Karşılığı:
        Spring Boot Actuator: GET /actuator/info

        Response:
        {
            "app": {
                "name": "Patient Management API",
                "version": "1.0.0",
                "description": "..."
            }
        }

    Returns:
        InfoResponse: Uygulama bilgileri
    """
    logger.info("GET /actuator/info - Returning application info")

    return InfoResponse(
        app={
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "Patient Management API - Snowflake to PostgreSQL ETL",
            "python_version": "3.11+",
            "framework": "FastAPI"
        }
    )


# =============================================================================
# GET /actuator/health/liveness - Kubernetes Liveness Probe
# =============================================================================
@router.get(
    "/health/liveness",
    summary="Liveness Probe",
    description="Simple liveness check for Kubernetes"
)
def liveness_probe():
    """
    Kubernetes liveness probe için basit endpoint.

    Liveness Probe Nedir?
    --------------------
    Kubernetes, container'ın "yaşayıp yaşamadığını" kontrol eder.
    Eğer bu endpoint başarısız olursa, Kubernetes container'ı yeniden başlatır.

    Bu endpoint sadece uygulamanın ayakta olduğunu doğrular.
    Veritabanı bağlantısı kontrolü yapmaz (o readiness için).

    Returns:
        dict: {"status": "UP"}
    """
    return {"status": "UP"}


# =============================================================================
# GET /actuator/health/readiness - Kubernetes Readiness Probe
# =============================================================================
@router.get(
    "/health/readiness",
    summary="Readiness Probe",
    description="Readiness check for Kubernetes - checks database connectivity"
)
def readiness_probe(db: Session = Depends(get_postgresql_db)):
    """
    Kubernetes readiness probe için endpoint.

    Readiness Probe Nedir?
    ---------------------
    Kubernetes, container'ın "trafiği alıp alamayacağını" kontrol eder.
    Eğer bu endpoint başarısız olursa, Kubernetes bu pod'a trafik yönlendirmez.

    Bu endpoint veritabanı bağlantısını da kontrol eder.

    Args:
        db (Session): PostgreSQL session

    Returns:
        dict: {"status": "UP"} veya {"status": "DOWN"}
    """
    pg_health = check_postgresql_health(db)

    if pg_health.get("status") == "UP":
        return {"status": "UP"}
    else:
        # Bağlantı hatası varsa 503 döner
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready"
        )
