from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import AuditLog
from app.auth import check_role

router = APIRouter(prefix="/logs", tags=["Audit Logs"])

@router.get("/")
async def get_audit_logs(db: AsyncSession = Depends(get_db), user=Depends(lambda: check_role("admin"))):
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()))
    return result.scalars().all()