from sqlalchemy import MetaData

def clear_database(engine):
    """Clear all data from the database."""
    meta = MetaData()
    meta.reflect(bind=engine)

    with engine.begin() as conn:
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())
