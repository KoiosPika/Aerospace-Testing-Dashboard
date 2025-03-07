import firebase_admin
from firebase_admin import auth, credentials
from dotenv import load_dotenv
import os

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

def set_custom_claims(user_email, role):
    """Assigns a role (engineer/admin) to a Firebase user"""
    try:
        user = auth.get_user_by_email(user_email)
        auth.set_custom_user_claims(user.uid, {"role": role})
        print(f"Role '{role}' assigned to {user_email}")
    except Exception as e:
        print(f"Error assigning role: {e}")

if __name__ == "__main__":
    user_email = input("Enter user email: ")
    role = input("Enter role (engineer/admin): ")
    set_custom_claims(user_email, role)