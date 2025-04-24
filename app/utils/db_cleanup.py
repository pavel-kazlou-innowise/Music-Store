from sqlalchemy import MetaData
from ..models.database import engine

def clear_database():
    """Clear all data from the database."""
    meta = MetaData()
    meta.reflect(bind=engine)
    
    # Удаляем все данные из всех таблиц
    with engine.begin() as conn:
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())
