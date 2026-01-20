"""
Patient Service - İş Mantığı Katmanı

Bu dosya hasta işlemleri için iş mantığını içerir.

Java Karşılaştırması:
--------------------
Java'da @Service annotation'ı ile işaretlenir:

    @Service
    public class PatientService {
        @Autowired
        private PatientRepository patientRepository;

        @Transactional(readOnly = true)
        public List<Patient> getAllPatients() {
            return patientRepository.findAll();
        }

        @Transactional
        public Patient createPatient(PatientRequest request) {
            Patient patient = Patient.builder()
                .name(request.getName())
                .surname(request.getSurname())
                .diseaseName(request.getDiseaseName())
                .build();
            return patientRepository.save(patient);
        }
    }

Python'da karşılığı:

    class PatientService:
        def __init__(self):
            self.repository = patient_repository

        def get_all_patients(self, db: Session) -> List[Patient]:
            return self.repository.find_all(db)

        def create_patient(self, db: Session, request: PatientRequest) -> Patient:
            patient = Patient(
                name=request.name,
                surname=request.surname,
                disease_name=request.disease_name
            )
            return self.repository.save(db, patient)

Transaction Yönetimi:
--------------------
Java'da @Transactional annotation'ı kullanılır.
Python/FastAPI'de transaction yönetimi Session üzerinden yapılır:
- Her request için yeni session
- db.commit() ile transaction tamamlanır
- Hata durumunda db.rollback() ile geri alınır

Service Katmanının Amacı:
------------------------
1. Controller'ı veritabanı detaylarından izole eder
2. İş kurallarını merkezi bir yerde toplar
3. Birden fazla repository'yi koordine edebilir
4. Unit test'ler için mocklanabilir
"""

from typing import List, Optional
import logging

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientRequest
from app.repositories.patient_repository import patient_repository

# Logger (Java'daki SLF4J Logger)
logger = logging.getLogger(__name__)


class PatientService:
    """
    Patient iş mantığı servisi.

    Java'daki PatientService sınıfına karşılık gelir.

    Sorumlulukları:
    - CRUD işlemleri için iş mantığı
    - Validasyon (ek kurallar varsa)
    - Loglama
    - Exception handling
    """

    def __init__(self):
        """
        Constructor - Repository dependency injection.

        Java'da @Autowired ile yapılır:
            @Autowired
            private PatientRepository patientRepository;

        Python'da constructor'da yapıyoruz:
            self.repository = patient_repository
        """
        self.repository = patient_repository

    def get_all_patients(self, db: Session) -> List[Patient]:
        """
        Tüm hastaları getirir.

        Java Karşılığı:
            @Transactional(readOnly = true)
            public List<Patient> getAllPatients() {
                return patientRepository.findAll();
            }

        Args:
            db (Session): Veritabanı session'ı

        Returns:
            List[Patient]: Tüm hasta kayıtları
        """
        logger.info("Fetching all patients from PostgreSQL")
        patients = self.repository.find_all(db)
        logger.info(f"Found {len(patients)} patients")
        return patients

    def get_patient_by_id(self, db: Session, patient_id: int) -> Optional[Patient]:
        """
        ID'ye göre hasta getirir.

        Java Karşılığı:
            @Transactional(readOnly = true)
            public Optional<Patient> getPatientById(Long id) {
                return patientRepository.findById(id);
            }

        Args:
            db (Session): Veritabanı session'ı
            patient_id (int): Hasta ID'si

        Returns:
            Optional[Patient]: Bulunan hasta veya None
        """
        logger.info(f"Fetching patient with id: {patient_id}")
        patient = self.repository.find_by_id(db, patient_id)

        if patient:
            logger.info(f"Found patient: {patient}")
        else:
            logger.warning(f"Patient not found with id: {patient_id}")

        return patient

    def create_patient(self, db: Session, request: PatientRequest) -> Patient:
        """
        Yeni hasta oluşturur.

        Java Karşılığı:
            @Transactional
            public Patient createPatient(PatientRequest request) {
                Patient patient = Patient.builder()
                    .name(request.getName())
                    .surname(request.getSurname())
                    .diseaseName(request.getDiseaseName())
                    .build();
                return patientRepository.save(patient);
            }

        Args:
            db (Session): Veritabanı session'ı
            request (PatientRequest): Hasta oluşturma isteği

        Returns:
            Patient: Oluşturulan hasta (id atanmış)
        """
        logger.info(f"Creating new patient: {request.name} {request.surname}")

        # DTO'dan Entity'ye dönüşüm
        # Java'daki Builder pattern yerine doğrudan constructor
        patient = Patient(
            name=request.name,
            surname=request.surname,
            disease_name=request.disease_name
        )

        # Veritabanına kaydet
        saved_patient = self.repository.save(db, patient)

        logger.info(f"Created patient with id: {saved_patient.id}")
        return saved_patient

    def delete_patient(self, db: Session, patient_id: int) -> bool:
        """
        Hasta kaydını siler.

        Java Karşılığı:
            @Transactional
            public void deletePatient(Long id) {
                patientRepository.deleteById(id);
            }

        Args:
            db (Session): Veritabanı session'ı
            patient_id (int): Silinecek hasta ID'si

        Returns:
            bool: Silme başarılı ise True
        """
        logger.info(f"Deleting patient with id: {patient_id}")
        result = self.repository.delete_by_id(db, patient_id)

        if result:
            logger.info(f"Patient deleted successfully: {patient_id}")
        else:
            logger.warning(f"Patient not found for deletion: {patient_id}")

        return result

    def get_patients_by_disease(self, db: Session, disease_name: str) -> List[Patient]:
        """
        Hastalık adına göre hastaları getirir.

        Java Karşılığı:
            @Transactional(readOnly = true)
            public List<Patient> getPatientsByDisease(String diseaseName) {
                return patientRepository.findByDiseaseName(diseaseName);
            }

        Args:
            db (Session): Veritabanı session'ı
            disease_name (str): Hastalık adı

        Returns:
            List[Patient]: Eşleşen hasta kayıtları
        """
        logger.info(f"Fetching patients with disease: {disease_name}")
        return self.repository.find_by_disease_name(db, disease_name)


# Singleton instance - Uygulama genelinde tek bir service nesnesi
# Java'daki @Service @Autowired pattern'ine benzer
patient_service = PatientService()
