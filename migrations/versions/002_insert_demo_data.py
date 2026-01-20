"""
Insert demo data

Java Karşılaştırması:
--------------------
Flyway (V2__insert_demo_data.sql):

    INSERT INTO tbl_patient (name, surname, disease_name) VALUES
        ('Mehmet', 'Aksahin', 'Migraine'),
        ('Mehmetovski', 'Aksahinovski', 'Gastroesophageal Reflux Disease');

Alembic (Python):

    op.execute(\"\"\"
        INSERT INTO tbl_patient (name, surname, disease_name) VALUES
        ('Mehmet', 'Aksahin', 'Migraine')
    \"\"\")

Revision ID: 002
Revises: 001
Create Date: 2026-01-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = '002'
down_revision: Union[str, None] = '001'  # 001'e bağlı
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Demo verilerini ekler.

    Java'daki V2__insert_demo_data.sql dosyasının karşılığı.
    """
    # Raw SQL ile veri ekleme
    # Java'daki SQL dosyasıyla aynı
    op.execute("""
        INSERT INTO tbl_patient (name, surname, disease_name) VALUES
            ('Mehmet', 'Aksahin', 'Migraine'),
            ('Mehmetovski', 'Aksahinovski', 'Gastroesophageal Reflux Disease')
    """)


def downgrade() -> None:
    """
    Demo verilerini siler.

    NOT: Production'da veri silme tehlikeli olabilir.
    Bu sadece demo/test amaçlıdır.
    """
    op.execute("""
        DELETE FROM tbl_patient
        WHERE name IN ('Mehmet', 'Mehmetovski')
          AND surname IN ('Aksahin', 'Aksahinovski')
    """)
