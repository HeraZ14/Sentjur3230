from django.contrib import admin
from django.urls import path, include
from . import settings, views
from django.conf.urls.static import static
from .views import preview_page
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name = 'home'),
    path('kontakt/',views.kontakt, name = 'kontakt'),
    path('', include('zajebancija.urls')),
    path('',include('store.urls')),
    path('', include('accounts.urls')),
    path("preview/<slug:slug>/", preview_page, name="page-preview"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


