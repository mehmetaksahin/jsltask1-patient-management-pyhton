"""
Patient Migration Service - ETL İş Mantığı

Bu dosya Snowflake'den PostgreSQL'e veri aktarımı (ETL) işlemlerini gerçekleştirir.

Java Karşılaştırması:
--------------------
Java (PatientMigrationService.java):

    @Service
    public class PatientMigrationService {
        @Autowired
        private SnowflakePatientRepository snowflakePatientRepository;
        @Autowired
        private PatientRepository patientRepository;

        private static final DateTimeFormatter DATE_TIME_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        public MigrationResult migrateFromSnowflakeToPostgresql() {
            List<SnowflakePatient> snowflakePatients = snowflakePatientRepository.findAll();
            String timestamp = LocalDateTime.now().format(DATE_TIME_FORMATTER);

            int successCount = 0;
            int failureCount = 0;

            for (SnowflakePatient sp : snowflakePatients) {
                try {
                    Patient patient = transformPatient(sp, timestamp);
                    patientRepository.save(patient);
                    successCount++;
                } catch (Exception e) {
                    failureCount++;
                }
            }

            return new MigrationResult(successCount, failureCount, "Migration completed");
        }

        private Patient transformPatient(SnowflakePatient sp, String timestamp) {
            return Patient.builder()
                .name(appendTimestamp(sp.getName(), timestamp))
                .surname(appendTimestamp(sp.getSurname(), timestamp))
                .diseaseName(appendTimestamp(sp.getDiseaseName(), timestamp))
                .build();
        }

        private String appendTimestamp(String value, String timestamp) {
            if (value == null || value.isEmpty()) {
                return timestamp;
            }
            return value + " " + timestamp;
        }
    }

ETL Süreci:
----------
1. EXTRACT (Çıkar): Snowflake'den tüm hasta kayıtlarını oku
2. TRANSFORM (Dönüştür): Her alana timestamp ekle
3. LOAD (Yükle): PostgreSQL'e kaydet

Timestamp Dönüşümü Örneği:
-------------------------
Snowflake'den: "William", "Moore", "Osteoporosis"
PostgreSQL'e: "William 2026-01-20 10:30:45", "Moore 2026-01-20 10:30:45", "Osteoporosis 2026-01-20 10:30:45"
"""

from datetime import datetime
import logging
from typing import Tuple

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.snowflake_patient import SnowflakePatient
from app.schemas.patient import MigrationResult
from app.repositories.patient_repository import patient_repository
from app.repositories.snowflake_repository import snowflake_repository

# Logger (Java'daki SLF4J Logger)
logger = logging.getLogger(__name__)

# Tarih formatı - Java'daki DateTimeFormatter'a karşılık gelir
# Java: DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
# Python: "%Y-%m-%d %H:%M:%S"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class MigrationService:
    """
    Snowflake -> PostgreSQL ETL Migration Service.

    Java'daki PatientMigrationService sınıfına birebir karşılık gelir.

    ETL Akışı:
    1. Snowflake'den tüm hastaları oku (Extract)
    2. Her hasta için timestamp ekle (Transform)
    3. PostgreSQL'e kaydet (Load)
    4. Başarı/hata sayısını döndür

    Hata Yönetimi:
    - Her kayıt için ayrı try-catch
    - Bir kayıt başarısız olsa bile diğerleri devam eder
    - Toplam başarı ve hata sayısı raporlanır
    """

    def __init__(self):
        """
        Constructor - Repository dependency injection.

        Java'daki @Autowired ile yapılan injection'ın karşılığı.
        """
        self.snowflake_repo = snowflake_repository
        self.postgresql_repo = patient_repository

    def migrate_from_snowflake_to_postgresql(self, db: Session) -> MigrationResult:
        """
        Snowflake'den PostgreSQL'e veri aktarımı yapar.

        Java Karşılığı:
            public MigrationResult migrateFromSnowflakeToPostgresql()

        ETL Süreci:
        -----------
        1. EXTRACT: Snowflake'den tüm hastaları oku
        2. TRANSFORM: Her alana timestamp ekle
        3. LOAD: PostgreSQL'e kaydet

        Args:
            db (Session): PostgreSQL session

        Returns:
            MigrationResult: İşlem sonucu (success/failure counts)
        """
        logger.info("Starting migration from Snowflake to PostgreSQL...")

        # =================================================================
        # EXTRACT PHASE (Çıkarma Aşaması)
        # =================================================================
        # Java: List<SnowflakePatient> snowflakePatients = snowflakePatientRepository.findAll();
        logger.info("EXTRACT: Fetching patients from Snowflake...")

        try:
            snowflake_patients = self.snowflake_repo.find_all()
            logger.info(f"EXTRACT: Found {len(snowflake_patients)} patients in Snowflake")
        except Exception as e:
            logger.error(f"EXTRACT: Failed to fetch from Snowflake: {e}")
            return MigrationResult(
                success_count=0,
                failure_count=0,
                message=f"Failed to connect to Snowflake: {str(e)}"
            )

        if not snowflake_patients:
            logger.warning("EXTRACT: No patients found in Snowflake")
            return MigrationResult(
                success_count=0,
                failure_count=0,
                message="No patients found in Snowflake to migrate"
            )

        # =================================================================
        # TRANSFORM & LOAD PHASE (Dönüştürme ve Yükleme Aşaması)
        # =================================================================
        # Java: String timestamp = LocalDateTime.now().format(DATE_TIME_FORMATTER);
        current_timestamp = datetime.now().strftime(DATE_TIME_FORMAT)
        logger.info(f"TRANSFORM: Using timestamp: {current_timestamp}")

        success_count = 0
        failure_count = 0

        # Her hasta için dönüşüm ve kayıt
        # Java'daki for loop'a karşılık gelir
        for snowflake_patient in snowflake_patients:
            try:
                # TRANSFORM: Timestamp ekle
                # Java: Patient patient = transformPatient(sp, timestamp);
                transformed_patient = self._transform_patient(
                    snowflake_patient, current_timestamp
                )

                # LOAD: PostgreSQL'e kaydet
                # Java: patientRepository.save(patient);
                self.postgresql_repo.save(db, transformed_patient)

                success_count += 1
                logger.debug(
                    f"LOAD: Migrated patient: {snowflake_patient.name} {snowflake_patient.surname}"
                )

            except Exception as e:
                # Hata durumunda sayacı artır ve devam et
                # Java: catch (Exception e) { failureCount++; log.error(...); }
                failure_count += 1
                logger.error(
                    f"LOAD: Failed to migrate patient {snowflake_patient.id}: {e}"
                )

        # =================================================================
        # RESULT (Sonuç)
        # =================================================================
        message = self._build_result_message(success_count, failure_count)
        logger.info(f"Migration completed: {message}")

        return MigrationResult(
            success_count=success_count,
            failure_count=failure_count,
            message=message
        )

    def _transform_patient(
        self, snowflake_patient: SnowflakePatient, timestamp: str
    ) -> Patient:
        """
        Snowflake Patient'ı PostgreSQL Patient'a dönüştürür.

        Java Karşılığı:
            private Patient transformPatient(SnowflakePatient sp, String timestamp) {
                return Patient.builder()
                    .name(appendTimestamp(sp.getName(), timestamp))
                    .surname(appendTimestamp(sp.getSurname(), timestamp))
                    .diseaseName(appendTimestamp(sp.getDiseaseName(), timestamp))
                    .build();
            }

        Dönüşüm:
        - Her alanın sonuna timestamp eklenir
        - "William" -> "William 2026-01-20 10:30:45"

        Args:
            snowflake_patient (SnowflakePatient): Kaynak hasta
            timestamp (str): Eklenecek timestamp

        Returns:
            Patient: Dönüştürülmüş PostgreSQL Patient nesnesi
        """
        return Patient(
            # id atama - PostgreSQL auto-increment yapacak
            name=self._append_timestamp(snowflake_patient.name, timestamp),
            surname=self._append_timestamp(snowflake_patient.surname, timestamp),
            disease_name=self._append_timestamp(snowflake_patient.disease_name, timestamp)
        )

    def _append_timestamp(self, value: str, timestamp: str) -> str:
        """
        Değerin sonuna timestamp ekler.

        Java Karşılığı:
            private String appendTimestamp(String value, String timestamp) {
                if (value == null || value.isEmpty()) {
                    return timestamp;
                }
                return value + " " + timestamp;
            }

        Örnekler:
        - "William", "2026-01-20" -> "William 2026-01-20"
        - "", "2026-01-20" -> "2026-01-20"
        - None, "2026-01-20" -> "2026-01-20"

        Args:
            value (str): Orijinal değer
            timestamp (str): Eklenecek timestamp

        Returns:
            str: Timestamp eklenmiş değer
        """
        # None veya boş string kontrolü
        # Java: if (value == null || value.isEmpty())
        if not value or not value.strip():
            return timestamp

        # Değer + boşluk + timestamp
        # Java: return value + " " + timestamp;
        return f"{value} {timestamp}"

    def _build_result_message(self, success_count: int, failure_count: int) -> str:
        """
        Sonuç mesajını oluşturur.

        Java'daki MigrationResult message alanına karşılık gelir.

        Args:
            success_count (int): Başarılı kayıt sayısı
            failure_count (int): Başarısız kayıt sayısı

        Returns:
            str: Sonuç mesajı
        """
        total = success_count + failure_count

        if failure_count == 0 and success_count > 0:
            return f"Migration completed successfully. {success_count} patients migrated."
        elif success_count == 0 and failure_count > 0:
            return f"Migration failed completely. {failure_count} patients could not be migrated."
        elif success_count > 0 and failure_count > 0:
            return (
                f"Migration partially completed. "
                f"{success_count} succeeded, {failure_count} failed out of {total} total."
            )
        else:
            return "No patients to migrate."


# Singleton instance
migration_service = MigrationService()
