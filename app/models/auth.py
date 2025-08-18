from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    Boolean,
    DateTime
)
from app.db.database import Base

class Auth(Base):
    __tablename__ = "auth"
    __table_args__= (
        UniqueConstraint("fin_kod"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)
    otp = Column(Integer)
    approved = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)