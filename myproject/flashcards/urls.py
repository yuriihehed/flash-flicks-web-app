from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  
    path('base/', views.base_page, name='base_page'),
    path('studypage/', views.studypage, name='studypage'),
    path('edit-learn-mode/', views.edit_learn_mode, name='edit_learn_mode'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'), 
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # FOR FUTURE PASSWORD RESET FUNCTIONALITY
    path('signup/', views.signup, name='signup'),  # Temporary placeholder
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)