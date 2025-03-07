import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from botocore.config import Config
from fastapi import APIRouter, HTTPException
from app.schemas import ReportData
import io
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/reports", tags=["Reports"])

BUCKET_NAME = "aerospace-test-reports"
AWS_REGION = "us-east-2"

s3 = boto3.client("s3",region_name = AWS_REGION, config=Config(signature_version="s3v4"))


@router.post("/")
async def generate_report(report_data: ReportData):
    try:
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer)
        pdf.drawString(100, 750, f"Test Report: {report_data.test_name}")
        pdf.drawString(100, 730, f"Temperature: {report_data.temperature}°C")
        pdf.drawString(100, 710, f"Speed: {report_data.speed} m/s")
        pdf.drawString(100, 690, f"Altitude: {report_data.altitude} m")
        pdf.save()
        pdf_buffer.seek(0)

        file_name = f"{report_data.test_name}.pdf"
        s3_key = f"reports/{file_name}"
        s3.upload_fileobj(pdf_buffer, BUCKET_NAME, s3_key)

        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,
        )

        return {"message": "Report generated successfully", "url": presigned_url}

    except (BotoCoreError, NoCredentialsError) as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
