from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestDataCreate(BaseModel):
    test_name: str
    timestamp: Optional[datetime] = None
    temperature: float
    speed: float
    altitude: float
    passed: bool

class ReportData(BaseModel):
    test_name: str
    temperature: float
    speed: float
    altitude: float