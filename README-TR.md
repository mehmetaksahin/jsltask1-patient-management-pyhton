# Patient Management API - Python Version

Snowflake'den PostgreSQL'e hasta verisi aktarımı yapan ETL uygulaması.

Bu proje, Java/Spring Boot versiyonunun Python/FastAPI'ye dönüştürülmüş halidir.

## Teknoloji Stack'i

| Katman | Java (Orijinal) | Python (Bu Proje) |
|--------|-----------------|-------------------|
| Web Framework | Spring Boot 3.2 | FastAPI |
| ORM | Spring Data JPA | SQLAlchemy |
| Veritabanı Driver | PostgreSQL JDBC | psycopg2 |
| Snowflake Driver | Snowflake JDBC | snowflake-connector-python |
| Validasyon | Bean Validation | Pydantic |
| Migration | Flyway | Alembic |
| HTTP Server | Tomcat (embedded) | Uvicorn (ASGI) |

## Proje Yapısı

```
jslexample-first-task-python/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Uygulama giriş noktası
│   ├── config/
│   │   ├── settings.py          # Konfigürasyon (application.yml karşılığı)
│   │   └── database.py          # Veritabanı bağlantıları
│   ├── models/
│   │   ├── patient.py           # PostgreSQL Entity
│   │   └── snowflake_patient.py # Snowflake veri modeli
│   ├── schemas/
│   │   └── patient.py           # Pydantic DTO'ları
│   ├── repositories/
│   │   ├── patient_repository.py      # PostgreSQL CRUD
│   │   └── snowflake_repository.py    # Snowflake okuma
│   ├── services/
│   │   ├── patient_service.py         # İş mantığı
│   │   └── migration_service.py       # ETL servisi
│   └── controllers/
│       ├── patient_controller.py      # REST API
│       └── health_controller.py       # Health check
├── migrations/                  # Alembic migrations
├── extras/
│   ├── jsl.sh                   # Docker push script
│   ├── docker-compose-local.yml # Lokal geliştirme
│   └── Patient-Management-API.postman_collection.json
├── spcs/
│   └── patient-service-spec.yaml    # Snowflake SPCS config
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── .env.example
```

## Kurulum

### 1. Sanal Ortam Oluştur (Önerilen)

```bash
# Python sanal ortamı oluştur
python -m venv venv

# Aktive et
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 3. Environment Değişkenlerini Ayarla

```bash
# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle (özellikle Snowflake şifresi)
```

### 4. PostgreSQL Başlat (Docker)

```bash
docker-compose -f extras/docker-compose-local.yml up -d postgres
```

### 5. Uygulamayı Çalıştır

```bash
# Geliştirme modu (hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# veya
python -m app.main
```

## API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/patients` | Tüm hastaları listele |
| GET | `/api/patients/{id}` | ID'ye göre hasta getir |
| POST | `/api/patients` | Yeni hasta oluştur |
| POST | `/api/patients/migrate` | Snowflake → PostgreSQL ETL |
| GET | `/actuator/health` | Sağlık kontrolü |
| GET | `/actuator/info` | Uygulama bilgisi |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

## API Dokümantasyonu

FastAPI otomatik olarak API dokümantasyonu oluşturur:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

## Docker ile Çalıştırma

### Lokal Docker Compose

```bash
# Tümünü başlat (PostgreSQL + API)
docker-compose -f extras/docker-compose-local.yml up -d

# Logları izle
docker-compose -f extras/docker-compose-local.yml logs -f

# Durdur
docker-compose -f extras/docker-compose-local.yml down
```

### Snowflake SPCS'e Deploy

```bash
# 1. Docker image'ı build ve push et
chmod +x extras/jsl.sh
./extras/jsl.sh

# 2. Snowflake'de service oluştur
# (spcs/patient-service-spec.yaml kullan)
```

## ETL Süreci

`POST /api/patients/migrate` endpoint'i çağrıldığında:

1. **EXTRACT**: Snowflake'den `TBL_PATIENT` tablosundaki tüm veriler okunur
2. **TRANSFORM**: Her alanın sonuna timestamp eklenir
   - `"William"` → `"William 2026-01-20 10:30:45"`
3. **LOAD**: Dönüştürülen veriler PostgreSQL'deki `tbl_patient` tablosuna kaydedilir

## Database Migration

```bash
# Migration'ları uygula
alembic upgrade head

# Yeni migration oluştur
alembic revision -m "description"

# Migration durumunu kontrol et
alembic current
```

## Test

```bash
# Postman collection'ı import et
# extras/Patient-Management-API.postman_collection.json

# veya curl ile test et
curl http://localhost:8080/api/patients
curl http://localhost:8080/actuator/health
```

## Java vs Python Karşılaştırması

### Request Body

Java (camelCase):
```json
{
    "name": "John",
    "surname": "Doe",
    "diseaseName": "Hypertension"
}
```

Python (snake_case):
```json
{
    "name": "John",
    "surname": "Doe",
    "disease_name": "Hypertension"
}
```

### Annotation vs Decorator

Java:
```java
@RestController
@RequestMapping("/api/patients")
public class PatientController {
    @GetMapping
    public List<Patient> getAll() { ... }
}
```

Python:
```python
router = APIRouter(prefix="/api/patients")

@router.get("")
def get_all(): ...
```

## Lisans

MIT License
