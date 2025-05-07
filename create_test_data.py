from app.models.database import SessionLocal
from app.models.models import Artist, Album
from app.utils.security import get_password_hash

def create_test_data():
    db = SessionLocal()
    try:
        # Create artists
        artists = [
            Artist(name="AT_Artist1", description="Test artist 1"),
            Artist(name="AT_Artist2", description="Test artist 2"),
            Artist(name="Other Artist", description="Not matching artist")
        ]
        for artist in artists:
            db.add(artist)
        db.commit()

        # Create albums
        albums = [
            Album(
                title="AT_Album1",
                artist_id=artists[0].id,
                release_year=2020,
                genre="ROCK",
                price=500.0,
                stock=10
            ),
            Album(
                title="AT_Album2",
                artist_id=artists[1].id,
                release_year=2021,
                genre="ROCK",
                price=750.0,
                stock=5
            ),
            Album(
                title="Other Album",
                artist_id=artists[2].id,
                release_year=2022,
                genre="POP",
                price=1000.0,
                stock=3
            )
        ]
        for album in albums:
            db.add(album)
        db.commit()
        print("Test data created successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 