"""
Snowflake Patient Model

Bu dosya Snowflake'deki 'TBL_PATIENT' tablosundan gelen verileri temsil eder.

Java Karşılaştırması:
--------------------
Java (SnowflakePatient.java):
    @Entity
    @Table(name = "TBL_PATIENT")
    public class SnowflakePatient {
        @Id
        private Long id;

        @Column(name = "NAME")
        private String name;
        ...
    }

Python'da Farklılık:
-------------------
Snowflake için SQLAlchemy Entity kullanmak yerine basit bir dataclass kullanıyoruz.
Çünkü:
1. Snowflake connector SQLAlchemy ile tam uyumlu değil
2. Sadece okuma (SELECT) yapacağız, JPA özellikleri gerekmez
3. Native connector daha hızlı ve güvenilir

Dataclass Nedir?
---------------
Python 3.7+ ile gelen bir özellik.
Otomatik olarak __init__, __repr__, __eq__ metodları oluşturur.
Java'daki Lombok @Data annotation'ına benzer.

Java Lombok:
    @Data
    @Builder
    public class SnowflakePatient {
        private Long id;
        private String name;
        private String surname;
        private String diseaseName;
    }

Python Dataclass:
    @dataclass
    class SnowflakePatient:
        id: int
        name: str
        surname: str
        disease_name: str
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SnowflakePatient:
    """
    Snowflake'den gelen hasta verilerini temsil eden veri sınıfı.

    NOT: Snowflake'de sütun adları BÜYÜK HARF'tir:
    - ID, NAME, SURNAME, DISEASE_NAME

    Attributes:
        id (int): Birincil anahtar
        name (str): Hasta adı (Snowflake'de NAME sütunu)
        surname (str): Hasta soyadı (Snowflake'de SURNAME sütunu)
        disease_name (str): Hastalık adı (Snowflake'de DISEASE_NAME sütunu)
    """

    id: Optional[int] = None  # Optional: None olabilir demek (Java'daki @Nullable)
    name: str = ""
    surname: str = ""
    disease_name: str = ""

    @classmethod
    def from_row(cls, row: tuple) -> "SnowflakePatient":
        """
        Veritabanı satırından SnowflakePatient nesnesi oluşturur.

        Factory Method Pattern - Java'daki static factory method'a karşılık gelir.

        Java Karşılığı:
            public static SnowflakePatient fromRow(ResultSet rs) {
                return SnowflakePatient.builder()
                    .id(rs.getLong("ID"))
                    .name(rs.getString("NAME"))
                    .build();
            }

        Args:
            row (tuple): Veritabanından gelen satır (ID, NAME, SURNAME, DISEASE_NAME)

        Returns:
            SnowflakePatient: Oluşturulan nesne
        """
        return cls(
            id=row[0],
            name=row[1] or "",  # None ise boş string
            surname=row[2] or "",
            disease_name=row[3] or ""
        )

    def __repr__(self) -> str:
        """
        Nesnenin string temsilini döner (toString()).
        """
        return f"<SnowflakePatient(id={self.id}, name='{self.name}', surname='{self.surname}')>"
