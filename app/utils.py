from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog

async def log_activity(db: AsyncSession, user_id: str, action: str, details: str = None):
    log_entry = AuditLog(user_id=user_id, action=action, details=details)
    db.add(log_entry)
    await db.commit()