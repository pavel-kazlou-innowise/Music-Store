from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .models.database import engine, Base
from .routers import auth, artists, albums

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Records Store API",
        version="1.0.0",
        description="""
        🎵 Records Store API - Backend for a music store application.
        
        ## Features
        
        * 👤 **Authentication** - JWT-based authentication system
        * 🎨 **Artists** - Manage music artists
        * 💿 **Albums** - Manage music albums with advanced filtering
        * 🛒 **Orders** - Handle customer orders
        * ⭐ **Reviews** - User reviews and ratings
        
        ## Authentication
        
        All protected endpoints require a JWT token. To get a token:
        1. Register a new user (`POST /register`)
        2. Login to get token (`POST /token`)
        3. Use token in Authorization header: `Bearer <token>`
        
        ## Roles
        
        * **Admin** - Can manage all resources
        * **User** - Can view resources and manage own data
        """,
        routes=app.routes,
    )
    
    # Custom tags metadata
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Operations with user authentication and registration",
        },
        {
            "name": "artists",
            "description": "CRUD operations with artists",
        },
        {
            "name": "albums",
            "description": "Manage music albums with filtering and sorting",
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix="/api",
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient permissions"}
    }
)

app.include_router(
    artists.router,
    prefix="/api",
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
        404: {"description": "Artist not found"}
    }
)

app.include_router(
    albums.router,
    prefix="/api",
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
        404: {"description": "Album not found"}
    }
)

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint returning API information and documentation links.
    """
    return {
        "message": "Welcome to Records Store API",
        "documentation": {
            "Swagger UI": "/docs",
            "ReDoc": "/redoc",
            "OpenAPI": "/openapi.json"
        },
        "version": "1.0.0",
        "status": "active"
    }
