from django.urls import path
from . import views

urlpatterns = [
    path('smarski-merch/', views.glasovanje, name='smarski-merch'),
    path('forumcek/', views.forum, name='forum'),

]