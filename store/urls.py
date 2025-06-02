from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name = 'home'),
    path('sentjur-merch/', views.sentjur_merch, name='sentjur-merch'),
    path('ostali-merch/', views.ostali_merch, name='ostali-merch'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('kontakt/', views.kontakt, name='kontakt'),


]
