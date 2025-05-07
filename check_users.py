from app.models.database import SessionLocal, engine
from app.models.models import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users in database")
        else:
            for user in users:
                print(f"User: {user.username}, Email: {user.email}, Is Admin: {user.is_admin}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 