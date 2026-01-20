"""
Patient Repository - PostgreSQL Veritabanı Erişim Katmanı

Bu dosya PostgreSQL veritabanı üzerinde CRUD işlemlerini gerçekleştirir.

Java Karşılaştırması:
--------------------
Java'da Spring Data JPA otomatik repository sağlar:

    public interface PatientRepository extends JpaRepository<Patient, Long> {
        List<Patient> findByName(String name);
        List<Patient> findBySurname(String surname);
    }

Python'da bu metodları manuel yazmamız gerekir:

    class PatientRepository:
        def find_all(self, db: Session) -> List[Patient]:
            return db.query(Patient).all()

        def find_by_name(self, db: Session, name: str) -> List[Patient]:
            return db.query(Patient).filter(Patient.name == name).all()

Neden Manuel?
-------------
Python'da Spring Data JPA gibi otomatik query generation yok.
SQLAlchemy ile sorguları kendimiz yazıyoruz.
Ama bu daha fazla kontrol sağlar ve anlaşılması kolay.

SQLAlchemy Query Syntax:
-----------------------
db.query(Model)           → SELECT * FROM model
    .filter(...)          → WHERE ...
    .order_by(...)        → ORDER BY ...
    .first()              → LIMIT 1 (tek kayıt)
    .all()                → Tüm sonuçlar (liste)
    .count()              → COUNT(*)
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.patient import Patient


class PatientRepository:
    """
    PostgreSQL Patient repository sınıfı.

    Java'daki PatientRepository interface'ine karşılık gelir,
    ama burada interface yerine concrete class kullanıyoruz.

    CRUD İşlemleri:
    - Create: save()
    - Read: find_all(), find_by_id()
    - Update: save() (mevcut kayıt için)
    - Delete: delete()
    """

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    def save(self, db: Session, patient: Patient) -> Patient:
        """
        Hasta kaydını veritabanına kaydeder.

        Java Karşılığı:
            patientRepository.save(patient);

        SQL Karşılığı:
            INSERT INTO tbl_patient (name, surname, disease_name)
            VALUES (?, ?, ?)
            RETURNING id;

        Args:
            db (Session): SQLAlchemy session (Java'daki EntityManager)
            patient (Patient): Kaydedilecek hasta nesnesi

        Returns:
            Patient: Kaydedilen hasta (id atanmış hali)

        Not:
            - Eğer patient.id None ise INSERT yapılır
            - Eğer patient.id varsa UPDATE yapılır (merge)
        """
        db.add(patient)  # Session'a ekle (Java'daki persist)
        db.commit()  # Transaction'ı commit et
        db.refresh(patient)  # Veritabanından güncel veriyi al (id dahil)
        return patient

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    def find_all(self, db: Session) -> List[Patient]:
        """
        Tüm hastaları getirir.

        Java Karşılığı:
            patientRepository.findAll();

        SQL Karşılığı:
            SELECT * FROM tbl_patient;

        Args:
            db (Session): SQLAlchemy session

        Returns:
            List[Patient]: Tüm hasta kayıtları
        """
        return db.query(Patient).all()

    def find_by_id(self, db: Session, patient_id: int) -> Optional[Patient]:
        """
        ID'ye göre hasta getirir.

        Java Karşılığı:
            patientRepository.findById(id);  // Optional<Patient> döner

        SQL Karşılığı:
            SELECT * FROM tbl_patient WHERE id = ? LIMIT 1;

        Args:
            db (Session): SQLAlchemy session
            patient_id (int): Hasta ID'si

        Returns:
            Optional[Patient]: Bulunan hasta veya None

        Not:
            Java'daki Optional<Patient> yerine Python'da Optional[Patient] kullanılır
            (typing modülünden). None dönebileceğini belirtir.
        """
        return db.query(Patient).filter(Patient.id == patient_id).first()

    def find_by_name(self, db: Session, name: str) -> List[Patient]:
        """
        Ada göre hasta arar.

        Java Karşılığı:
            List<Patient> findByName(String name);

        SQL Karşılığı:
            SELECT * FROM tbl_patient WHERE name = ?;

        Args:
            db (Session): SQLAlchemy session
            name (str): Aranacak ad

        Returns:
            List[Patient]: Eşleşen hasta kayıtları
        """
        return db.query(Patient).filter(Patient.name == name).all()

    def find_by_surname(self, db: Session, surname: str) -> List[Patient]:
        """
        Soyadına göre hasta arar.

        Java Karşılığı:
            List<Patient> findBySurname(String surname);

        Args:
            db (Session): SQLAlchemy session
            surname (str): Aranacak soyad

        Returns:
            List[Patient]: Eşleşen hasta kayıtları
        """
        return db.query(Patient).filter(Patient.surname == surname).all()

    def find_by_disease_name(self, db: Session, disease_name: str) -> List[Patient]:
        """
        Hastalık adına göre hasta arar.

        Java Karşılığı:
            List<Patient> findByDiseaseName(String diseaseName);

        Args:
            db (Session): SQLAlchemy session
            disease_name (str): Aranacak hastalık adı

        Returns:
            List[Patient]: Eşleşen hasta kayıtları
        """
        return db.query(Patient).filter(Patient.disease_name == disease_name).all()

    def find_by_name_and_surname(
        self, db: Session, name: str, surname: str
    ) -> List[Patient]:
        """
        Ad ve soyadına göre hasta arar.

        Java Karşılığı:
            List<Patient> findByNameAndSurname(String name, String surname);

        SQL Karşılığı:
            SELECT * FROM tbl_patient WHERE name = ? AND surname = ?;

        Args:
            db (Session): SQLAlchemy session
            name (str): Aranacak ad
            surname (str): Aranacak soyad

        Returns:
            List[Patient]: Eşleşen hasta kayıtları
        """
        return (
            db.query(Patient)
            .filter(Patient.name == name, Patient.surname == surname)
            .all()
        )

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    def delete(self, db: Session, patient: Patient) -> None:
        """
        Hasta kaydını siler.

        Java Karşılığı:
            patientRepository.delete(patient);

        SQL Karşılığı:
            DELETE FROM tbl_patient WHERE id = ?;

        Args:
            db (Session): SQLAlchemy session
            patient (Patient): Silinecek hasta nesnesi
        """
        db.delete(patient)
        db.commit()

    def delete_by_id(self, db: Session, patient_id: int) -> bool:
        """
        ID'ye göre hasta siler.

        Java Karşılığı:
            patientRepository.deleteById(id);

        Args:
            db (Session): SQLAlchemy session
            patient_id (int): Silinecek hasta ID'si

        Returns:
            bool: Silme başarılı ise True, kayıt bulunamadıysa False
        """
        patient = self.find_by_id(db, patient_id)
        if patient:
            self.delete(db, patient)
            return True
        return False

    # =========================================================================
    # COUNT OPERATIONS
    # =========================================================================

    def count(self, db: Session) -> int:
        """
        Toplam hasta sayısını döner.

        Java Karşılığı:
            patientRepository.count();

        SQL Karşılığı:
            SELECT COUNT(*) FROM tbl_patient;

        Args:
            db (Session): SQLAlchemy session

        Returns:
            int: Toplam kayıt sayısı
        """
        return db.query(Patient).count()


# Singleton instance - Uygulama genelinde tek bir repository nesnesi
# Java'daki @Repository @Autowired pattern'ine benzer
patient_repository = PatientRepository()
