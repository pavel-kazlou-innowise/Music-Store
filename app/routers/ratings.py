from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.models import Rating, User, Album
from ..schemas.schemas import RatingCreate, RatingUpdate, RatingResponse, RatingVote
from ..schemas.schemas import AlbumRatingStats, UserRatingStats
from ..services.rating_service import RatingService
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=RatingResponse)
def create_rating(
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создает новый рейтинг для альбома."""
    # Проверяем существование альбома
    album = db.query(Album).filter(Album.id == rating.album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
        
    # Проверяем, не оставлял ли пользователь уже рейтинг
    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.album_id == rating.album_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=400,
            detail="You have already rated this album"
        )
        
    # Проверяем, покупал ли пользователь альбом
    is_verified = db.query(Album)\
        .join(Album.orders)\
        .filter(
            Album.id == rating.album_id,
            Album.orders.any(user_id=current_user.id)
        ).first() is not None
        
    # Создаем рейтинг
    db_rating = Rating(
        user_id=current_user.id,
        album_id=rating.album_id,
        score=rating.score,
        is_verified_purchase=is_verified,
        review_text_length=len(rating.review_text) if rating.review_text else 0
    )
    
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    # Обновляем рейтинг альбома
    RatingService.update_album_rating(db, rating.album_id)
    
    return db_rating

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновляет существующий рейтинг."""
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
        
    if db_rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your rating")
        
    db_rating.score = rating.score
    db_rating.review_text_length = len(rating.review_text) if rating.review_text else 0
    
    db.commit()
    db.refresh(db_rating)
    
    # Обновляем рейтинг альбома
    RatingService.update_album_rating(db, db_rating.album_id)
    
    return db_rating

@router.post("/{rating_id}/vote")
def vote_for_rating(
    rating_id: int,
    vote: RatingVote,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Голосует за полезность рейтинга."""
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
        
    # Проверяем, не голосовал ли пользователь уже
    existing_vote = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.votes.any(user_id=current_user.id)
    ).first()
    
    if existing_vote:
        raise HTTPException(
            status_code=400,
            detail="You have already voted for this rating"
        )
        
    # Обновляем счетчики
    if vote.is_helpful:
        db_rating.helpful_votes += 1
    else:
        db_rating.unhelpful_votes += 1
        
    db.commit()
    
    return {"status": "success"}

@router.get("/albums/{album_id}/stats", response_model=AlbumRatingStats)
def get_album_stats(
    album_id: int,
    db: Session = Depends(get_db)
):
    """Получает статистику рейтингов для альбома."""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
        
    return RatingService.get_album_rating_stats(db, album_id)

@router.get("/users/{user_id}/stats", response_model=UserRatingStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получает статистику рейтингов пользователя."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return RatingService.get_user_rating_stats(db, user_id)
