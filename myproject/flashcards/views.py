from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import FlashcardSetForm, FlashcardForm, FlashcardFormSet
from .models import Flashcard, Folder, FlashcardSet
from django.forms.models import modelformset_factory 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserProfile
from .models import Folder, Flashcard, UserProfile, Category, Progress, StudyStreak
import json


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

def home(request):
    return render(request, 'home.html')

def create_folder(request):
    if request.method == "POST":
        folder_name = request.POST.get("name", "")
        if folder_name:
            folder = Folder.objects.create(name=folder_name)
            return JsonResponse({"success": True, "folder_name": folder.name})
        return JsonResponse({"success": False})

    return render(request, "create_folder.html") 

def folder(request, slug=None):
    # Get the first folder if no slug is provided
    if slug is None:
        folder = Folder.objects.first()
        if folder:
            return redirect('folder', slug=folder.slug)  # Redirect to the first folder's page
        else:
            # If no folders exist, create a general folder representation
            return render(request, 'folder.html', {'folder': None, 'flashcards': []})

    # If slug is provided, get the specified folder
    folder = get_object_or_404(Folder, slug=slug)
    flashcards = Flashcard.objects.filter(flashcard_set__folder=folder)  # Get flashcards via FlashcardSet
    return render(request, 'folder.html', {'folder': folder, 'flashcards': flashcards})


def create_flashcard_set(request):
    # We can also define the formset here if not defined in forms.py
    # FlashcardFormSet = modelformset_factory(Flashcard, form=FlashcardForm, extra=1, can_delete=True)

    if request.method == 'POST':
        set_form = FlashcardSetForm(request.POST)
        formset = FlashcardFormSet(request.POST, request.FILES, queryset=Flashcard.objects.none())

        if set_form.is_valid() and formset.is_valid():
            # Save the flashcard set
            flashcard_set = set_form.save()

            # Save each individual card
            for form in formset:
                # Check that the form has data (to avoid empty forms)
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    flashcard = form.save(commit=False)
                    flashcard.flashcard_set = flashcard_set
                    flashcard.save()

            # Redirect to some page, e.g., a list of all flashcard sets
            return redirect('flashcard_sets_list')
    else:
        set_form = FlashcardSetForm()
        # We pass an empty queryset, so we’re not editing existing cards
        formset = FlashcardFormSet(queryset=Flashcard.objects.none())

    context = {
        'set_form': set_form,
        'formset': formset
    }
    return render(request, 'create_flashcard_set.html', context)



User = get_user_model()

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm")

        if not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, "register.html")

    
        user = User(email=email)
        user.set_password(password)
        user.save()

    
        UserProfile.objects.create(user=user)

        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")

    return render(request, "register.html")

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return redirect("base_page")  # Redirect to home/dashboard
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")
