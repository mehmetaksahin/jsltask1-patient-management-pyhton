USE ROLE ACCOUNTADMIN;

-- 1. Depo ve İşlem Gücü
CREATE OR REPLACE WAREHOUSE POC_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

CREATE OR REPLACE DATABASE POC_DB;
CREATE OR REPLACE SCHEMA POC_DB.PUBLIC;

-- 2. Image Registry (Burası senin Docker Hub'ın olacak)
-- Bu komut schema altında bir imaj deposu oluşturur.
CREATE IMAGE REPOSITORY POC_DB.PUBLIC.MY_IMAGE_REPO;

-- 3. Compute Pool (Bu senin Kubernetes Cluster'ın/Node Group'un)
-- STANDARD_XSMALL, test için en ucuz seçeneklerden biridir.
CREATE COMPUTE POOL IF NOT EXISTS POC_POOL
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_XS; -- Dikkat: CPU mimarisi X64

-- 4. Rol ve Yetkiler (Best Practice)
CREATE ROLE IF NOT EXISTS POC_SERVICE_ROLE;
GRANT USAGE ON DATABASE POC_DB TO ROLE POC_SERVICE_ROLE;
GRANT USAGE ON SCHEMA POC_DB.PUBLIC TO ROLE POC_SERVICE_ROLE;
GRANT READ, WRITE ON IMAGE REPOSITORY POC_DB.PUBLIC.MY_IMAGE_REPO TO ROLE POC_SERVICE_ROLE;
GRANT USAGE ON WAREHOUSE POC_WH TO ROLE POC_SERVICE_ROLE;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE POC_SERVICE_ROLE; -- Dışarıdan erişim için
GRANT USAGE ON COMPUTE POOL POC_POOL TO ROLE POC_SERVICE_ROLE;


------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
SHOW IMAGE REPOSITORIES IN SCHEMA POC_DB.PUBLIC;



------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
USE DATABASE POC_DB;
USE SCHEMA PUBLIC;

CREATE TABLE IF NOT EXISTS TBL_PATIENT (
 ID NUMBER AUTOINCREMENT PRIMARY KEY,
 NAME VARCHAR(100) NOT NULL,
 SURNAME VARCHAR(100) NOT NULL,
 DISEASE_NAME VARCHAR(200) NOT NULL
);

INSERT INTO TBL_PATIENT (NAME, SURNAME, DISEASE_NAME) VALUES
    ('John', 'Smith', 'Hypertension'),
    ('Emily', 'Johnson', 'Type 2 Diabetes'),
    ('Michael', 'Williams', 'Asthma'),
    ('Sarah', 'Brown', 'Migraine'),
    ('David', 'Jones', 'Rheumatoid Arthritis'),
    ('Jennifer', 'Davis', 'Chronic Kidney Disease'),
    ('Robert', 'Miller', 'Coronary Artery Disease'),
    ('Jessica', 'Wilson', 'Hypothyroidism'),
    ('William', 'Moore', 'Osteoporosis'),
    ('Amanda', 'Taylor', 'Gastroesophageal Reflux Disease');

SELECT * FROM PUBLIC.TBL_PATIENT;


------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------

USE DATABASE POC_DB;
USE SCHEMA PUBLIC;

SHOW IMAGE REPOSITORIES;



USE ROLE ACCOUNTADMIN;
USE DATABASE POC_DB;
USE SCHEMA PUBLIC;

-- 1. Eski repository'yi sil
DROP IMAGE REPOSITORY IF EXISTS MY_IMAGE_REPO;

-- 2. Yeni repository'yi oluştur
CREATE IMAGE REPOSITORY POC_REPO;

-- 3. Yetkileri ver
GRANT READ, WRITE ON IMAGE REPOSITORY POC_REPO TO ROLE POC_SERVICE_ROLE;

-- 4. Repository URL'ini kontrol et
SHOW IMAGE REPOSITORIES IN SCHEMA POC_DB.PUBLIC; -- hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo

------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------

-- Snowflake'te image'ı listele
SHOW IMAGES IN IMAGE REPOSITORY POC_DB.PUBLIC.POC_REPO; -- poc_db/public/poc_repo/patient-management:latest & poc_db/public/poc_repo/postgres:15-alpine

------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------

-- 1. Spec dosyasını stage'e yükle

SHOW STAGES IN SCHEMA POC_DB.PUBLIC;

CREATE STAGE POC_DB.PUBLIC.POC_STAGE;

SHOW STAGES IN SCHEMA POC_DB.PUBLIC;

-- arch -arm64 brew install --cask snowflake-snowsql
-- vim .zshrc -> export PATH="/Applications/SnowSQL.app/Contents/MacOS:$PATH"
-- snowsql -a hjelvtk-ls62935 -u mehmetjsl -------> password: 'xxxxxxxxxxxxx'

--USE DATABASE POC_DB;
--USE SCHEMA PUBLIC;
--PUT file:///Users/mehmetaksahin/memox/jsl/jslexample-first-task/spcs/patient-service-spec.yaml @poc_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;


-- Mevcut compute pool'ları listele
SHOW COMPUTE POOLS;

-- 2. Service oluştur

-- Network rule oluştur
CREATE OR REPLACE NETWORK RULE poc_egress_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('0.0.0.0:443', '0.0.0.0:80');

-- External access integration oluştur
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION poc_external_access
  ALLOWED_NETWORK_RULES = (poc_egress_rule)
  ENABLED = TRUE;

-- DİKKAT !!!!!!!!!!!
-- SQL compilation error: External access is not supported for trial accounts.

-- Sonra service'i oluştur
CREATE SERVICE patient_service
  IN COMPUTE POOL POC_POOL
  FROM @poc_stage
  SPECIFICATION_FILE = 'patient-service-spec.yaml'
  EXTERNAL_ACCESS_INTEGRATIONS = (poc_external_access);

-- DİKKAT !!!!!!!!!!!
-- SQL compilation error: External access is not supported for trial accounts.


-- 3. Service durumunu kontrol et
--DESCRIBE SERVICE patient_service;
--CALL SYSTEM$GET_SERVICE_STATUS('patient_service');

-- 4. Service loglarını kontrol et
--CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'patient-api');
--CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'postgresql');

------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------

-- Trial hesaplarda External Access Integration desteklenmiyor. Service'i external access olmadan oluşturalım.
-- Bu durumda service dışarıdan erişilemez olacak. Ama Snowflake içinden (aynı account'tan) erişilebilir.
-- Trial hesap limitleri nedeniyle alternatif yaklaşım:
-- Eğer dışarıdan (Postman'den) erişim gerekiyorsa, spec dosyasını güncelleyip public: true yerine Snowflake Function üzerinden erişim sağlayabiliriz. Ama önce service'in çalışıp çalışmadığını kontrol edelim:

-- Service oluştur
CREATE SERVICE patient_service
  IN COMPUTE POOL POC_POOL
  FROM @poc_stage
  SPECIFICATION_FILE = 'patient-service-spec.yaml';

-- Durumu kontrol et
DESCRIBE SERVICE patient_service;
-- dns_name: patient-service.bfn6.svc.spcs.internal

-- Service durumunu kontrol et
CALL SYSTEM$GET_SERVICE_STATUS('patient_service');

-- Logları kontrol et
CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'patient-api');
CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'postgresql'); -- ??????? exec /usr/local/bin/docker-entrypoint.sh: exec format error -> postgresql benim macte derlenince arm64 olmuş bunu amd64 yapıyorum


-- HATADAN DOLAYI TEKRAR SİL KUR YAPIYORUZ
-- snowsql -> PUT file:///Users/mehmetaksahin/memox/jsl/jslexample-first-task/spcs/patient-service-spec.yaml @poc_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- bir de imajı yeniden yükledik

-- Service'i sil
DROP SERVICE IF EXISTS patient_service;

-- Yeniden oluştur
CREATE SERVICE patient_service
  IN COMPUTE POOL POC_POOL
  FROM @poc_stage
  SPECIFICATION_FILE = 'patient-service-spec.yaml';

-- Birkaç dakika sonra durumu kontrol ediyoruz
CALL SYSTEM$GET_SERVICE_STATUS('patient_service');
-- [{"status":"READY","message":"Running","containerName":"patient-api","instanceId":"0","serviceName":"PATIENT_SERVICE","image":"hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/patient-management:latest","restartCount":0,"startTime":"2026-01-19T15:50:45Z"},{"status":"READY","message":"Running","containerName":"postgresql","instanceId":"0","serviceName":"PATIENT_SERVICE","image":"hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/postgres:15-alpine","restartCount":0,"startTime":"2026-01-19T15:50:44Z"}]

-- Logları kontrol et
CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'postgresql');
-- 2026-01-19 15:50:46.149 UTC [1] LOG:  database system is ready to accept connections
CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'patient-api');
-- Snowflake-HikariPool - Start completed.
-- HHH000342: Could not obtain connection to query metadata
-- HHH90000025: PostgreSQLDialect does not need to be specified explicitly using 'hibernate.dialect' (remove the property setting and it will be selected by default)
-- Attempting Flyway migration on PostgreSQL...
-- lyway migration completed successfully
-- Completed initialization in 9 ms
-- net.snowflake.client.jdbc.RestRequest    : Stop retrying since elapsed time due to network issues has reached timeout. Elapsed: 300,050(ms), timeout: 300,000(ms)


SHOW ENDPOINTS IN SERVICE patient_service;

-- Patients listesi için Service Function oluştur
CREATE OR REPLACE FUNCTION get_patients()
RETURNS VARIANT
SERVICE = patient_service
ENDPOINT = 'patient-api'
AS '/api/patients';

-- Test et
SELECT get_patients();

-- Önce basit bir GET deneyelim ki login olmadığı için çalışmadı galiba
SELECT SYSTEM$CALL_SERVICE_ENDPOINT('patient_service', 'patient-api', '/actuator/health');

-- tarayıcıdan bak
--https://mqa4u-hjelvtk-ls62935.snowflakecomputing.app/api/patients

--
-- 1. Security Integration oluştur (OAuth Client)
CREATE OR REPLACE SECURITY INTEGRATION patient_api_oauth
  TYPE = OAUTH
  ENABLED = TRUE
  OAUTH_CLIENT = CUSTOM
  OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
  OAUTH_REDIRECT_URI = 'https://oauth.pstmn.io/v1/callback'
  OAUTH_ISSUE_REFRESH_TOKENS = TRUE
  OAUTH_REFRESH_TOKEN_VALIDITY = 86400;

-- OAUTH_CLIENT_ID:
-- kMoBQd6lZ0iRIB5W+LjzHc3CQqM=
-- 3. Client Secret'ı almak için
SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('PATIENT_API_OAUTH'); -- {"OAUTH_CLIENT_SECRET_2":"pIl/A7RlzfxPnp1MXlXjxDEQe/AWpdKhtUXBvUlJEy0=","OAUTH_CLIENT_SECRET":"vNyMuDzvNjcHqY0Vvxr9kEBRfVlaAxsbJx+5n4/Mv5A=","OAUTH_CLIENT_ID":"kMoBQd6lZ0iRIB5W+LjzHc3CQqM="}



-- 2. Client ID ve Secret'ı al
DESCRIBE SECURITY INTEGRATION patient_api_oauth;


------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------

CREATE OR REPLACE NETWORK RULE snowflake_egress_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('hjelvtk-ls62935.snowflakecomputing.com:443');

-- Bu sadece TAM HESAPTA çalışır (trial'da çalışmaz)
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION snowflake_access
  ALLOWED_NETWORK_RULES = (snowflake_egress_rule)
  ENABLED = TRUE; -- SQL compilation error: External access is not supported for trial accounts.

-- Service'i bu integration ile oluştur
ALTER SERVICE patient_service SET
  EXTERNAL_ACCESS_INTEGRATIONS = (snowflake_access);

------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------

-- PYTHON'A BAŞLIYORUZ

-- python projesinin imajını yükledim docker push ile
-- postgreyi attım ama sonra zaten var diye değiştirmedi galiba


SHOW IMAGES IN IMAGE REPOSITORY POC_DB.PUBLIC.POC_REPO;
-- patient-management:latest
-- patient-management-python:latest
-- postgres:15alphine


SELECT * FROM PUBLIC.TBL_PATIENT;
-- datalar var


-- 3. Service durumunu kontrol et
CALL SYSTEM$GET_SERVICE_STATUS('patient_service');

-- java serviceinin loglarını kontrol et
CALL SYSTEM$GET_SERVICE_LOGS('patient_service', 0, 'patient-api');

-- tüm servisleri durdur uçur
DROP SERVICE IF EXISTS patient_service;


-- SnowSQL ile spcs dosyasını yükledim:
-- snowsql -a hjelvtk-ls62935 -u mehmetjsl
-- terminal: mehmetjsl#POC_WH@(no database).(no schema)
-- USE DATABASE POC_DB;
-- USE SCHEMA PUBLIC;
-- terminal şuna döndü: mehmetjsl#POC_WH@POC_DB.PUBLIC>
-- not: öncesinde spec yaml dosyasının içindeki şifreyi güncelledim
-- PUT file:///Users/mehmetaksahin/memox/jsl/jslexample-first-task-python/spcs/patient-service-spec.yaml @poc_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
--+---------------------------+---------------------------+-------------+-------------+--------------------+--------------------+----------+---------+
--| source                    | target                    | source_size | target_size | source_compression | target_compression | status   | message |
--|---------------------------+---------------------------+-------------+-------------+--------------------+--------------------+----------+---------|
--| patient-service-spec.yaml | patient-service-spec.yaml |        4149 |        4160 | NONE               | NONE               | UPLOADED |         |
--+---------------------------+---------------------------+-------------+-------------+--------------------+--------------------+----------+---------+


CREATE SERVICE patient_service_python
  IN COMPUTE POOL POC_POOL
  FROM @poc_stage
  SPECIFICATION_FILE = 'patient-service-spec.yaml';
-- DROP SERVICE IF EXISTS patient_service_python;


-- Service durumunu kontrol et
CALL SYSTEM$GET_SERVICE_STATUS('patient_service_python');

CALL SYSTEM$GET_SERVICE_LOGS('patient_service_python', 0, 'postgres'); -- OK
CALL SYSTEM$GET_SERVICE_LOGS('patient_service_python', 0, 'patient-api'); -- OK

-- Kontroller
SHOW IMAGES IN IMAGE REPOSITORY POC_DB.PUBLIC.POC_REPO;

SELECT SYSTEM$CALL_SERVICE_ENDPOINT('patient_service_python', 'patient-api', '/health'); -- bunlar çalışmaz
SELECT SYSTEM$CALL_SERVICE_ENDPOINT('patient_service_python', 'patient-api', '/api/patients'); -- bunlar çalışmaz

SHOW ENDPOINTS IN SERVICE patient_service_python;
-- tarayıcıdan bak çünkü login isteyecek
--https://ira4u-hjelvtk-ls62935.snowflakecomputing.app/api/patients

-- ÇALIŞTI

-- ŞİMDİ yeni bir endpoint ekledim get tipinde
-- o yüzden uçurup yeniden kuracağım
DROP SERVICE IF EXISTS patient_service_python;

CREATE SERVICE patient_service_python
  IN COMPUTE POOL POC_POOL
  FROM @poc_stage
  SPECIFICATION_FILE = 'patient-service-spec.yaml';

CALL SYSTEM$GET_SERVICE_STATUS('patient_service_python');

CALL SYSTEM$GET_SERVICE_LOGS('patient_service_python', 0, 'postgres');

CALL SYSTEM$GET_SERVICE_LOGS('patient_service_python', 0, 'patient-api');

SHOW ENDPOINTS IN SERVICE patient_service_python; --mra4u-hjelvtk-ls62935.snowflakecomputing.app

-- https://mra4u-hjelvtk-ls62935.snowflakecomputing.app/api/patients
-- bu çalıştı
--

-- https://mra4u-hjelvtk-ls62935.snowflakecomputing.app/api/patients/migrate-get
-- ama bunda şu hata geldi
-- {"detail":"Failed to connect to Snowflake: 250001: Could not connect to Snowflake backend after 2 attempt(s).Aborting"}
/*
Sorunun sebebi: Snowflake Container Services (SPCS) içindeki container'lar varsayılan olarak dış ağa (internet) erişemez. Trial hesaplarda External Access Integration desteklenmediği için container içinden Snowflake API'sine (JDBC/ODBC bağlantısı) ulaşılamıyor.
DataGrip'ten bağlanabiliyorsunuz çünkü o sizin bilgisayarınızdan gidiyor (internet erişimi var). Ama container içinden Snowflake'e bağlanmak için hjelvtk-ls62935.snowflakecomputing.com:443 adresine erişim gerekiyor - bu da "external access" sayılıyor.
Çözüm seçenekleri:
1 Snowflake'i atlayıp sadece PostgreSQL kullan - Migration özelliğini devre dışı bırak, sadece PostgreSQL CRUD'u göster
2 Snowflake verilerini önceden PostgreSQL'e aktar - Snowflake Worksheet'ten manuel sorgu ile verileri çekip PostgreSQL'e INSERT et
3 Service Function üzerinden Snowflake'e eriş - Container içinden değil, Snowflake tarafından çağrılan bir function ile veri çek
Seçenek 3 için yaklaşım:

-- Snowflake'te bir function oluştur
CREATE OR REPLACE FUNCTION get_snowflake_patients()
RETURNS TABLE (id NUMBER, name VARCHAR, surname VARCHAR, disease_name VARCHAR)
AS
$$
  SELECT ID, NAME, SURNAME, DISEASE_NAME FROM TBL_PATIENT
$$;

-- Servisten bu function'ı çağır
SELECT * FROM TABLE(get_snowflake_patients());

Ama bu da container'dan Snowflake'e bağlantı gerektirir.
En pratik çözüm: Trial hesapta Snowflake → PostgreSQL migration'ı doğrudan container içinden yapamazsınız. Bunun yerine:
Snowflake'ten verileri manuel çekin
/api/patients POST endpoint'i ile PostgreSQL'e ekleyin
Ya da projeyi "demo amaçlı" olarak sadece PostgreSQL CRUD gösterimi şeklinde sunun. Ne dersiniz?
*/




-- ŞİFRELERİ SİLMEYİ UNUTMA
