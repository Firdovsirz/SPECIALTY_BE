from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Faculty(Base):
    __tablename__ = "faculties"
    __table_args__ = (
        UniqueConstraint("faculty_code"),
        UniqueConstraint("faculty_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    university_code = Column(String, ForeignKey("universities.university_code"), nullable=False)
    faculty_code = Column(String, nullable=False, unique=True)
    faculty_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    university = relationship("University", back_populates="faculties")
    cafedras = relationship("Cafedra", back_populates="faculty")