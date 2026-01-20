"""
Create patient table

Java Karşılaştırması:
--------------------
Flyway (V1__create_patient_table.sql):

    CREATE TABLE tbl_patient (
        id BIGSERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        surname VARCHAR(100) NOT NULL,
        disease_name VARCHAR(200) NOT NULL
    );

    CREATE INDEX idx_patient_disease_name ON tbl_patient(disease_name);

Alembic (Python):

    op.create_table(
        'tbl_patient',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        ...
    )

Revision ID: 001
Revises: None (ilk migration)
Create Date: 2026-01-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None  # İlk migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Patient tablosunu oluşturur.

    Java'daki V1__create_patient_table.sql dosyasının karşılığı.
    """
    # Tablo oluştur
    op.create_table(
        'tbl_patient',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('surname', sa.String(length=100), nullable=False),
        sa.Column('disease_name', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Index oluştur (disease_name üzerinde)
    # Java'daki: CREATE INDEX idx_patient_disease_name ON tbl_patient(disease_name);
    op.create_index(
        'idx_patient_disease_name',
        'tbl_patient',
        ['disease_name'],
        unique=False
    )


def downgrade() -> None:
    """
    Patient tablosunu siler.

    Flyway'de bu yok, Alembic'te downgrade desteği var.
    """
    # Önce index'i sil
    op.drop_index('idx_patient_disease_name', table_name='tbl_patient')

    # Sonra tabloyu sil
    op.drop_table('tbl_patient')
