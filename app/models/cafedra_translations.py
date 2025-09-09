from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    UniqueConstraint,
    CheckConstraint
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Cafedra(Base):
    __tablename__ = "cafedras"
    __table_args__ = (
        UniqueConstraint("cafedra_code"),
        UniqueConstraint("cafedra_name"),
        CheckConstraint("lang_code IN ('az', 'en')")
    )

    id = Column(Integer, primary_key=True, index=True)
    lang_code = Column(String(2), nullable=False)
    cafedra_code = Column(String, nullable=False, unique=True)
    cafedra_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    specialties = relationship("Specialty", back_populates="cafedra")