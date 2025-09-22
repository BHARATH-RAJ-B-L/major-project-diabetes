# backend/app/seed_admin.py
"""
Run this once to create the admin user.
"""
import sys
from pathlib import Path
import warnings

# Suppress bcrypt warnings
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

# Add backend directory to path for relative imports
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.db import SessionLocal, engine
from app.models import Base
from app.crud import create_user, get_user_by_username

# create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
admin_username = "bharath raj"
admin_email = "bhbl22csaiml@cmrit.ac.in"
admin_password = "majorproject"

try:
    if get_user_by_username(db, admin_username):
        print("Admin already exists")
    else:
        create_user(db, admin_username, admin_email, admin_password, is_admin=True)
        print("Admin created successfully")
finally:
    db.close()
