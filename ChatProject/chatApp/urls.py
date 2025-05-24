from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('index/', views.index, name='index'),
    path('chat/<str:room_name>/', views.room, name='room'),
    path('logout/', views.logout_view, name='logout'),
]
