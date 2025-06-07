from django.urls import path
from . import views

urlpatterns = [
    path('sentjur-merch/', views.sentjur_merch, name='sentjur-merch'),
    path('ostali-merch/', views.ostali_merch, name='ostali-merch'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('kontakt/', views.kontakt, name='kontakt'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('vojzek/', views.cart_view, name='vojzek'),


]
