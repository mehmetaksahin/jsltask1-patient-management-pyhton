"""
Patient Entity - PostgreSQL Modeli

Bu dosya PostgreSQL'deki 'tbl_patient' tablosunu temsil eder.

Java Karşılaştırması:
--------------------
Java (Patient.java):
    @Entity
    @Table(name = "tbl_patient")
    public class Patient {
        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long id;

        @Column(name = "name", nullable = false, length = 100)
        private String name;
        ...
    }

Python (patient.py):
    class Patient(PostgreSQLBase):
        __tablename__ = "tbl_patient"

        id = Column(BigInteger, primary_key=True, autoincrement=True)
        name = Column(String(100), nullable=False)
        ...

Temel Farklılıklar:
------------------
1. Java'da @Entity annotation → Python'da Base sınıfından miras
2. Java'da @Table(name=...) → Python'da __tablename__ = ...
3. Java'da @Column → Python'da Column() fonksiyonu
4. Java'da Lombok @Getter @Setter → Python'da otomatik (property erişimi)
5. Java'da @Builder → Python'da __init__ veya dataclass
"""

from sqlalchemy import Column, BigInteger, String
from app.config.database import PostgreSQLBase


class Patient(PostgreSQLBase):
    """
    PostgreSQL Patient entity sınıfı.

    Bu sınıf, veritabanındaki tbl_patient tablosunu temsil eder.
    Her instance bir hasta kaydına karşılık gelir.

    Attributes:
        id (int): Birincil anahtar, otomatik artan
        name (str): Hasta adı, maksimum 100 karakter
        surname (str): Hasta soyadı, maksimum 100 karakter
        disease_name (str): Hastalık adı, maksimum 200 karakter
    """

    # Tablo adı - Java'daki @Table(name = "tbl_patient") karşılığı
    __tablename__ = "tbl_patient"

    # Sütun tanımlamaları
    # Java'daki @Id @GeneratedValue(strategy = GenerationType.IDENTITY) karşılığı
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Birincil anahtar, otomatik artan"
    )

    # Java'daki @Column(name = "name", nullable = false, length = 100) karşılığı
    name = Column(
        String(100),
        nullable=False,
        comment="Hasta adı"
    )

    # Java'daki @Column(name = "surname", nullable = false, length = 100) karşılığı
    surname = Column(
        String(100),
        nullable=False,
        comment="Hasta soyadı"
    )

    # Java'daki @Column(name = "disease_name", nullable = false, length = 200) karşılığı
    disease_name = Column(
        String(200),
        nullable=False,
        comment="Hastalık adı"
    )

    def __repr__(self) -> str:
        """
        Nesnenin string temsilini döner.

        Java'daki toString() metoduna karşılık gelir.
        Debug ve loglama için kullanılır.

        Returns:
            str: Patient nesnesinin okunabilir gösterimi
        """
        return f"<Patient(id={self.id}, name='{self.name}', surname='{self.surname}')>"

    def to_dict(self) -> dict:
        """
        Nesneyi dictionary'ye dönüştürür.

        JSON serialization için kullanılır.
        Java'da genellikle Jackson otomatik yapar, Python'da manuel tanımlanabilir.

        Returns:
            dict: Patient verilerini içeren dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "disease_name": self.disease_name
        }
