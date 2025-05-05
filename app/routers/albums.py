from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.database import get_db
from ..models.models import Album, Artist
from ..schemas.schemas import AlbumCreate, AlbumResponse
from ..utils.security import get_current_admin_user, get_current_user

router = APIRouter(
    prefix="/albums",
    tags=["albums"]
)

@router.post("/", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
def create_album(
    album: AlbumCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """
    Create a new album (Admin only)
    """
    # Check if artist exists
    artist = db.query(Artist).filter(Artist.id == album.artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    db_album = Album(**album.dict())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

@router.get("/", response_model=List[AlbumResponse])
def get_albums(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, enum=["price_asc", "price_desc", "title", "year"]),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """
    Get all albums with filtering, sorting and pagination (Authenticated users only)
    """
    query = db.query(Album)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Album.title.ilike(f"%{search}%"),
                Album.genre.ilike(f"%{search}%")
            )
        )
    if genre:
        query = query.filter(Album.genre == genre)
    if min_price is not None:
        query = query.filter(Album.price >= min_price)
    if max_price is not None:
        query = query.filter(Album.price <= max_price)
    
    # Apply sorting
    if sort_by:
        if sort_by == "price_asc":
            query = query.order_by(Album.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Album.price.desc())
        elif sort_by == "title":
            query = query.order_by(Album.title.asc())
        elif sort_by == "year":
            query = query.order_by(Album.release_year.desc())
    
    # Apply pagination
    albums = query.offset(skip).limit(limit).all()
    return albums

@router.get("/{album_id}", response_model=AlbumResponse)
def get_album(
    album_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """
    Get album by ID (Authenticated users only)
    """
    album = db.query(Album).filter(Album.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.put("/{album_id}", response_model=AlbumResponse)
def update_album(
    album_id: int,
    album: AlbumCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """
    Update album details (Admin only)
    """
    db_album = db.query(Album).filter(Album.id == album_id).first()
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    
    # Check if artist exists
    artist = db.query(Artist).filter(Artist.id == album.artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    for key, value in album.dict().items():
        setattr(db_album, key, value)
    
    db.commit()
    db.refresh(db_album)
    return db_album

@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(
    album_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """
    Delete an album (Admin only)
    """
    db_album = db.query(Album).filter(Album.id == album_id).first()
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    
    db.delete(db_album)
    db.commit()
    return None
