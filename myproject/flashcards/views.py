from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import FlashcardSetForm, FlashcardForm, FlashcardFormSet
from django.forms.models import modelformset_factory 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from .models import Folder, Flashcard, UserProfile, Category, Progress, StudyStreak, FlashcardSet, UserProfile
from django.db.models import Count
import json
from .models import Folder
from django.views.decorators.http import require_POST
from django.utils.text import slugify



def landing_page(request):
    ensure_superuser()
    return render(request, 'landing.html')

def base_page(request):
    return render(request, 'base.html')

def studypage(request):
    cards = range(1, 7)  # Example card range
    return render(request, 'studypage.html', {'cards': cards})

def edit_learn_mode(request):
    return render(request, 'edit_learn_mode.html')

def forgot_password(request):
    return render(request, 'forgot_password.html')

def home(request):
    folders = Folder.objects.all().annotate(flashcardSet_count=Count("flashcard_sets"))
    deck = FlashcardSet.objects.all().annotate(flashcard_count=Count("flashcards"))
    
    if request.method == "POST":
        # Get folder name from form submission
        folder_name = request.POST.get("name", "").strip()

        if not folder_name:
            messages.error(request, "Folder name cannot be empty.")
        else:
            # Create the folder
            Folder.objects.create(user=request.user, name=folder_name)
            messages.success(request, "Folder created successfully!")

        return redirect("homepage")
    return render(request, 'home.html', {'folders': folders, "flashcard_sets": deck})

def folder_list(request):
    general_folder, created = Folder.objects.get_or_create(
        name="General",
        user=request.user,
        defaults={'slug': 'general'}
    )
    """View for showing all folders"""

    folders = Folder.objects.filter(user=request.user)
    return render(request, 'folder.html', {'folders': folders})

def folder_detail(request, slug):
    """View for showing a specific folder and its contents"""
    if not slug or slug == 'general':
        # Get or create the general folder
        folder, created = Folder.objects.get_or_create(
            name="General",
            user=request.user,
            defaults={'slug': 'general'}
        )
    else:
        try:
            folder = get_object_or_404(Folder, slug=slug, user=request.user)
        except Folder.DoesNotExist:
            messages.error(request, "Folder not found.")
            return redirect('folder_list')
    # if not slug:
    #     return redirect('folder_list')
    
    # try:
    #     # Handle the 'general' folder case
    #     if slug == 'general':
    #         # You might need to create a general folder if it doesn't exist
    #         folder, created = Folder.objects.get_or_create(
    #             name="General", 
    #             user=request.user,
    #             defaults={'slug': 'general'}
    #         )
    #     else:
    #         folder = get_object_or_404(Folder, slug=slug, user=request.user)
        
        # Get flashcard sets belonging to this folder
        flashcard_sets = FlashcardSet.objects.filter(folder=folder)
        
        context = {
            'folder': folder,
            'flashcard_sets': flashcard_sets,
            'folders': Folder.objects.filter(user=request.user)  # For sidebar
        }
        return render(request, 'folder_detail.html', context)


@require_POST
def create_folder(request):
    """View for creating a new folder via AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        name = request.POST.get('name', '').strip()
        
        # Validate folder name
        if not name:
            return JsonResponse({'success': False, 'error': 'Folder name is required'})
        
        # Generate a slug from the name
        base_slug = slugify(name)
        slug = base_slug
        
        # If slug already exists, make it unique
        counter = 1
        while Folder.objects.filter(slug=slug, user=request.user).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create the folder
        folder = Folder.objects.create(
            name=name,
            slug=slug,
            user=request.user
        )
        
        return JsonResponse({
            'success': True, 
            'folder_name': folder.name,
            'folder_slug': folder.slug,
            'redirect_url': f'/folder/{folder.slug}/'  # Include redirect URL if needed
        })
        
    except Exception as e:
        # Log the error for debugging
        print(f"Folder creation error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

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
            return redirect("home")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")

def ensure_superuser():
    User = get_user_model()
    admin_email = "admin@hotmail.com"  
    admin_password = "Password"  

    if not User.objects.filter(email=admin_email).exists():
        superuser = User(email=admin_email, is_staff=True, is_superuser=True)
        superuser.set_password(admin_password)
        superuser.save()
        print(f"Superuser {admin_email} created automatically.")
    else:
        print(f"Superuser {admin_email} already exists.")