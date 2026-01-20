"""
Snowflake Repository - Snowflake Veritabanı Erişim Katmanı

Bu dosya Snowflake veritabanından veri okuma işlemlerini gerçekleştirir.

Java Karşılaştırması:
--------------------
Java'da JPA Repository kullanılır:

    public interface SnowflakePatientRepository extends JpaRepository<SnowflakePatient, Long> {
        List<SnowflakePatient> findByName(String name);
    }

Python'da native Snowflake connector kullanıyoruz:

    class SnowflakeRepository:
        def find_all(self) -> List[SnowflakePatient]:
            with snowflake_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM TBL_PATIENT")
                return [SnowflakePatient.from_row(row) for row in cursor.fetchall()]

Neden Native Connector?
----------------------
1. Snowflake'in SQLAlchemy desteği tam değil
2. JPA özellikleri (lazy loading vb.) Snowflake'de sorun çıkarabilir
3. Native connector daha hızlı ve güvenilir
4. Sadece SELECT yapacağız, JPA'nın gelişmiş özellikleri gerekmez

Snowflake SQL Notları:
---------------------
- Tablo ve sütun adları BÜYÜK HARF: TBL_PATIENT, NAME, SURNAME
- Snowflake büyük/küçük harf duyarlıdır (çift tırnak kullanılmadığında büyük harfe çevirir)
"""

from typing import List, Optional
import logging

from app.config.database import snowflake_session
from app.models.snowflake_patient import SnowflakePatient

# Logger oluştur (Java'daki SLF4J Logger'a karşılık gelir)
# Java: private static final Logger logger = LoggerFactory.getLogger(SnowflakeRepository.class);
logger = logging.getLogger(__name__)


class SnowflakeRepository:
    """
    Snowflake Patient repository sınıfı.

    Java'daki SnowflakePatientRepository interface'ine karşılık gelir.

    NOT: Bu repository sadece READ işlemleri yapar.
    ETL sürecinde Snowflake'den veri okuyoruz, yazmıyoruz.
    """

    # Tablo adı sabiti
    TABLE_NAME = "TBL_PATIENT"

    def find_all(self) -> List[SnowflakePatient]:
        """
        Tüm hastaları Snowflake'den getirir.

        Java Karşılığı:
            snowflakePatientRepository.findAll();

        SQL:
            SELECT ID, NAME, SURNAME, DISEASE_NAME FROM TBL_PATIENT;

        Returns:
            List[SnowflakePatient]: Tüm hasta kayıtları

        Raises:
            Exception: Snowflake bağlantı hatası durumunda
        """
        patients = []

        # with ifadesi: Java'daki try-with-resources gibi
        # Bağlantı otomatik olarak kapatılır
        with snowflake_session() as conn:
            cursor = conn.cursor()
            try:
                # SQL sorgusu çalıştır
                query = f"SELECT ID, NAME, SURNAME, DISEASE_NAME FROM {self.TABLE_NAME}"
                logger.info(f"Executing Snowflake query: {query}")

                cursor.execute(query)

                # Tüm sonuçları al ve SnowflakePatient nesnelerine dönüştür
                # Java'daki stream().map() işlemine benzer:
                # results.stream().map(row -> SnowflakePatient.fromRow(row)).collect(toList())
                rows = cursor.fetchall()

                for row in rows:
                    patient = SnowflakePatient.from_row(row)
                    patients.append(patient)

                logger.info(f"Found {len(patients)} patients in Snowflake")

            except Exception as e:
                logger.error(f"Error fetching patients from Snowflake: {e}")
                raise
            finally:
                cursor.close()

        return patients

    def find_by_id(self, patient_id: int) -> Optional[SnowflakePatient]:
        """
        ID'ye göre hasta getirir.

        Java Karşılığı:
            snowflakePatientRepository.findById(id);

        SQL:
            SELECT ID, NAME, SURNAME, DISEASE_NAME FROM TBL_PATIENT WHERE ID = ?;

        Args:
            patient_id (int): Hasta ID'si

        Returns:
            Optional[SnowflakePatient]: Bulunan hasta veya None
        """
        with snowflake_session() as conn:
            cursor = conn.cursor()
            try:
                query = f"""
                    SELECT ID, NAME, SURNAME, DISEASE_NAME
                    FROM {self.TABLE_NAME}
                    WHERE ID = %s
                """
                cursor.execute(query, (patient_id,))
                row = cursor.fetchone()

                if row:
                    return SnowflakePatient.from_row(row)
                return None

            except Exception as e:
                logger.error(f"Error fetching patient by ID from Snowflake: {e}")
                raise
            finally:
                cursor.close()

    def find_by_name(self, name: str) -> List[SnowflakePatient]:
        """
        Ada göre hasta arar.

        Java Karşılığı:
            List<SnowflakePatient> findByName(String name);

        SQL:
            SELECT * FROM TBL_PATIENT WHERE NAME = ?;

        Args:
            name (str): Aranacak ad

        Returns:
            List[SnowflakePatient]: Eşleşen hasta kayıtları
        """
        patients = []

        with snowflake_session() as conn:
            cursor = conn.cursor()
            try:
                query = f"""
                    SELECT ID, NAME, SURNAME, DISEASE_NAME
                    FROM {self.TABLE_NAME}
                    WHERE NAME = %s
                """
                cursor.execute(query, (name,))

                for row in cursor.fetchall():
                    patients.append(SnowflakePatient.from_row(row))

            except Exception as e:
                logger.error(f"Error fetching patients by name from Snowflake: {e}")
                raise
            finally:
                cursor.close()

        return patients

    def find_by_surname(self, surname: str) -> List[SnowflakePatient]:
        """
        Soyadına göre hasta arar.

        Java Karşılığı:
            List<SnowflakePatient> findBySurname(String surname);

        Args:
            surname (str): Aranacak soyad

        Returns:
            List[SnowflakePatient]: Eşleşen hasta kayıtları
        """
        patients = []

        with snowflake_session() as conn:
            cursor = conn.cursor()
            try:
                query = f"""
                    SELECT ID, NAME, SURNAME, DISEASE_NAME
                    FROM {self.TABLE_NAME}
                    WHERE SURNAME = %s
                """
                cursor.execute(query, (surname,))

                for row in cursor.fetchall():
                    patients.append(SnowflakePatient.from_row(row))

            except Exception as e:
                logger.error(f"Error fetching patients by surname from Snowflake: {e}")
                raise
            finally:
                cursor.close()

        return patients

    def find_by_disease_name(self, disease_name: str) -> List[SnowflakePatient]:
        """
        Hastalık adına göre hasta arar.

        Java Karşılığı:
            List<SnowflakePatient> findByDiseaseName(String diseaseName);

        Args:
            disease_name (str): Aranacak hastalık adı

        Returns:
            List[SnowflakePatient]: Eşleşen hasta kayıtları
        """
        patients = []

        with snowflake_session() as conn:
            cursor = conn.cursor()
            try:
                query = f"""
                    SELECT ID, NAME, SURNAME, DISEASE_NAME
                    FROM {self.TABLE_NAME}
                    WHERE DISEASE_NAME = %s
                """
                cursor.execute(query, (disease_name,))

                for row in cursor.fetchall():
                    patients.append(SnowflakePatient.from_row(row))

            except Exception as e:
                logger.error(f"Error fetching patients by disease from Snowflake: {e}")
                raise
            finally:
                cursor.close()

        return patients

    def count(self) -> int:
        """
        Toplam hasta sayısını döner.

        Java Karşılığı:
            snowflakePatientRepository.count();

        SQL:
            SELECT COUNT(*) FROM TBL_PATIENT;

        Returns:
            int: Toplam kayıt sayısı
        """
        with snowflake_session() as conn:
            cursor = conn.cursor()
            try:
                query = f"SELECT COUNT(*) FROM {self.TABLE_NAME}"
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0

            except Exception as e:
                logger.error(f"Error counting patients in Snowflake: {e}")
                raise
            finally:
                cursor.close()


# Singleton instance
snowflake_repository = SnowflakeRepository()
