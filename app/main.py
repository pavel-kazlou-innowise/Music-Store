from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .models.database import engine, Base
from .routers import auth, artists, albums, promotions, ratings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Records Store API",
    description="""
    🎵 Современный API для магазина виниловых пластинок.
    
    ## Основные возможности
    
    * 👤 **Аутентификация** - Система на основе JWT
    * 🎨 **Артисты** - Управление артистами и их каталогами
    * 💿 **Альбомы** - Управление альбомами с расширенной фильтрацией
    * 🛒 **Заказы** - Обработка заказов клиентов
    * ⭐ **Рейтинги** - Система рейтингов и отзывов
    * 🎁 **Акции** - Скидки, промокоды и программа лояльности
    
    ## Рейтинги и отзывы
    
    ### Особенности системы рейтингов:
    * Взвешенный рейтинг с учетом множества факторов
    * Проверка подтвержденных покупок
    * Оценка качества отзывов
    * Система голосования за полезность
    * Защита от накрутки
    
    ### Расчет рейтинга
    Итоговый рейтинг учитывает:
    * Базовую оценку (1-5 звезд)
    * Статус покупателя (verified purchase)
    * Качество отзыва (длина, форматирование)
    * Голоса за полезность
    * Возраст отзыва
    
    ## Аутентификация
    
    Все защищенные эндпоинты требуют JWT токен:
    1. Зарегистрируйте пользователя (`POST /api/auth/register`)
    2. Получите токен (`POST /api/auth/login`)
    3. Используйте токен в заголовке: `Authorization: Bearer <token>`
    
    ## Роли
    
    * **Admin** - Полный доступ к управлению
    * **User** - Доступ к базовому функционалу
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Records Store API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем теги с описаниями
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Операции с аутентификацией и регистрацией",
            "externalDocs": {
                "description": "Подробнее об аутентификации",
                "url": "/api/docs#section/Authentication",
            },
        },
        {
            "name": "artists",
            "description": "Управление артистами",
        },
        {
            "name": "albums",
            "description": "Управление альбомами",
        },
        {
            "name": "ratings",
            "description": """
            Система рейтингов и отзывов.
            
            ### Возможности
            * Создание и редактирование отзывов
            * Голосование за полезность
            * Просмотр статистики
            * Фильтрация и сортировка
            
            ### Особенности
            * Защита от накрутки
            * Взвешенный рейтинг
            * Верификация покупок
            """,
        },
        {
            "name": "promotions",
            "description": "Управление акциями и программой лояльности",
        }
    ]
    
    # Добавляем компоненты безопасности
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT токен доступа. Получите через POST /api/auth/login",
        }
    }
    
    # Добавляем примеры
    openapi_schema["components"]["examples"] = {
        "RatingCreate": {
            "summary": "Пример создания рейтинга",
            "value": {
                "score": 5,
                "review_text": "Отличный альбом! Качество записи превосходное."
            }
        },
        "RatingResponse": {
            "summary": "Пример ответа с рейтингом",
            "value": {
                "id": 1,
                "score": 5,
                "review_text": "Отличный альбом! Качество записи превосходное.",
                "user_id": 1,
                "album_id": 1,
                "is_verified_purchase": True,
                "helpful_votes": 10,
                "unhelpful_votes": 1,
                "created_at": "2025-05-05T10:00:00"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Подключаем роутеры
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"],
    responses={
        401: {"description": "Ошибка аутентификации"},
        403: {"description": "Недостаточно прав"}
    }
)

app.include_router(
    artists.router,
    prefix="/api",
    tags=["artists"],
    responses={
        401: {"description": "Требуется аутентификация"},
        403: {"description": "Требуются права администратора"},
        404: {"description": "Артист не найден"}
    }
)

app.include_router(
    albums.router,
    prefix="/api",
    tags=["albums"],
    responses={
        401: {"description": "Требуется аутентификация"},
        403: {"description": "Требуются права администратора"},
        404: {"description": "Альбом не найден"}
    }
)

app.include_router(
    ratings.router,
    prefix="/api",
    tags=["ratings"],
    responses={
        401: {"description": "Требуется аутентификация"},
        403: {"description": "Нет прав на выполнение операции"},
        404: {"description": "Ресурс не найден"},
        422: {"description": "Ошибка валидации данных"}
    }
)

app.include_router(
    promotions.router,
    prefix="/api",
    tags=["promotions"],
    responses={
        401: {"description": "Требуется аутентификация"},
        403: {"description": "Требуются права администратора"},
        404: {"description": "Ресурс не найден"},
        400: {"description": "Некорректный запрос"}
    }
)

@app.get("/", tags=["root"])
async def root():
    """
    Корневой эндпоинт API.
    Возвращает базовую информацию о сервисе.
    """
    return {
        "name": "Records Store API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }
