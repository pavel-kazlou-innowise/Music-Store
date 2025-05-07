from app.models.database import SessionLocal
from app.models.models import User
from app.utils.security import get_password_hash

def register_user(username: str, email: str, password: str):
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if user:
            print(f"User {username} already exists")
            return
        
        # Create user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True  # Первый пользователь становится админом
        )
        
        db.add(new_user)
        db.commit()
        print(f"User {username} created successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем админа с паролем из теста
    register_user("admin", "admin@example.com", "stringst")
    # Создаем тестового пользователя
    register_user("TestUser", "test@example.com", "TestUser") 