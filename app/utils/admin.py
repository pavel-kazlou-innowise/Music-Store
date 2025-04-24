from sqlalchemy.orm import Session
from ..models.database import get_db, engine
from ..models.models import User
from .security import get_password_hash

def create_admin(username: str, email: str, password: str):
    """
    Create an admin user directly in the database.
    Use this script to create the first admin user.
    """
    db = Session(engine)
    try:
        # Check if user exists
        user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if user:
            print(f"User {username} already exists")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True
        )
        
        db.add(admin)
        db.commit()
        print(f"Admin user {username} created successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Пример использования:
    # create_admin("admin", "admin@example.com", "your-secure-password")
