from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Otp(Base):
    __tablename__ = "otp"
    __table_args__= (
        UniqueConstraint("fin_kod"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String, nullable=False, unique=True)
    otp = Column(Integer, nullable=False)
    otp_expires_at = Column(DateTime, nullable=False)

    # auth = relationship("Auth", back_populates="otp")