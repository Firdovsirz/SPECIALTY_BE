from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Specialty(Base):
    __tablename__ = "specialties"
    __table_args__ = (
        UniqueConstraint("specialty_code"),
        UniqueConstraint("specialty_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    university_code = Column(String, ForeignKey("universities.university_code"), nullable=False)
    cafedra_code = Column(String, ForeignKey("cafedras.cafedra_code"), nullable=False)
    specialty_code = Column(String, nullable=False, unique=True)
    specialty_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    university = relationship("University", back_populates="specialties")
    cafedra = relationship("Cafedra", back_populates="specialties")