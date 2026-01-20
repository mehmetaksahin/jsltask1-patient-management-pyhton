"""
Alembic Migration Script Template

Bu dosya yeni migration dosyaları için şablondur.
'alembic revision -m "mesaj"' komutu ile oluşturulan dosyalar bu şablonu kullanır.

Java Karşılaştırması:
--------------------
Flyway'de migration dosyaları manuel oluşturulur: V1__create_table.sql
Alembic'de 'alembic revision' komutu ile otomatik oluşturulur.
"""

"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """
    Migration'ı uygula (upgrade).

    Java Karşılaştırması:
        Flyway'deki V1__create_table.sql dosyasının içeriği

    Burada SQLAlchemy operations kullanılır:
        op.create_table(...)
        op.add_column(...)
        op.execute("RAW SQL")
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Migration'ı geri al (downgrade).

    Flyway'de downgrade yoktur, Alembic'te var.
    Bu fonksiyon upgrade'in tersini yapar.

    Örnek:
        upgrade: create_table("users")
        downgrade: drop_table("users")
    """
    ${downgrades if downgrades else "pass"}
