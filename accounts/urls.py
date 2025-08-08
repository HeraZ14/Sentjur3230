from django.urls import path
from . import views
from .views import profile_view, custom_login, custom_logout, CustomPasswordResetDoneView, CustomPasswordResetCompleteView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('accounts/login/', custom_login.as_view(), name='login'),
    path('logout/', custom_logout.as_view(), name='logout'),

    # Forgot password flow:
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('password-change/', views.change_password, name='password_change'),

]
