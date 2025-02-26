from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path

def logout_view(request):
    logout(request)
    return redirect('/login/')

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  
    path('base/', views.base_page, name='base_page'),
    path('studypage/', views.studypage, name='studypage'),    
    path('edit-learn-mode/', views.edit_learn_mode, name='edit_learn_mode'),
    path('login/', views.login_page, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('register/', views.register, name='register'),
    
    path('create-flashcard-set', views.create_flashcard_set, name='create_flashcard_set'), # need the homepage to function properly first
    path('edit-flashcard-set/<int:pk>/', views.edit_flashcard_set, name='edit_flashcard_set'), # for the edit page of the flashcard set
    path('logout/', logout_view, name='logout'), #logout
    path('learning-styles/', views.learning_page, name='learning'),
    
    
    #Home Page
    path('homepage/', views.home, name='home'), 
    
    
    #Folder
    path('folder/<slug:slug>/', views.folder_detail, name='folder_detail'),
    path('folder/', views.folder_list, name='folder_list'),
    
    path('create-folder/', views.create_folder, name='create_folder'),

]

#if settings.DEBUG:path('lea