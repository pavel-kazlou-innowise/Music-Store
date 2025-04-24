# Records Store API

🎵 Backend API for a music store application built with FastAPI and SQLAlchemy.

## Features

* 👤 **Authentication** - JWT-based authentication system
* 🎨 **Artists** - Manage music artists
* 💿 **Albums** - Manage music albums with advanced filtering
* 🛒 **Orders** - Handle customer orders
* ⭐ **Reviews** - User reviews and ratings

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd records-store
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Setup

1. Install Python 3.10:
```bash
# Windows
# Download from https://www.python.org/downloads/release/python-31011/
```

2. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Run the application:
```bash
poetry run uvicorn app.main:app --reload
```

## Project Structure

```
records-store/
├── app/
│   ├── core/          # Configuration
│   ├── models/        # Database models
│   ├── routers/       # API endpoints
│   ├── schemas/       # Pydantic models
│   └── utils/         # Utilities
├── tests/             # Test files
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## Environment Variables

- `DATABASE_URL`: SQLite database URL
- `SECRET_KEY`: Secret key for JWT
- `API_V1_STR`: API version prefix
- `PROJECT_NAME`: Project name

## Contributing

1. Create a new branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License.
