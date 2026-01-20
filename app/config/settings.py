"""
Uygulama Konfigürasyonu (Java'daki application.yml'a karşılık gelir)

Bu dosya tüm konfigürasyon değerlerini merkezi bir yerden yönetir.
Pydantic BaseSettings kullanarak:
- Environment değişkenlerinden otomatik okuma
- .env dosyasından okuma
- Tip kontrolü ve validasyon
- Default değer tanımlama

Java Karşılaştırması:
--------------------
Java (application.yml):
    datasource:
      postgresql:
        jdbc-url: jdbc:postgresql://localhost:5432/patient_db
        username: postgres

Python (settings.py):
    class Settings(BaseSettings):
        postgresql_host: str = "localhost"
        postgresql_port: int = 5432
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Uygulama ayarları sınıfı.

    Her alan bir environment değişkenine karşılık gelir.
    Örnek: postgresql_host -> POSTGRESQL_HOST environment değişkeni
    """

    # =========================================================================
    # UYGULAMA AYARLARI
    # =========================================================================
    app_name: str = "Patient Management API"
    app_version: str = "1.0.0"
    debug: bool = False

    # =========================================================================
    # POSTGRESQL AYARLARI
    # =========================================================================
    # Java'daki datasource.postgresql altındaki ayarlara karşılık gelir

    postgresql_host: str = "localhost"
    postgresql_port: int = 5432
    postgresql_database: str = "patient_db"
    postgresql_username: str = "postgres"
    postgresql_password: str = "postgres"

    # Connection pool ayarları (Java'daki HikariCP ayarlarına karşılık gelir)
    postgresql_pool_size: int = 10
    postgresql_max_overflow: int = 5

    # =========================================================================
    # SNOWFLAKE AYARLARI
    # =========================================================================
    # Java'daki datasource.snowflake altındaki ayarlara karşılık gelir

    snowflake_account: str = "hjelvtk-ls62935"
    snowflake_user: str = "mehmetjsl"
    snowflake_password: str = ""  # .env dosyasından okunacak
    snowflake_database: str = "POC_DB"
    snowflake_schema: str = "PUBLIC"
    snowflake_warehouse: str = "POC_WH"

    # Connection pool ayarları
    snowflake_pool_size: int = 5

    # =========================================================================
    # SERVER AYARLARI
    # =========================================================================
    server_host: str = "0.0.0.0"
    server_port: int = 8080

    @property
    def postgresql_url(self) -> str:
        """
        PostgreSQL bağlantı URL'sini oluşturur.

        Java'daki jdbc:postgresql://localhost:5432/patient_db formatına karşılık gelir.
        Python'da: postgresql+psycopg://username:password@host:port/database

        NOT: psycopg3 kullandığımız için 'postgresql+psycopg' dialect'ini kullanıyoruz.
        (psycopg2 için 'postgresql' veya 'postgresql+psycopg2' kullanılırdı)
        """
        return (
            f"postgresql+psycopg://{self.postgresql_username}:{self.postgresql_password}"
            f"@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_database}"
        )

    @property
    def snowflake_connection_params(self) -> dict:
        """
        Snowflake bağlantı parametrelerini dictionary olarak döner.

        Snowflake connector'ı JDBC URL yerine parametre dictionary'si kullanır.
        """
        return {
            "account": self.snowflake_account,
            "user": self.snowflake_user,
            "password": self.snowflake_password,
            "database": self.snowflake_database,
            "schema": self.snowflake_schema,
            "warehouse": self.snowflake_warehouse,
        }

    class Config:
        """
        Pydantic model konfigürasyonu.

        env_file: Hangi .env dosyasından okunacağını belirtir
        env_file_encoding: Dosya encoding'i
        case_sensitive: Environment değişken adları büyük/küçük harf duyarlı mı
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # POSTGRESQL_HOST ve postgresql_host aynı


# Singleton pattern: Uygulama genelinde tek bir settings nesnesi kullanılır
# Java'daki @Configuration @Bean gibi düşünebilirsin
settings = Settings()
