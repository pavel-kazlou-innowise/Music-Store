from app.utils.admin import create_admin

# Создаем первого админа
create_admin(
    username="admin",
    email="admin@example.com",
    password="admin123"  # В реальном проекте используйте сложный пароль!
)
