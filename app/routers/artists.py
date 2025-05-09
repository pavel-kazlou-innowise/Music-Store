from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.models import Artist
from ..schemas.schemas import ArtistCreate, ArtistResponse
from ..utils.security import get_current_admin_user, get_current_user

router = APIRouter(
    prefix="/artists",
    tags=["artists"]
)

@router.post("/", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED, responses={201: {"content": {"application/json": {}}}})
def create_artist(
    artist: ArtistCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """
    Create a new artist (Admin only)
    """
    db_artist = Artist(**artist.dict())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return Response(content=ArtistResponse.model_validate(db_artist).model_dump_json(), media_type="application/json")

@router.get("/", response_model=List[ArtistResponse], responses={200: {"content": {"application/json": {}}}})
def get_artists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """
    Get all artists with pagination (Authenticated users only)
    """
    artists = db.query(Artist).offset(skip).limit(limit).all()
    return Response(content=[ArtistResponse.model_validate(artist).model_dump_json() for artist in artists], media_type="application/json")

@router.get("/{artist_id}", response_model=ArtistResponse, responses={200: {"content": {"application/json": {}}}})
def get_artist(
    artist_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """
    Get artist by ID (Authenticated users only)
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return Response(content=ArtistResponse.model_validate(artist).model_dump_json(), media_type="application/json")

@router.put("/{artist_id}", response_model=ArtistResponse, responses={200: {"content": {"application/json": {}}}})
def update_artist(
    artist_id: int,
    artist: ArtistCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """
    Update artist details (Admin only)
    """
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    for key, value in artist.dict().items():
        setattr(db_artist, key, value)
    
    db.commit()
    db.refresh(db_artist)
    return Response(content=ArtistResponse.model_validate(db_artist).model_dump_json(), media_type="application/json")

@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT, responses={204: {"content": {"application/json": {}}}})
def delete_artist(
    artist_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """
    Delete an artist (Admin only)
    """
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    db.delete(db_artist)
    db.commit()
    return None
