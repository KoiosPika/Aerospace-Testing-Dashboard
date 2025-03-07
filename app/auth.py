import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

security = HTTPBearer()

async def verify_firebase_token(token: HTTPAuthorizationCredentials = Security(security)):
    """Verify Firebase ID Token and extract user info"""
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
async def check_role(required_role: str, token: dict = Depends(verify_firebase_token)):
    """Check if user has the required role"""
    user_role = token.get("role")
    if not user_role or user_role != required_role:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return token

