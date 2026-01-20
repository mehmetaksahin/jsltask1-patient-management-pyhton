"""
Patient Schemas - Pydantic DTO'ları

Bu dosya API request ve response modellerini tanımlar.
Pydantic ile otomatik validasyon ve serialization sağlanır.

Java Karşılaştırması:
--------------------
Java'da DTO sınıfları ve validation annotation'ları kullanılır:

    public class PatientRequest {
        @NotBlank(message = "Name is required")
        private String name;

        @NotBlank(message = "Surname is required")
        private String surname;

        @NotBlank(message = "Disease name is required")
        private String diseaseName;
    }

Python'da Pydantic modelleri kullanılır:

    class PatientRequest(BaseModel):
        name: str = Field(..., min_length=1)
        surname: str = Field(..., min_length=1)
        disease_name: str = Field(..., min_length=1)

Pydantic Avantajları:
--------------------
1. Otomatik tip kontrolü (runtime'da)
2. Otomatik JSON serialization/deserialization
3. OpenAPI/Swagger dokümantasyonu otomatik oluşturulur
4. Validation hataları otomatik HTTP 422 response'a dönüşür

Field() Parametreleri:
---------------------
- ... (Ellipsis): Zorunlu alan (Java'daki @NotNull)
- default: Varsayılan değer
- min_length: Minimum uzunluk (Java'daki @Size(min=...))
- max_length: Maximum uzunluk (Java'daki @Size(max=...))
- description: Alan açıklaması (Swagger'da görünür)
- example: Örnek değer (Swagger'da görünür)
"""

from pydantic import BaseModel, Field
from typing import Optional


class PatientRequest(BaseModel):
    """
    Hasta oluşturma isteği için şema.

    Java'daki PatientRequest.java DTO'suna karşılık gelir.

    POST /api/patients endpoint'i bu şemayı kullanır.

    Örnek JSON:
        {
            "name": "John",
            "surname": "Doe",
            "disease_name": "Hypertension"
        }
    """

    # Java'daki @NotBlank karşılığı: Field(..., min_length=1)
    # ... (Ellipsis) = zorunlu alan
    # min_length=1 = boş olamaz
    name: str = Field(
        ...,  # Zorunlu alan
        min_length=1,
        max_length=100,
        description="Hasta adı",
        examples=["John"]
    )

    surname: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Hasta soyadı",
        examples=["Doe"]
    )

    # JSON'da snake_case kullanıyoruz (disease_name)
    # Java'daki diseaseName -> Python'da disease_name
    disease_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Hastalık adı",
        examples=["Hypertension"]
    )

    class Config:
        """
        Pydantic model konfigürasyonu.

        json_schema_extra: OpenAPI/Swagger için ek bilgiler
        """
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "disease_name": "Hypertension"
            }
        }


class PatientResponse(BaseModel):
    """
    Hasta response şeması.

    Java'da genellikle Entity sınıfı doğrudan döndürülür,
    ama Python'da response için ayrı şema kullanmak best practice'dir.

    Bu şema:
    1. API'nin döneceği verileri tanımlar
    2. Hangi alanların döneceğini kontrol eder
    3. Swagger dokümantasyonunu oluşturur

    Örnek Response:
        {
            "id": 1,
            "name": "John",
            "surname": "Doe",
            "disease_name": "Hypertension"
        }
    """

    id: int = Field(..., description="Hasta ID'si")
    name: str = Field(..., description="Hasta adı")
    surname: str = Field(..., description="Hasta soyadı")
    disease_name: str = Field(..., description="Hastalık adı")

    class Config:
        """
        from_attributes: SQLAlchemy modelinden otomatik dönüşüm sağlar.

        Java'da Jackson'ın @JsonProperty ile yaptığı işe benzer.
        ORM nesnesini doğrudan Pydantic modeline dönüştürür.

        Kullanım:
            patient_entity = db.query(Patient).first()
            patient_response = PatientResponse.model_validate(patient_entity)
        """
        from_attributes = True  # SQLAlchemy modelden okumayı etkinleştirir


class MigrationResult(BaseModel):
    """
    ETL migration sonucu şeması.

    Java'daki MigrationResult record'una karşılık gelir:
        public record MigrationResult(
            int successCount,
            int failureCount,
            String message
        ) {}

    POST /api/patients/migrate endpoint'i bu şemayı döndürür.

    Örnek Response:
        {
            "success_count": 10,
            "failure_count": 0,
            "message": "Migration completed successfully",
            "total_processed": 10,
            "is_successful": true
        }
    """

    success_count: int = Field(
        ...,
        ge=0,  # >= 0 (greater than or equal)
        description="Başarıyla migrate edilen kayıt sayısı"
    )

    failure_count: int = Field(
        ...,
        ge=0,
        description="Başarısız olan kayıt sayısı"
    )

    message: str = Field(
        ...,
        description="İşlem sonuç mesajı"
    )

    @property
    def total_processed(self) -> int:
        """
        Toplam işlenen kayıt sayısı.

        Java'daki totalProcessed() metoduna karşılık gelir.

        Returns:
            int: success_count + failure_count
        """
        return self.success_count + self.failure_count

    @property
    def is_successful(self) -> bool:
        """
        Migration başarılı mı kontrol eder.

        Java'daki isSuccessful() metoduna karşılık gelir.

        Returns:
            bool: Hata yoksa ve en az bir kayıt varsa True
        """
        return self.failure_count == 0 and self.success_count > 0

    class Config:
        json_schema_extra = {
            "example": {
                "success_count": 10,
                "failure_count": 0,
                "message": "Migration completed successfully"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response şeması.

    Spring Boot Actuator'ın /actuator/health endpoint'ine karşılık gelir.

    Örnek Response:
        {
            "status": "UP",
            "components": {
                "postgresql": {"status": "UP"},
                "snowflake": {"status": "UP"}
            }
        }
    """

    status: str = Field(..., description="Genel sistem durumu (UP/DOWN)")
    components: Optional[dict] = Field(
        default=None,
        description="Bileşen durumları"
    )


class InfoResponse(BaseModel):
    """
    Application info response şeması.

    Spring Boot Actuator'ın /actuator/info endpoint'ine karşılık gelir.

    Örnek Response:
        {
            "app": {
                "name": "Patient Management API",
                "version": "1.0.0"
            }
        }
    """

    app: dict = Field(..., description="Uygulama bilgileri")
