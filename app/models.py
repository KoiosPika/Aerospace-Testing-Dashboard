from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class TestData(Base):
    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    passed = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(String, nullable=True)