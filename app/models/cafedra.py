from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    UniqueConstraint,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Cafedra(Base):
    __tablename__ = "cafedras"
    __table_args__ = (
        UniqueConstraint("cafedra_code"),
        UniqueConstraint("cafedra_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    university_code = Column(String, ForeignKey("universities.university_code"), nullable=False)
    faculty_code = Column(String, ForeignKey("faculties.faculty_code"), nullable=False)
    cafedra_code = Column(String, nullable=False, unique=True)
    cafedra_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    university = relationship("University", back_populates="cafedras")
    faculty = relationship("Faculty", back_populates="cafedras")
    specialties = relationship("Specialty", back_populates="cafedra")