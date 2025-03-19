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
from .views import forgot_password_view, reset_password_view

def logout_view(request):
    logout(request)
    return redirect('/login/')

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  
    path('base/', views.base_page, name='base_page'),
    path('studypage/<int:set_id>/', views.studypage, name='studypage'),    
    path('edit-learn-mode/', views.edit_learn_mode, name='edit_learn_mode'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    
    path('create-flashcard-set', views.create_flashcard_set, name='create_flashcard_set'), # need the homepage to function properly first
    path('edit-flashcard-set/<int:pk>/', views.edit_flashcard_set, name='edit_flashcard_set'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('landing_page')), name='logout'),
    path('learning-styles/', views.learning_page, name='learning'),
    
    #flashcards
    path('update_flashcard_text/<int:term_id>/', views.update_flashcard, name='update_flashcard_text'),
    path('update_star_status/<int:term_id>/', views.update_star_status, name='update_star_status'),

    # Settings
    path('settings/', views.accounts_settings, name='settings'),
    
    #Home Page
    path('homepage/', views.home, name='home'), 
    
    
    #Folder
    path('folder/<slug:slug>/', views.folder_detail, name='folder_detail'),
    path('folder/', views.folder_list, name='folder_list'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('flashcards/<int:set_id>/', views.flashcard_set_details, name='flashcard_set_details'),
    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('delete-folder/', views.delete_folder, name='delete_folder'),


    #Calender
    
    path('calendar/', views.calendar_view, name='calendar'),
    path('get-events/', views.get_events, name='get-events'),
    path('add-event/', views.add_event, name='add-event'),
    path('update-event/', views.update_event, name='update-event'),
    path('delete-event/', views.delete_event, name='delete-event'),

    path('update_flashcard_status/<int:flashcard_id>/', update_flashcard_status, name='update_flashcard_status'),
    # for the search bar
    path('search/<int:set_id>/', views.search_terms, name='search_terms'),
    # for the flashcard set deteteing
    path('sets/<int:set_id>/delete/', views.delete_flashcard_set, name='delete_flashcard_set'),

    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset/<uidb64>/<token>/', reset_password_view, name='reset_password'),
    
    # Update Learn Settings
    path('update_learn_settings/', views.update_learn_settings, name='update_learn_settings'),
    
    
    path('create-test-flashcard-set/', views.create_test_flashcard_set, name='create_test_flashcard_set'),

    path('about/', views.about_page, name='about'),
]

#if settings.DEBUG:path('learning-styles/', views.learning_page, name='learning')
  #  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
