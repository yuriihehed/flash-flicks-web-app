from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', views.landing_page, name='landing_page'),  
    path('base/', views.base_page, name='base_page'),
    path('studypage/', views.studypage, name='studypage'),
    path('edit-learn-mode/', views.edit_learn_mode, name='edit_learn_mode'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)