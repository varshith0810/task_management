"""
Seed script – creates a default admin user on first run.
Safe to run multiple times (checks before inserting).
"""
 
from app.db.session import SessionLocal
from app.models.models import User, GlobalRole
from app.core.security import hash_password
 
 
DEFAULT_EMAIL    = "admin@taskmanager.com"
DEFAULT_PASSWORD = "Admin@1234"
DEFAULT_NAME     = "Admin"
 
 
def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=DEFAULT_EMAIL).first()
        if existing:
            print(f"[seed] Admin user already exists: {DEFAULT_EMAIL}")
            return
 
        admin = User(
            email=DEFAULT_EMAIL,
            full_name=DEFAULT_NAME,
            hashed_password=hash_password(DEFAULT_PASSWORD),
            role=GlobalRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"[seed] Admin user created: {DEFAULT_EMAIL} / {DEFAULT_PASSWORD}")
    finally:
        db.close()
 
 
if __name__ == "__main__":
    seed()
