from django.urls import path
from . import views

urlpatterns = [
    # Главная страница — лента постов
    path('', views.home, name='home'),

    # Аутентификация пользователей
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Создание контента
    path('create_post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),



    # Взаимодействие с постами (лайки через AJAX)
    path('like/<int:post_id>/', views.LikePostView.as_view(), name='like_post'),

    # Управление подписками
    path('subscribe/<int:user_id>/', views.subscribe, name='subscribe'),
    path('unsubscribe/<int:user_id>/', views.unsubscribe, name='unsubscribe'),

    # Профили пользователей
    path('profile/<int:user_id>/', views.profile, name='profile'),

    # Поиск
    path('search/', views.search, name='search'),

    path('post/<int:post_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

]
