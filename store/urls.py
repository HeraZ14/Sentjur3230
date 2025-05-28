from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name = 'home'),
    path('sentjur-merch/', views.sentjur_merch, name='sentjur-merch'),
]
