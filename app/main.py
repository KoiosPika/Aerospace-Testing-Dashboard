from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from app.database import engine
from app.models import Base
from app.routes import test_data, reports, audit_logs
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_data.router)
app.include_router(reports.router)
app.include_router(audit_logs.router)

@app.get("/")
def home():
    return {"message": "Aerospace Testing API is running!"}

# ✅ WebSocket for Real-Time Updates
@app.websocket("/ws/test-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT * FROM test_data ORDER BY timestamp DESC LIMIT 10"))
                rows = result.fetchall()
                
                data = [
                    {
                        "id": row.id,
                        "test_name": row.test_name,
                        "timestamp": row.timestamp.isoformat(),
                        "temperature": row.temperature,
                        "speed": row.speed,
                        "altitude": row.altitude,
                        "passed": row.passed
                    }
                    for row in rows
                ]
                
                await websocket.send_text(json.dumps(data))
            
            await asyncio.sleep(2)  # Update every 2 seconds
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")

# ✅ Ensure app runs properly when executed as script
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)