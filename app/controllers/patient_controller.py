"""
Patient Controller - REST API Endpoint'leri

Bu dosya hasta yönetimi için REST API endpoint'lerini tanımlar.

Java Karşılaştırması:
--------------------
Java (PatientController.java):

    @RestController
    @RequestMapping("/api/patients")
    public class PatientController {

        @Autowired
        private PatientService patientService;

        @Autowired
        private PatientMigrationService migrationService;

        @GetMapping
        public ResponseEntity<List<Patient>> getAllPatients() {
            return ResponseEntity.ok(patientService.getAllPatients());
        }

        @GetMapping("/{id}")
        public ResponseEntity<Patient> getPatientById(@PathVariable Long id) {
            return patientService.getPatientById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
        }

        @PostMapping
        public ResponseEntity<Patient> createPatient(@Valid @RequestBody PatientRequest request) {
            Patient patient = patientService.createPatient(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(patient);
        }

        @PostMapping("/migrate")
        public ResponseEntity<MigrationResult> migrateFromSnowflake() {
            MigrationResult result = migrationService.migrateFromSnowflakeToPostgresql();
            if (result.isSuccessful()) {
                return ResponseEntity.ok(result);
            } else if (result.getSuccessCount() > 0) {
                return ResponseEntity.status(HttpStatus.PARTIAL_CONTENT).body(result);
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(result);
            }
        }
    }

FastAPI Routing:
---------------
FastAPI'de routing @app.get(), @app.post() decorator'ları ile yapılır.
Veya APIRouter kullanarak modüler routing yapılabilir.

APIRouter Nedir?
---------------
Java'daki @RequestMapping("/api/patients") gibi bir prefix tanımlar.
Birden fazla router'ı ana uygulamaya ekleyebilirsin.

Dependency Injection:
--------------------
FastAPI'de Depends() kullanılır.
Java'daki @Autowired'a karşılık gelir.

HTTP Status Kodları:
-------------------
- 200 OK: Başarılı GET/POST
- 201 Created: Başarılı oluşturma
- 206 Partial Content: Kısmen başarılı (migration)
- 404 Not Found: Kaynak bulunamadı
- 422 Unprocessable Entity: Validation hatası
- 500 Internal Server Error: Sunucu hatası
"""

from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_postgresql_db
from app.schemas.patient import (
    PatientRequest,
    PatientResponse,
    MigrationResult
)
from app.services.patient_service import patient_service
from app.services.migration_service import migration_service

# Logger
logger = logging.getLogger(__name__)

# Router oluştur - Java'daki @RequestMapping("/api/patients") karşılığı
# prefix: Tüm endpoint'lerin önüne eklenir
# tags: Swagger UI'da gruplandırma için kullanılır
router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"]  # Swagger'da kategori adı
)


# =============================================================================
# GET /api/patients - Tüm hastaları listele
# =============================================================================
@router.get(
    "",
    response_model=List[PatientResponse],
    summary="Get All Patients",
    description="Retrieves all patients from PostgreSQL database"
)
def get_all_patients(db: Session = Depends(get_postgresql_db)):
    """
    Tüm hastaları getirir.

    Java Karşılığı:
        @GetMapping
        public ResponseEntity<List<Patient>> getAllPatients() {
            return ResponseEntity.ok(patientService.getAllPatients());
        }

    FastAPI Detayları:
    -----------------
    - @router.get("") : GET /api/patients endpoint'i tanımlar
    - response_model: Response'un şemasını belirtir (Swagger için)
    - Depends(get_postgresql_db): Session dependency injection

    Args:
        db (Session): PostgreSQL session (otomatik inject edilir)

    Returns:
        List[PatientResponse]: Hasta listesi (HTTP 200)
    """
    logger.info("GET /api/patients - Fetching all patients")
    patients = patient_service.get_all_patients(db)
    return patients


# =============================================================================
# GET /api/patients/migrate-get - Tarayıcıdan migration tetikleme
# =============================================================================
# NOT: Bu endpoint /{patient_id}'den ÖNCE tanımlanmalı!
# Aksi halde FastAPI "migrate-get" string'ini patient_id olarak parse etmeye çalışır.
@router.get(
    "/migrate-get",
    response_model=MigrationResult,
    summary="Migrate from Snowflake (GET)",
    description="Same as POST /migrate but accessible via browser GET request"
)
def migrate_from_snowflake_get(db: Session = Depends(get_postgresql_db)):
    """
    Tarayıcıdan migration tetiklemek için GET endpoint.

    POST /migrate ile aynı işlemi yapar, sadece GET method kullanır.
    Trial hesaplarda Postman kullanılamadığı için tarayıcıdan erişim sağlar.
    """
    logger.info("GET /api/patients/migrate-get - Starting migration (browser trigger)")

    result = migration_service.migrate_from_snowflake_to_postgresql(db)

    if result.is_successful:
        logger.info(f"Migration successful: {result.success_count} patients migrated")
        return result
    elif result.success_count > 0:
        logger.warning(
            f"Migration partially successful: "
            f"{result.success_count} succeeded, {result.failure_count} failed"
        )
        return result
    else:
        logger.error(f"Migration failed: {result.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message
        )


# =============================================================================
# GET /api/patients/{id} - ID'ye göre hasta getir
# =============================================================================
@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get Patient by ID",
    description="Retrieves a specific patient by their ID"
)
def get_patient_by_id(
    patient_id: int,  # Path parameter - Java'daki @PathVariable
    db: Session = Depends(get_postgresql_db)
):
    """
    ID'ye göre hasta getirir.

    Java Karşılığı:
        @GetMapping("/{id}")
        public ResponseEntity<Patient> getPatientById(@PathVariable Long id) {
            return patientService.getPatientById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
        }

    FastAPI Detayları:
    -----------------
    - /{patient_id} : URL'deki değer otomatik olarak patient_id parametresine atanır
    - HTTPException(404): Java'daki ResponseEntity.notFound() karşılığı

    Args:
        patient_id (int): Hasta ID'si (URL'den alınır)
        db (Session): PostgreSQL session

    Returns:
        PatientResponse: Bulunan hasta (HTTP 200)

    Raises:
        HTTPException(404): Hasta bulunamazsa
    """
    logger.info(f"GET /api/patients/{patient_id} - Fetching patient")

    patient = patient_service.get_patient_by_id(db, patient_id)

    if patient is None:
        # Java: return ResponseEntity.notFound().build();
        logger.warning(f"Patient not found: {patient_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found"
        )

    return patient


# =============================================================================
# POST /api/patients - Yeni hasta oluştur
# =============================================================================
@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,  # Başarılı oluşturma kodu
    summary="Create Patient",
    description="Creates a new patient record"
)
def create_patient(
    request: PatientRequest,  # Request body - Java'daki @RequestBody
    db: Session = Depends(get_postgresql_db)
):
    """
    Yeni hasta oluşturur.

    Java Karşılığı:
        @PostMapping
        public ResponseEntity<Patient> createPatient(
            @Valid @RequestBody PatientRequest request
        ) {
            Patient patient = patientService.createPatient(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(patient);
        }

    FastAPI Detayları:
    -----------------
    - request: PatientRequest -> @RequestBody @Valid otomatik karşılığı
    - Pydantic validation otomatik yapılır (422 hatası döner)
    - status_code=201: Java'daki HttpStatus.CREATED

    Request Body Örneği:
        {
            "name": "John",
            "surname": "Doe",
            "disease_name": "Hypertension"
        }

    Args:
        request (PatientRequest): Hasta oluşturma isteği
        db (Session): PostgreSQL session

    Returns:
        PatientResponse: Oluşturulan hasta (HTTP 201)
    """
    logger.info(f"POST /api/patients - Creating patient: {request.name} {request.surname}")

    patient = patient_service.create_patient(db, request)

    logger.info(f"Patient created with id: {patient.id}")
    return patient


# =============================================================================
# POST /api/patients/migrate - Snowflake'den PostgreSQL'e migration
# =============================================================================
@router.post(
    "/migrate",
    response_model=MigrationResult,
    summary="Migrate from Snowflake",
    description="Migrates patient data from Snowflake to PostgreSQL with timestamp transformation"
)
def migrate_from_snowflake(db: Session = Depends(get_postgresql_db)):
    """
    Snowflake'den PostgreSQL'e veri aktarımı yapar.

    Java Karşılığı:
        @PostMapping("/migrate")
        public ResponseEntity<MigrationResult> migrateFromSnowflake() {
            MigrationResult result = migrationService.migrateFromSnowflakeToPostgresql();
            if (result.isSuccessful()) {
                return ResponseEntity.ok(result);
            } else if (result.getSuccessCount() > 0) {
                return ResponseEntity.status(HttpStatus.PARTIAL_CONTENT).body(result);
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(result);
            }
        }

    ETL Süreci:
    ----------
    1. Snowflake'den tüm hastaları oku
    2. Her alana timestamp ekle
    3. PostgreSQL'e kaydet

    HTTP Status Kodları:
    -------------------
    - 200 OK: Tamamen başarılı
    - 206 Partial Content: Kısmen başarılı
    - 500 Internal Server Error: Tamamen başarısız

    Args:
        db (Session): PostgreSQL session

    Returns:
        MigrationResult: İşlem sonucu

    Raises:
        HTTPException(500): Tamamen başarısız olursa
    """
    logger.info("POST /api/patients/migrate - Starting migration")

    result = migration_service.migrate_from_snowflake_to_postgresql(db)

    # Status kodu belirleme - Java'daki if-else ile aynı mantık
    if result.is_successful:
        # Tamamen başarılı
        logger.info(f"Migration successful: {result.success_count} patients migrated")
        return result

    elif result.success_count > 0:
        # Kısmen başarılı - HTTP 206 Partial Content
        logger.warning(
            f"Migration partially successful: "
            f"{result.success_count} succeeded, {result.failure_count} failed"
        )
        # FastAPI'de custom status code döndürmek için Response kullanılabilir
        # Ama basitlik için result'ı dönüyoruz
        return result

    else:
        # Tamamen başarısız
        logger.error(f"Migration failed: {result.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message
        )
