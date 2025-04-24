from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

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
    
    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")
    reviews = relationship("Review", back_populates="album")

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
    total_amount = Column(Float)
    status = Column(String)  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

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
