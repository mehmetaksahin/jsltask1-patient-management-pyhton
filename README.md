# Patient Management API - Python/FastAPI

A REST API for patient management with ETL (Extract-Transform-Load) capabilities. This project demonstrates how to migrate data from Snowflake to PostgreSQL using Python and FastAPI.

> **Note:** This is the Python version of the original Java/Spring Boot project. For Turkish documentation, see [README-TR.md](README-TR.md).

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13 |
| Web Framework | FastAPI |
| ORM | SQLAlchemy |
| Target Database | PostgreSQL |
| Source Database | Snowflake |
| Validation | Pydantic |
| Server | Uvicorn (ASGI) |

## Project Structure

```
jslexample-first-task-python/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config/
│   │   ├── database.py      # Database connections (PostgreSQL & Snowflake)
│   │   └── settings.py      # Application configuration
│   ├── models/
│   │   └── patient.py       # SQLAlchemy entity model
│   ├── schemas/
│   │   └── patient.py       # Pydantic DTOs (request/response)
│   ├── repositories/
│   │   └── patient_repository.py  # Data access layer
│   ├── services/
│   │   └── patient_service.py     # Business logic & ETL
│   └── routers/
│       └── patient_router.py      # API endpoints
├── extras/
│   └── docker-compose-local.yml   # Local PostgreSQL setup
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.13+
- Docker (for PostgreSQL)
- Snowflake account (for ETL feature)

### Installation

```bash
# 1. Navigate to project directory
cd jslexample-first-task-python

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and set your Snowflake password

# 5. Start PostgreSQL
docker-compose -f extras/docker-compose-local.yml up -d postgres

# 6. Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Verify Installation

- Swagger UI: http://localhost:8080/docs
- Health Check: http://localhost:8080/actuator/health

## API Endpoints

### Patient CRUD Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/patients` | List all patients |
| GET | `/api/patients/{id}` | Get patient by ID |
| POST | `/api/patients` | Create new patient |
| DELETE | `/api/patients/{id}` | Delete patient |

### ETL Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/patients/migrate` | Migrate data from Snowflake to PostgreSQL |

### Health & Info (Actuator-style)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/actuator/health` | Health check |
| GET | `/actuator/info` | Application info |

## Example Requests

### Create Patient

```bash
curl -X POST http://localhost:8080/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John",
    "surname": "Doe",
    "disease_name": "Hypertension"
  }'
```

### Get All Patients

```bash
curl http://localhost:8080/api/patients
```

### Run ETL Migration

```bash
curl -X POST http://localhost:8080/api/patients/migrate
```

## Configuration

Environment variables (set in `.env` file):

```env
# PostgreSQL
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=patient_db
POSTGRESQL_USERNAME=postgres
POSTGRESQL_PASSWORD=postgres

# Snowflake
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-user
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=POC_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=POC_WH
```

## Java vs Python Comparison

This project serves as a learning resource for Java developers transitioning to Python. Key differences:

| Concept | Java/Spring Boot | Python/FastAPI |
|---------|------------------|----------------|
| Entry Point | `@SpringBootApplication` | `FastAPI()` instance |
| Dependency Injection | `@Autowired` | `Depends()` |
| Entity | `@Entity` class | SQLAlchemy model |
| DTO | Record/Class | Pydantic `BaseModel` |
| Repository | `JpaRepository<T, ID>` | Custom class with session |
| Configuration | `application.yml` | `Settings` class + `.env` |
| Validation | `@NotBlank`, `@Valid` | Pydantic `Field()` |

## License

MIT License
