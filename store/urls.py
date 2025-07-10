from django.urls import path
from . import views

urlpatterns = [
    path('sentjur-merch/', views.sentjur_merch, name='sentjur-merch'),
    path('smarski-merch/', views.smarski_merch, name='smarski-merch'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('kontakt/', views.kontakt, name='kontakt'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('vojzek/', views.cart_view, name='vojzek'),
    path('checkout/', views.checkout, name='checkout'),
    path('stripe_pay/', views.stripe_pay, name='stripe_pay'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),



]
