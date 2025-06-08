from django.urls import path
from . import views
from .views import profile_view, custom_login

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('login/', views.custom_login, name='login'),
]
