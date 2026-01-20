#!/bin/bash
# =============================================================================
# SNOWFLAKE DOCKER REGISTRY PUSH SCRIPT (PYTHON VERSION)
# =============================================================================
# Bu script, Python uygulamasını Snowflake Container Registry'ye push eder.
#
# Java Versiyonu ile Fark:
# -----------------------
# Java: patient-management:latest
# Python: patient-management-python:latest
#
# Kullanım:
# ---------
#   chmod +x jsl.sh
#   ./jsl.sh
# =============================================================================

# Registry bilgileri
REGISTRY="hjelvtk-ls62935.registry.snowflakecomputing.com"
REPO_PATH="poc_db/public/poc_repo"

# Image adları
PYTHON_IMAGE="patient-management-python"
POSTGRES_IMAGE="postgres:15-alpine"

echo "=============================================="
echo "Snowflake Container Registry Push Script"
echo "Python Version"
echo "=============================================="

# -----------------------------------------------------------------------------
# STEP 1: Docker Registry'ye Login
# -----------------------------------------------------------------------------
echo ""
echo "[1/4] Logging into Snowflake Docker Registry..."
echo "Registry: $REGISTRY"
echo ""

docker login $REGISTRY

if [ $? -ne 0 ]; then
    echo "ERROR: Docker login failed!"
    exit 1
fi

echo "Login successful!"

# -----------------------------------------------------------------------------
# STEP 2: PostgreSQL Image'ını Push Et
# -----------------------------------------------------------------------------
echo ""
echo "[2/4] Pulling and pushing PostgreSQL image..."
echo ""

# PostgreSQL image'ını indir
docker pull $POSTGRES_IMAGE

# Tag ekle
docker tag $POSTGRES_IMAGE $REGISTRY/$REPO_PATH/$POSTGRES_IMAGE

# Push et
docker push $REGISTRY/$REPO_PATH/$POSTGRES_IMAGE

if [ $? -ne 0 ]; then
    echo "ERROR: PostgreSQL image push failed!"
    exit 1
fi

echo "PostgreSQL image pushed successfully!"

# -----------------------------------------------------------------------------
# STEP 3: Python API Image'ını Build Et
# -----------------------------------------------------------------------------
echo ""
echo "[3/4] Building Python Patient Management API image..."
echo ""

# Proje kök dizinine git (extras klasöründen bir üst dizin)
cd "$(dirname "$0")/.."

# M4 işlemci için platform belirt (amd64)
# Snowflake SPCS linux/amd64 gerektirir
docker build --platform linux/amd64 -t $PYTHON_IMAGE:latest .

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed!"
    exit 1
fi

echo "Docker build successful!"

# -----------------------------------------------------------------------------
# STEP 4: Python API Image'ını Push Et
# -----------------------------------------------------------------------------
echo ""
echo "[4/4] Pushing Python Patient Management API image..."
echo ""

# Tag ekle
docker tag $PYTHON_IMAGE:latest $REGISTRY/$REPO_PATH/$PYTHON_IMAGE:latest

# Push et
docker push $REGISTRY/$REPO_PATH/$PYTHON_IMAGE:latest

if [ $? -ne 0 ]; then
    echo "ERROR: Python API image push failed!"
    exit 1
fi

echo "Python API image pushed successfully!"

# -----------------------------------------------------------------------------
# TAMAMLANDI
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "All images pushed successfully!"
echo "=============================================="
echo ""
echo "Pushed images:"
echo "  - $REGISTRY/$REPO_PATH/$POSTGRES_IMAGE"
echo "  - $REGISTRY/$REPO_PATH/$PYTHON_IMAGE:latest"
echo ""
echo "Next steps:"
echo "  1. Update SPCS service spec if needed"
echo "  2. Create/update Snowflake service"
echo "=============================================="
