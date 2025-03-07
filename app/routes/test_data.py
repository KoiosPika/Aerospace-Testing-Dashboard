from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from app.database import get_db
from app.models import TestData
from app.schemas import TestDataCreate
from app.auth import verify_firebase_token, check_role
from app.utils import log_activity
from typing import Optional
from datetime import datetime
from weasyprint import HTML
from jinja2 import Template

router = APIRouter(prefix="/test-data", tags=["Test Data"])

@router.post("/", response_model=TestDataCreate)
async def add_test_data(
    test_data: TestDataCreate, 
    db: AsyncSession = Depends(get_db), 
    user=Depends(verify_firebase_token)
):
    new_test = TestData(
        test_name=test_data.test_name,
        temperature=test_data.temperature,
        speed=test_data.speed,
        altitude=test_data.altitude,
        passed=test_data.passed
    )
    db.add(new_test)
    await db.commit()
    await db.refresh(new_test)
    return new_test

@router.get("/")
async def get_all_test_data(db: AsyncSession = Depends(get_db), user=Depends(verify_firebase_token)):
    await log_activity(db, user['uid'], "VIEW", "Viewed test data")
    result = await db.execute(select(TestData))
    return result.scalars().all()

@router.delete("/{test_id}")
async def delete_test_data(
    test_id: int, 
    db: AsyncSession = Depends(get_db), 
    user=Depends(lambda: check_role("admin"))
):
    result = await db.execute(select(TestData).where(TestData.id == test_id))
    test_entry = result.scalars().first()
    
    if not test_entry:
        raise HTTPException(status_code=404, detail="Test data not found")

    await log_activity(db, user['uid'], "DELETE", f"Deleted test data ID {test_id}")
    await db.delete(test_entry)
    await db.commit()
    return {"message": "Test data deleted successfully"}

@router.get("/report", response_class=Response)
async def generate_pdf_report(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestData))
    test_data = result.scalars().all()

    if not test_data:
        raise HTTPException(status_code=404, detail="No test data available")

    template = Template("""
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { text-align: center; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Aerospace Test Report</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Test Name</th>
                <th>Temperature</th>
                <th>Speed</th>
                <th>Altitude</th>
                <th>Status</th>
            </tr>
            {% for test in test_data %}
            <tr>
                <td>{{ test.id }}</td>
                <td>{{ test.test_name }}</td>
                <td>{{ test.temperature }}</td>
                <td>{{ test.speed }}</td>
                <td>{{ test.altitude }}</td>
                <td>{{ "Passed" if test.passed else "Failed" }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """)

    html_content = template.render(test_data=test_data)
    
    pdf = HTML(string=html_content).write_pdf()

    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=test_report.pdf"})