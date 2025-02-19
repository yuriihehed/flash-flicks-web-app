from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserProfile
from .models import Folder, Deck, Flashcard, UserProfile, Category, Progress, StudyStreak

from .forms import FlashcardSetForm, FlashcardForm, FlashcardFormSet
from .models import Flashcard
from django.forms.models import modelformset_factory


def landing_page(request):
   return render(request, 'landing.html')

def base_page(request):
   return render(request, 'base.html')

def studypage(request):
    cards = range(1, 7)  # Example card range
    return render(request, 'studypage.html', {'cards': cards})

def edit_learn_mode(request):
    return render(request, 'edit_learn_mode.html')

def signup(request):
    return HttpResponse("Signup page coming soon!")  # Placeholder

def forgot_password(request):
    return render(request, 'forgot_password.html')

def homepage(request):
    return render(request, 'homepage.html')