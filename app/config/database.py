"""
Veritabanı Bağlantı Konfigürasyonu

Bu dosya PostgreSQL ve Snowflake veritabanı bağlantılarını yönetir.

Java Karşılaştırması:
--------------------
Java'da her veritabanı için ayrı @Configuration sınıfları var:
- PostgreSQLDataSourceConfig.java
- SnowflakeDataSourceConfig.java

Her birinde:
- DataSource bean'i (bağlantı havuzu)
- EntityManagerFactory bean'i (JPA session yönetimi)
- TransactionManager bean'i

Python'da bunların karşılığı:
- Engine: DataSource'a karşılık gelir (bağlantı havuzu)
- SessionLocal: EntityManager'a karşılık gelir (session factory)
- Session: Her request için bir session (Unit of Work pattern)

SQLAlchemy Temel Kavramları:
---------------------------
1. Engine: Veritabanına fiziksel bağlantıyı temsil eder
   - Connection pool yönetimi
   - Dialect (PostgreSQL, MySQL vb.) seçimi

2. Session: Veritabanı işlemlerini gruplar (transaction)
   - Java'daki EntityManager'a benzer
   - Nesneleri takip eder (identity map)
   - commit() ve rollback() işlemleri

3. Base: Tüm model sınıflarının miras aldığı temel sınıf
   - Java'daki @Entity sınıflarının ortak atasına benzer
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import snowflake.connector
from contextlib import contextmanager

from app.config.settings import settings


# =============================================================================
# POSTGRESQL KONFIGÜRASYONU
# =============================================================================

# Engine oluşturma (Java'daki DataSource bean'ine karşılık gelir)
# create_engine() fonksiyonu:
# - Bağlantı URL'sini alır
# - Connection pool oluşturur
# - Dialect'i otomatik seçer (postgresql://)
postgresql_engine = create_engine(
    settings.postgresql_url,

    # Connection Pool Ayarları (Java'daki HikariCP ayarlarına karşılık gelir)
    poolclass=QueuePool,  # Bağlantı havuzu tipi
    pool_size=settings.postgresql_pool_size,  # Havuzdaki sabit bağlantı sayısı
    max_overflow=settings.postgresql_max_overflow,  # Ekstra bağlantı sayısı (yoğunlukta)
    pool_pre_ping=True,  # Her kullanımda bağlantının canlı olduğunu kontrol et

    # Debug için SQL sorgularını logla (Java'daki hibernate.show_sql: true)
    echo=settings.debug,
)

# SessionLocal: Session factory oluşturma
# Java'daki EntityManagerFactory'ye karşılık gelir
# Her request için yeni bir session oluşturulur
PostgreSQLSessionLocal = sessionmaker(
    autocommit=False,  # Manuel commit gerekli (transaction kontrolü)
    autoflush=False,   # Manuel flush gerekli
    bind=postgresql_engine  # Hangi engine'e bağlı
)

# Base sınıf: Tüm PostgreSQL modelleri bu sınıftan miras alır
# Java'da buna gerek yok çünkü @Entity annotation'ı kullanılıyor
PostgreSQLBase = declarative_base()


# =============================================================================
# SNOWFLAKE KONFIGÜRASYONU
# =============================================================================

# Snowflake için SQLAlchemy yerine native connector kullanıyoruz
# Çünkü Snowflake'in SQLAlchemy desteği sınırlı ve JPA gibi çalışmıyor
# Java'da da Snowflake JDBC ile direkt çalışılabilir

def get_snowflake_connection():
    """
    Snowflake bağlantısı oluşturur.

    Java'daki SnowflakeDataSourceConfig.snowflakeDataSource() metoduna karşılık gelir.

    Returns:
        snowflake.connector.connection: Snowflake bağlantı nesnesi
    """
    return snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        password=settings.snowflake_password,
        database=settings.snowflake_database,
        schema=settings.snowflake_schema,
        warehouse=settings.snowflake_warehouse,
    )


@contextmanager
def snowflake_session():
    """
    Snowflake bağlantısını context manager olarak sağlar.

    Context Manager Nedir?
    ---------------------
    Python'da 'with' ifadesi ile kullanılan nesnelerdir.
    Otomatik olarak kaynakları açar ve kapatır.

    Kullanım:
        with snowflake_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TBL_PATIENT")

    Java Karşılığı:
        try (Connection conn = dataSource.getConnection()) {
            // işlemler
        } // otomatik kapanır

    Yields:
        snowflake.connector.connection: Snowflake bağlantısı
    """
    conn = None
    try:
        conn = get_snowflake_connection()
        yield conn
    finally:
        if conn:
            conn.close()


# =============================================================================
# DEPENDENCY INJECTION FONKSİYONLARI
# =============================================================================

def get_postgresql_db():
    """
    PostgreSQL session'ı sağlayan dependency injection fonksiyonu.

    FastAPI'de Dependency Injection (DI):
    ------------------------------------
    Java'daki @Autowired gibi çalışır ama fonksiyon bazlı.
    FastAPI endpoint'lerinde 'Depends()' ile kullanılır.

    Java Karşılığı:
        @Autowired
        private EntityManager entityManager;

    Python/FastAPI Kullanımı:
        @app.get("/patients")
        def get_patients(db: Session = Depends(get_postgresql_db)):
            return db.query(Patient).all()

    Yields:
        Session: SQLAlchemy session nesnesi

    Not: 'yield' kullanımı, request bittiğinde session'ın otomatik kapanmasını sağlar
    (Java'daki try-with-resources gibi)
    """
    db = PostgreSQLSessionLocal()
    try:
        yield db
    finally:
        db.close()
