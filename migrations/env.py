"""
Alembic Environment Configuration

Bu dosya Alembic migration ortamını yapılandırır.

Java Karşılaştırması:
--------------------
Flyway otomatik olarak migration'ları bulur ve çalıştırır.
Alembic'de bu env.py dosyası ile yapılır.

Flyway:
    - classpath:db/migration altındaki V1__, V2__ dosyalarını bulur
    - Sırayla çalıştırır
    - flyway_schema_history tablosunda takip eder

Alembic:
    - migrations/versions altındaki dosyaları bulur
    - alembic_version tablosunda takip eder
    - upgrade/downgrade komutlarını destekler

Kullanım:
--------
    # Migration oluştur
    alembic revision -m "create patient table"

    # Migration'ları çalıştır
    alembic upgrade head

    # Geri al
    alembic downgrade -1
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Proje modüllerini import et
from app.config.settings import settings
from app.config.database import PostgreSQLBase

# Alembic Config nesnesi
config = context.config

# Logging konfigürasyonu
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy metadata - Alembic'in tablo yapısını bilmesi için
# Java'da Entity sınıfları taranır, burada Base.metadata kullanılır
target_metadata = PostgreSQLBase.metadata

# Veritabanı URL'sini ayarla (settings'den)
config.set_main_option("sqlalchemy.url", settings.postgresql_url)


def run_migrations_offline() -> None:
    """
    Offline migration modu.

    Veritabanına bağlanmadan SQL script'i oluşturur.
    CI/CD pipeline'larında kullanılabilir.

    Kullanım:
        alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online migration modu.

    Veritabanına bağlanarak migration'ları çalıştırır.
    Normal kullanım budur.

    Kullanım:
        alembic upgrade head
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Çalışma modunu belirle
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
