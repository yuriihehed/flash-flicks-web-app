from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', views.landing_page, name='landing'),
    path('base/', views.base_page, name='base'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)