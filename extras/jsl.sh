REGISTRY="hjelvtk-ls62935.registry.snowflakecomputing.com"
REPO_PATH="poc_db/public/poc_repo"
PYTHON_IMAGE="patient-management-python"
POSTGRES_IMAGE="postgres:15-alpine"

docker login hjelvtk-ls62935.registry.snowflakecomputing.com -u mehmetjsl -p 'sifresifresifre'

docker rmi hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/postgres:15-alpine
docker rmi postgres:15-alpine
docker pull --platform linux/amd64 postgres:15-alpine # mac mini m4 işlemcili olduğu için platform belirtildi
docker inspect postgres:15-alpine | grep Architecture # "Architecture": "amd64"
docker tag postgres:15-alpine hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/postgres:15-alpine
docker push hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/postgres:15-alpine

# java imajlarını sil
#docker rmi patient-management:latest
#docker rmi hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/patient-management:latest
#docker rmi patient-management-python:latest
#docker rmi hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/patient-management-python:latest

cd /Users/mehmetaksahin/memox/jsl/jslexample-first-task-python
docker build --platform linux/amd64 -t patient-management-python:latest . # mac mini m4 işlemcili olduğu için platform belirtildi
docker tag patient-management-python:latest hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/patient-management-python:latest
docker push hjelvtk-ls62935.registry.snowflakecomputing.com/poc_db/public/poc_repo/patient-management-python:latest

