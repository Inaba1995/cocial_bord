from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),

    # Основные URL приложения social (главная страница и все остальные маршруты)
    path('', include('social.urls')),
]

# Обслуживание медиа‑файлов в режиме разработки
# ВАЖНО: этот блок работает только в режиме DEBUG = True
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    # Дополнительно можно добавить обслуживание статических файлов
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
