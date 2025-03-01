from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy
from django.urls import path
from .views import update_flashcard  # <-- Add this line
from .views import update_flashcard_status

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
    path('edit-flashcard-set/<int:pk>/', views.edit_flashcard_set, name='edit_flashcard_set'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('landing_page')), name='logout'),
    path('learning-styles/', views.learning_page, name='learning'),
    
    #flashcards
    path('update_flashcard/<int:flashcard_id>/', update_flashcard, name='update_flashcard'),
    
    #Home Page
    path('homepage/', views.home, name='home'), 
    
    
    #Folder
    path('folder/<slug:slug>/', views.folder_detail, name='folder_detail'),
    path('folder/', views.folder_list, name='folder_list'),
    
    path('create-folder/', views.create_folder, name='create_folder'),
    
    path('flashcards/<int:set_id>/', views.flashcard_set_details, name='flashcard_set_details'),

    #Calender
    
    path('calendar/', views.calendar_view, name='calendar'),
    path('get-events/', views.get_events, name='get-events'),
    path('add-event/', views.add_event, name='add-event'),
    path('update-event/', views.update_event, name='update-event'),
    path('delete-event/', views.delete_event, name='delete-event'),

    path('update_flashcard_status/<int:flashcard_id>/', update_flashcard_status, name='update_flashcard_status'),


]

#if settings.DEBUG:path('learning-styles/', views.learning_page, name='learning')
  #  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)