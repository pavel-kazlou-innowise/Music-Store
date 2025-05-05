from pydantic import BaseModel, EmailStr, conint, Field
from typing import Optional, List, Dict
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")  # Allow only letters, numbers, underscore and dash

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)  # Minimum 8 characters for password

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}

# Artist schemas
class ArtistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)

class ArtistCreate(ArtistBase):
    pass

class ArtistResponse(ArtistBase):
    id: int
    
    model_config = {"from_attributes": True}

# Album schemas
class AlbumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    release_year: int = Field(..., ge=1900, le=2100)
    genre: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)

class AlbumCreate(AlbumBase):
    artist_id: int = Field(..., ge=1)  # Artist ID must be positive

class AlbumResponse(AlbumBase):
    id: int
    artist: ArtistResponse

    model_config = {"from_attributes": True}

# Track schemas
class TrackBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    duration: int = Field(..., ge=1)  # Duration in seconds must be positive
    track_number: int = Field(..., ge=1)  # Track number must be positive

class TrackCreate(TrackBase):
    album_id: int = Field(..., ge=1)  # Album ID must be positive

class TrackResponse(TrackBase):
    id: int
    album_id: int

    model_config = {"from_attributes": True}

# Order schemas
class OrderItemBase(BaseModel):
    album_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)  # Quantity must be at least 1

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    price_at_time: float

    model_config = {"from_attributes": True}

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    promo_code: Optional[str] = None
    gift_card_code: Optional[str] = None
    use_loyalty_points: Optional[int] = Field(None, ge=0)  # Количество баллов для использования

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    subtotal: float  # Сумма до скидок
    discount_amount: float  # Общая сумма скидок
    points_earned: int  # Начисленные баллы лояльности
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    applied_promo_code: Optional[str] = None
    applied_gift_card: Optional[str] = None
    used_loyalty_points: Optional[int] = None
    discount_details: Optional[Dict] = None  # Детали примененных скидок

    model_config = {"from_attributes": True}

# Review schemas
class ReviewBase(BaseModel):
    rating: conint(ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)  # Optional comment with max length

class ReviewCreate(ReviewBase):
    album_id: int

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    album_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

# Rating schemas
class RatingBase(BaseModel):
    """
    Базовая схема для рейтинга.
    
    Attributes:
        score: Оценка от 1 до 5 звезд
        review_text: Опциональный текст отзыва
    """
    score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Оценка от 1 до 5 звезд",
        example=5,
        title="Рейтинг"
    )
    review_text: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Текст отзыва (от 10 до 2000 символов)",
        example="Отличный альбом! Качество записи превосходное.",
        title="Текст отзыва"
    )

class RatingCreate(RatingBase):
    """
    Схема для создания нового рейтинга.
    
    Attributes:
        album_id: ID альбома
    """
    album_id: int = Field(
        ...,
        gt=0,
        description="ID альбома",
        example=1,
        title="ID альбома"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "score": 5,
                "review_text": "Отличный альбом! Качество записи превосходное.",
                "album_id": 1
            }
        }
    }

class RatingUpdate(BaseModel):
    """
    Схема для обновления рейтинга.
    
    Attributes:
        score: Новая оценка
        review_text: Новый текст отзыва
    """
    score: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Новая оценка от 1 до 5 звезд",
        example=4,
        title="Рейтинг"
    )
    review_text: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Новый текст отзыва",
        example="После нескольких прослушиваний могу сказать...",
        title="Текст отзыва"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "score": 4,
                "review_text": "После нескольких прослушиваний могу сказать..."
            }
        }
    }

class RatingVote(BaseModel):
    """
    Схема для голосования за полезность отзыва.
    
    Attributes:
        is_helpful: Флаг полезности отзыва
    """
    is_helpful: bool = Field(
        ...,
        description="Был ли отзыв полезным",
        example=True,
        title="Полезность"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_helpful": True
            }
        }
    }

class RatingResponse(RatingBase):
    """
    Схема ответа с информацией о рейтинге.
    
    Attributes:
        id: ID рейтинга
        user_id: ID пользователя
        album_id: ID альбома
        is_verified_purchase: Подтвержденная покупка
        helpful_votes: Количество голосов "полезно"
        unhelpful_votes: Количество голосов "бесполезно"
        created_at: Дата создания
        updated_at: Дата обновления
    """
    id: int
    user_id: int
    album_id: int
    is_verified_purchase: bool
    helpful_votes: int
    unhelpful_votes: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class AlbumRatingStats(BaseModel):
    """
    Схема статистики рейтингов альбома.
    
    Attributes:
        album_id: ID альбома
        weighted_rating: Взвешенный рейтинг
        rating_count: Общее количество оценок
        verified_rating_count: Количество оценок от подтвержденных покупателей
        rating_distribution: Распределение оценок
        verified_rating_distribution: Распределение оценок от подтвержденных покупателей
    """
    album_id: int
    weighted_rating: float = Field(..., description="Взвешенный рейтинг с учетом всех факторов")
    rating_count: int = Field(..., description="Общее количество оценок")
    verified_rating_count: int = Field(..., description="Количество оценок от подтвержденных покупателей")
    rating_distribution: Dict[int, int] = Field(..., description="Распределение оценок по звездам")
    verified_rating_distribution: Dict[int, int] = Field(..., description="Распределение оценок от подтвержденных покупателей")

    model_config = {"from_attributes": True}

class UserRatingStats(BaseModel):
    """
    Схема статистики рейтингов пользователя.
    
    Attributes:
        user_id: ID пользователя
        total_ratings: Общее количество отзывов
        average_rating: Средняя оценка
        rating_distribution: Распределение оценок
        helpful_votes_received: Количество полезных голосов
        total_review_length: Общая длина всех отзывов
    """
    user_id: int
    total_ratings: int = Field(..., description="Общее количество отзывов")
    average_rating: float = Field(..., description="Средняя оценка")
    rating_distribution: Dict[int, int] = Field(..., description="Распределение оценок по звездам")
    helpful_votes_received: int = Field(..., description="Количество полезных голосов")
    total_review_length: int = Field(..., description="Общая длина всех отзывов")

    model_config = {"from_attributes": True}

# Gift card schemas
class GiftCardBase(BaseModel):
    code: str = Field(..., min_length=8, max_length=20, pattern="^[A-Z0-9-]+$")
    initial_balance: float = Field(..., gt=0)
    expiry_date: datetime
    is_active: bool = True

class GiftCardCreate(GiftCardBase):
    pass

class GiftCardResponse(GiftCardBase):
    id: int
    current_balance: float
    created_at: datetime

    model_config = {"from_attributes": True}

# Promo code schemas
class PromoCodeBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=20, pattern="^[A-Z0-9_-]+$")
    description: Optional[str] = Field(None, max_length=1000)
    discount_amount: Optional[float] = Field(None, ge=0)
    discount_percent: Optional[int] = Field(None, ge=0, le=100)
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    max_uses: Optional[int] = Field(None, ge=1)
    minimum_order_amount: float = Field(default=0, ge=0)
    is_single_use: bool = False

class PromoCodeCreate(PromoCodeBase):
    pass

class PromoCodeResponse(PromoCodeBase):
    id: int
    uses_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

# Loyalty schemas
class LoyaltyTierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    min_points: int = Field(..., ge=0)
    points_multiplier: float = Field(..., ge=1.0)
    discount_percent: Optional[int] = Field(None, ge=0, le=100)

class LoyaltyTierCreate(LoyaltyTierBase):
    pass

class LoyaltyTierResponse(LoyaltyTierBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class UserLoyaltyBase(BaseModel):
    points: int = Field(default=0, ge=0)
    total_points_earned: int = Field(default=0, ge=0)

class UserLoyaltyResponse(UserLoyaltyBase):
    id: int
    user_id: int
    tier_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    tier: Optional[LoyaltyTierResponse]

    model_config = {"from_attributes": True}

# Discount schemas
class DiscountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    discount_percent: Optional[int] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    start_date: datetime
    end_date: datetime
    is_active: bool = True

class DiscountCreate(DiscountBase):
    pass

class DiscountResponse(DiscountBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
