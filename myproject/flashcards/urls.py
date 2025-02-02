from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView

# from .views import CustomLoginView

urlpatterns = [
    
    path('', views.landing_page, name='landing'),
    path('', views.base_page, name='base'),
]