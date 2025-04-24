from pydantic import BaseModel, EmailStr, conint
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Artist schemas
class ArtistBase(BaseModel):
    name: str
    description: Optional[str] = None

class ArtistCreate(ArtistBase):
    pass

class ArtistResponse(ArtistBase):
    id: int
    
    class Config:
        orm_mode = True

# Album schemas
class AlbumBase(BaseModel):
    title: str
    release_year: int
    genre: str
    price: float
    stock: int

class AlbumCreate(AlbumBase):
    artist_id: int

class AlbumResponse(AlbumBase):
    id: int
    artist: ArtistResponse

    class Config:
        orm_mode = True

# Track schemas
class TrackBase(BaseModel):
    title: str
    duration: int
    track_number: int

class TrackCreate(TrackBase):
    album_id: int

class TrackResponse(TrackBase):
    id: int
    album_id: int

    class Config:
        orm_mode = True

# Order schemas
class OrderItemBase(BaseModel):
    album_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    price_at_time: float

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True

# Review schemas
class ReviewBase(BaseModel):
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    album_id: int

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    album_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
