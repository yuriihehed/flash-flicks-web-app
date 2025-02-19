from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import FlashcardSetForm, FlashcardForm, FlashcardFormSet
from .models import Flashcard, FlashcardSet
from django.forms.models import modelformset_factory
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserProfile
from .models import Folder, Deck, Flashcard, UserProfile, Category, Progress, StudyStreak


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
            return redirect('flashcard_sets_list') # Placeholder
    else:
        set_form = FlashcardSetForm()
        # We pass an empty queryset, so we’re not editing existing cards
        formset = FlashcardFormSet(queryset=Flashcard.objects.none())

    context = {
        'set_form': set_form,
        'formset': formset
    }
    return render(request, 'create_flashcard_set.html', context)

<<<<<<< HEAD
def edit_flashcard_set(request, pk):
    # Retrieve the FlashcardSet instance by its primary key (pk)
    flashcard_set = get_object_or_404(FlashcardSet, pk=pk)

    if request.method == 'POST':
        # If the request method is POST, bind the form and formset to the POST data
        set_form = FlashcardSetForm(request.POST, instance=flashcard_set)
        formset = FlashcardFormSet(request.POST, request.FILES, queryset=flashcard_set.flashcards.all())

        # if its valid save the form and formset
        if set_form.is_valid() and formset.is_valid():
            set_form.save()

            # then save each individual card
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    form.save()
                    
            # redirect to some page, e.g., a list of all flashcard sets
            return redirect('flashcard_sets_list')  # Placeholder
    else:
        # If the request method is GET, populate the form and formset with the existing data
        set_form = FlashcardSetForm(instance=flashcard_set)
        formset = FlashcardFormSet(queryset=flashcard_set.flashcards.all())
        
    # Pass the form, formset, and flashcard set to the template context
    context = {
        'set_form': set_form,
        'formset': formset,
        'flashcard_set': flashcard_set
    }
    # Render the edit_flashcard_set.html template with the context
    return render(request, 'edit_flashcard_set.html', context)
=======


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
>>>>>>> upstream/main
