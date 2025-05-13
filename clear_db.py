import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.utils.db_cleanup import clear_database

if __name__ == "__main__":
    # Load variables from .env file into environment
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not set in .env file or environment")

    print("DATABASE_URL from .env:", db_url)

    # Create engine using the loaded URL
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    clear_database(engine)

    print("Database cleared successfully")
