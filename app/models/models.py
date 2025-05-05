from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import func

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    loyalty = relationship("UserLoyalty", back_populates="user", uselist=False)
    promo_code_usages = relationship("PromoCodeUsage", back_populates="user")
    loyalty_transactions = relationship("LoyaltyPointTransaction", back_populates="user")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    rating_votes = relationship("RatingVote", back_populates="user", cascade="all, delete-orphan")

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    
    albums = relationship("Album", back_populates="artist")

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    release_year = Column(Integer)
    genre = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    weighted_rating = Column(Float, default=0.0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    verified_rating_count = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index('ix_albums_weighted_rating', 'weighted_rating'),
        Index('ix_albums_rating_count', 'rating_count'),
    )
    
    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")
    reviews = relationship("Review", back_populates="album")
    ratings = relationship("Rating", back_populates="album", cascade="all, delete-orphan")

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"))
    duration = Column(Integer)  # duration in seconds
    track_number = Column(Integer)
    
    album = relationship("Album", back_populates="tracks")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)  # Сумма до скидок
    discount_amount = Column(Float, default=0)  # Общая сумма скидок
    points_earned = Column(Integer, default=0)  # Начисленные баллы лояльности
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Примененные скидки
    applied_promo_code = Column(String)  # Код примененного промокода
    applied_gift_card = Column(String)  # Код примененной подарочной карты
    used_loyalty_points = Column(Integer)  # Использованные баллы лояльности
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    promo_code_usages = relationship("PromoCodeUsage", back_populates="order")
    gift_card_transactions = relationship("GiftCardTransaction", back_populates="order")
    loyalty_point_transactions = relationship("LoyaltyPointTransaction", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    album_id = Column(Integer, ForeignKey("albums.id"))
    quantity = Column(Integer)
    price_at_time = Column(Float)
    
    order = relationship("Order", back_populates="items")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    album_id = Column(Integer, ForeignKey("albums.id"))
    rating = Column(Integer)  # 1-5
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")
    album = relationship("Album", back_populates="reviews")

class PromoCodeUsage(Base):
    __tablename__ = "promo_code_usages"

    id = Column(Integer, primary_key=True, index=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    used_at = Column(DateTime, default=func.now())

    promo_code = relationship("PromoCode", back_populates="usages")
    user = relationship("User", back_populates="promo_code_usages")
    order = relationship("Order", back_populates="promo_code_usages")

class GiftCardTransaction(Base):
    __tablename__ = "gift_card_transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    gift_card_id = Column(Integer, ForeignKey("gift_cards.id"))
    amount = Column(Float)
    used_at = Column(DateTime, default=func.now())
    
    order = relationship("Order", back_populates="gift_card_transactions")
    gift_card = relationship("GiftCard", back_populates="transactions")

class LoyaltyPointTransaction(Base):
    __tablename__ = "loyalty_point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    points = Column(Integer)
    used_at = Column(DateTime, default=func.now())
    
    order = relationship("Order", back_populates="loyalty_point_transactions")
    user = relationship("User", back_populates="loyalty_transactions")

class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    discount_amount = Column(Float, nullable=False)
    discount_percent = Column(Integer)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer)
    uses_count = Column(Integer, default=0)
    minimum_order_amount = Column(Float, default=0)
    is_single_use = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    usages = relationship("PromoCodeUsage", back_populates="promo_code")

class GiftCard(Base):
    __tablename__ = "gift_cards"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    initial_balance = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    transactions = relationship("GiftCardTransaction", back_populates="gift_card")

class Rating(Base):
    """
    Модель рейтинга/отзыва для альбома.
    
    Attributes:
        id: Уникальный идентификатор
        user_id: ID пользователя
        album_id: ID альбома
        score: Оценка (1-5)
        is_verified_purchase: Флаг подтвержденной покупки
        created_at: Дата создания
        updated_at: Дата обновления
        review_text_length: Длина текста отзыва
        helpful_votes: Количество голосов "полезно"
        unhelpful_votes: Количество голосов "бесполезно"
    """
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    is_verified_purchase = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    review_text_length = Column(Integer, default=0)
    helpful_votes = Column(Integer, default=0)
    unhelpful_votes = Column(Integer, default=0)
    
    __table_args__ = (
        Index('ix_ratings_user_album', 'user_id', 'album_id', unique=True),  # Уникальный индекс
        Index('ix_ratings_score', 'score'),  # Индекс для агрегации
        Index('ix_ratings_created_at', 'created_at'),  # Индекс для сортировки по дате
    )
    
    user = relationship("User", back_populates="ratings")
    album = relationship("Album", back_populates="ratings")
    votes = relationship("RatingVote", back_populates="rating", cascade="all, delete-orphan")

class RatingVote(Base):
    """
    Модель голоса за полезность отзыва.
    
    Attributes:
        id: Уникальный идентификатор
        rating_id: ID рейтинга
        user_id: ID пользователя
        is_helpful: Флаг полезности
        created_at: Дата голосования
    """
    __tablename__ = "rating_votes"

    id = Column(Integer, primary_key=True, index=True)
    rating_id = Column(Integer, ForeignKey("ratings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_helpful = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('ix_rating_votes_user_rating', 'user_id', 'rating_id', unique=True),
    )
    
    rating = relationship("Rating", back_populates="votes")
    user = relationship("User", back_populates="rating_votes")
