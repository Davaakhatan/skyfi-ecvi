"""Script to create an admin user"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_admin_user(username: str, email: str, password: str):
    """Create an admin user"""
    db: Session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists!")
            return False
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user '{username}' created successfully!")
        print(f"User ID: {admin_user.id}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_admin_user(username, email, password)

