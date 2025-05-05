from .auth import router as auth_router
from .artists import router as artists_router
from .albums import router as albums_router
from .promotions import router as promotions_router
from .ratings import router as ratings_router

__all__ = ["auth_router", "artists_router", "albums_router", "promotions_router", "ratings_router"]
