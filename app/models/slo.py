# slo model
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class Slo(Base):
    __tablename__ = "slo"
    
    id = Column(Integer, primary_key=True, index=True)
    university_code = Column(String, ForeignKey("universities.university_code"), nullable=False)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)
    slo_code = Column(String, nullable=False, unique=True)

    university = relationship("University", back_populates="slos")
    specialty = relationship("Specialty", back_populates="slos")
    translations = relationship("SloTranslation", back_populates="slo")





