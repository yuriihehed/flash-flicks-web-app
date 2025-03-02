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
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Event
from datetime import datetime, timedelta
from .models import Flashcard


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

@login_required
def home(request):
    # Get only the current user's folders
    folders = Folder.objects.filter(user=request.user).annotate(flashcardSet_count=Count("flashcard_sets"))
    
    # Get only the current user's flashcard sets
    deck = FlashcardSet.objects.filter(user=request.user).annotate(flashcard_count=Count("flashcards"))
    
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
    
    # Add user_folders to context for sidebar
    user_folders = Folder.objects.filter(user=request.user)
    
    return render(request, 'home.html', {
        'folders': folders, 
        "flashcard_sets": deck,
        "user_folders": user_folders  # This is needed for the sidebar
    })

@login_required
def folder_list(request):
    """View for showing all folders and flashcard sets in the 'General' folder"""
    folders = Folder.objects.filter(user=request.user)
    general_folder = Folder.objects.filter(user=request.user, name="General").first()
    flashcard_sets = FlashcardSet.objects.filter(folder=general_folder) if general_folder else []

    return render(request, 'folder.html', {
        'folders': folders,
        'flashcard_sets': flashcard_sets  # Now available in the template
    })

@login_required
def folder_detail(request, slug):
    """View for showing a specific folder and its contents"""
    if not slug:
        return redirect('folder_list')
    
    try:
        # Handle the 'general' folder case
        if slug == 'general':
            # You might need to create a general folder if it doesn't exist
            folder, created = Folder.objects.get_or_create(
                name="General", 
                user=request.user,
                defaults={'slug': 'general'}
            )
        else:
            folder = get_object_or_404(Folder, slug=slug, user=request.user)
        
        # Get flashcard sets belonging to this folder
        flashcard_sets = FlashcardSet.objects.filter(folder=folder, user=request.user)

        
        context = {
            'folder': folder,
            'flashcard_sets': flashcard_sets,
            'folders': Folder.objects.filter(user=request.user)  # For sidebar
        }
        return render(request, 'folder_detail.html', context)
    
    except Folder.DoesNotExist:
        messages.error(request, "Folder not found.")
        return redirect('folder_list')

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
# @login_required
# def create_flashcard_set(request):
#     # We can also define the formset here if not defined in forms.py
#     # FlashcardFormSet = modelformset_factory(Flashcard, form=FlashcardForm, extra=1, can_delete=True)

#     if request.method == 'POST':
#         set_form = FlashcardSetForm(request.POST, email=request.user.email)
#         formset = FlashcardFormSet(request.POST, request.FILES, queryset=Flashcard.objects.none())

#         if set_form.is_valid() and formset.is_valid():
#             # Save the flashcard set
#             flashcard_set = set_form.save()

#             # Save each individual card
#             valid_card_count = 0
#             for form in formset:
#                 # Check that the form has data (to avoid empty forms)
#                 if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
#                     flashcard = form.save(commit=False)
#                     flashcard.flashcard_set = flashcard_set
#                     flashcard.save()
#                     valid_card_count += 1
#             if valid_card_count < 2:
#                 # Optionally, add an error message and re-render the form
#                 messages.error(request, "You must add at least two flashcards.")
#                 # You might choose to delete the flashcard_set or not save it yet
#                 return render(request, 'create_flashcard_set.html', {'set_form': set_form, 'formset': formset})

#             # Redirect to some page, e.g., a list of all flashcard sets
#             return redirect('flashcard_set_details', set_id=flashcard_set.id) # Placeholder
#     else:
#         set_form = FlashcardSetForm(email=request.user.email)
#         # We pass an empty queryset, so we’re not editing existing cards
#         formset = FlashcardFormSet(queryset=Flashcard.objects.none())

#     context = {
#         'set_form': set_form,
#         'formset': formset
#     }
#     return render(request, 'create_flashcard_set.html', context)

@login_required
def create_flashcard_set(request):
    if request.method == 'POST':
        set_form = FlashcardSetForm(request.POST, email=request.user.email)
        formset = FlashcardFormSet(request.POST, request.FILES, queryset=Flashcard.objects.none())

        if set_form.is_valid() and formset.is_valid():
            # Create but don't save the flashcard set yet
            flashcard_set = set_form.save(commit=False)
            
            # Set the user manually
            flashcard_set.user = request.user
            
            # Now save the flashcard set with the user assigned
            flashcard_set.save()

            # Save each individual card
            valid_card_count = 0
            for form in formset:
                # Check that the form has data (to avoid empty forms)
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    flashcard = form.save(commit=False)
                    flashcard.flashcard_set = flashcard_set
                    flashcard.save()
                    valid_card_count += 1
                    
            if valid_card_count < 2:
                # If not enough valid cards, handle the error
                flashcard_set.delete()  # Delete the flashcard set since it doesn't have enough cards
                messages.error(request, "You must add at least two flashcards.")
                return render(request, 'create_flashcard_set.html', {'set_form': set_form, 'formset': formset})

            # Redirect to the detail view
            return redirect('flashcard_set_details', set_id=flashcard_set.id)
    else:
        set_form = FlashcardSetForm(email=request.user.email)
        formset = FlashcardFormSet(queryset=Flashcard.objects.none())

    # Add the user's folders for sidebar display
    user_folders = Folder.objects.filter(user=request.user)
    
    context = {
        'set_form': set_form,
        'formset': formset,
        'user_folders': user_folders
    }
    return render(request, 'create_flashcard_set.html', context)

# def edit_flashcard_set(request, pk):
#     # Retrieve the FlashcardSet instance by its primary key (pk)
#     flashcard_set = get_object_or_404(FlashcardSet, pk=pk)

#     if request.method == 'POST':
#         # If the request method is POST, bind the form and formset to the POST data
#         set_form = FlashcardSetForm(request.POST, instance=flashcard_set)
#         formset = FlashcardFormSet(request.POST, request.FILES, queryset=flashcard_set.flashcards.all())

#         # if its valid save the form and formset
#         if set_form.is_valid() and formset.is_valid():
#             set_form.save()

#             # then save each individual card
#             for form in formset:
#                 if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
#                     flashcard = form.save(commit=False)
#                     flashcard.flashcard_set = flashcard_set  # assign the foreign key
#                     flashcard.save()
                    
#             # redirect to some page, e.g., a list of all flashcard sets
#             return redirect('flashcard_set_details',set_id=flashcard_set.id)  # Placeholder
#     else:
#         # If the request method is GET, populate the form and formset with the existing data
#         set_form = FlashcardSetForm(instance=flashcard_set)
#         formset = FlashcardFormSet(queryset=flashcard_set.flashcards.all())
        
#     # Pass the form, formset, and flashcard set to the template context
#     context = {
#         'set_form': set_form,
#         'formset': formset,
#         'flashcard_set': flashcard_set
#     }
#     # Render the edit_flashcard_set.html template with the context
#     return render(request, 'edit_flashcard_set.html', context)

@login_required
def edit_flashcard_set(request, pk):
    # Retrieve the FlashcardSet instance by its primary key (pk)
    flashcard_set = get_object_or_404(FlashcardSet, pk=pk, user=request.user)  # Ensure user owns this set

    if request.method == 'POST':
        # If the request method is POST, bind the form and formset to the POST data
        set_form = FlashcardSetForm(request.POST, instance=flashcard_set, email=request.user.email)
        formset = FlashcardFormSet(request.POST, request.FILES, queryset=flashcard_set.flashcards.all())

        # if its valid save the form and formset
        if set_form.is_valid() and formset.is_valid():
            # Save the set, ensuring user is set
            flashcard_set = set_form.save(commit=False)
            flashcard_set.user = request.user  # Make sure user is set
            flashcard_set.save()

            # Process deleted cards
            for form in formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()

            # then save each individual card
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    flashcard = form.save(commit=False)
                    flashcard.flashcard_set = flashcard_set  # assign the foreign key
                    flashcard.save()
                    
            # redirect to the detail view
            return redirect('flashcard_set_details', set_id=flashcard_set.id)
    else:
        # If the request method is GET, populate the form and formset with the existing data
        set_form = FlashcardSetForm(instance=flashcard_set, email=request.user.email)
        formset = FlashcardFormSet(queryset=flashcard_set.flashcards.all())
    
    # Get user folders for sidebar
    user_folders = Folder.objects.filter(user=request.user)
        
    # Pass the form, formset, and flashcard set to the template context
    context = {
        'set_form': set_form,
        'formset': formset,
        'flashcard_set': flashcard_set,
        'user_folders': user_folders
    }
    # Render the edit_flashcard_set.html template with the context
    return render(request, 'edit_flashcard_set.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Flashcard

@csrf_exempt  # Only use if CSRF token is not available
def update_flashcard(request, term_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            term = data.get("term", "").strip()
            definition = data.get("definition", "").strip()

            flashcard = Flashcard.objects.get(id=term_id)
            flashcard.term = term
            flashcard.definition = definition
            flashcard.save()

            return JsonResponse({"success": True})
        except Flashcard.DoesNotExist:
            return JsonResponse({"success": False, "error": "Flashcard not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request"})


User = get_user_model()

def register(request):
    if request.method == "POST":
        name = request.POST.get("name") 
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

    
        user = User(email=email, first_name=name)
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

def learning_page(request):
    return render(request, 'learning.html')

@login_required
def flashcard_set_details(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    terms = flashcard_set.flashcards.all()

    for term in terms:
        term.is_learned = term.learned_by.filter(id=request.user.id).exists()

    return render(request, 'set_page.html', {
        'flashcard_set': flashcard_set,
        'terms': terms,
    })










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

def learning_page(request):
    return render(request, 'learning.html')


#calender page


def calendar_view(request):
    return render(request, 'calendar.html')  # This is the new calendar page

def generate_recurring_events(event):
    occurrences = []
    base_date = event.date  # Changed from `start_date` to `date`

    for i in range(10):  # Generate up to 10 future occurrences
        if event.recurring_type == 'daily':
            new_date = base_date + timedelta(days=i)
        elif event.recurring_type == 'weekly':
            new_date = base_date + timedelta(weeks=i)
        elif event.recurring_type == 'monthly':
            new_date = base_date.replace(month=base_date.month + i)

        occurrences.append({
            "id": event.id,
            "title": event.title,
            "class_name": event.class_name,
            "start_time": event.start_time.strftime("%I:%M %p"),
            "end_time": event.end_time.strftime("%I:%M %p"),
            "start": new_date.strftime("%Y-%m-%d"),
            "is_recurring": event.is_recurring,
            "recurring_type": event.recurring_type
        })

    return occurrences
@csrf_exempt
def get_events(request):
    events = Event.objects.all()
    event_list = []

    for event in events:
        if event.is_recurring:
            event_list.extend(generate_recurring_events(event))  # Use fixed function
        else:
            event_list.append({
                "id": event.id,
                "title": event.title,
                "class_name": event.class_name,
                "start_time": event.start_time.strftime("%I:%M %p"),
                "end_time": event.end_time.strftime("%I:%M %p"),
                "start": event.date.strftime("%Y-%m-%d"),  # Changed from `start_date` to `date`
                "is_recurring": event.is_recurring,
                "recurring_type": event.recurring_type
            })

    return JsonResponse(event_list, safe=False)








@csrf_exempt
def add_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        class_name = data.get('class_name', '')
        date = data.get('date')
        start_time = data.get('start_time', '00:00:00')
        end_time = data.get('end_time', '23:59:59')
        is_recurring = data.get('is_recurring', False)
        recurring_type = data.get('recurring_type')

        if not title or not date or not start_time or not end_time:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        event = Event.objects.create(
            title=title,
            class_name=class_name,
            date=date,
            start_time=start_time,
            end_time=end_time,
            is_recurring=is_recurring,
            recurring_type=recurring_type
        )

        return JsonResponse({"message": "Event added successfully"})
    
@csrf_exempt
def delete_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_id = data.get('id')
        delete_all = data.get('delete_all', False)

        try:
            event = Event.objects.get(id=event_id)

            if delete_all and event.is_recurring:
                # ✅ Delete all events that share the same title, class, and recurrence type
                Event.objects.filter(
                    title=event.title,
                    class_name=event.class_name,
                    recurring_type=event.recurring_type
                ).delete()
                return JsonResponse({"message": "All occurrences of the event deleted successfully"})

            elif event.is_recurring:
                # ✅ Delete only this specific occurrence
                event.delete()
                return JsonResponse({"message": "This occurrence of the event was deleted"})

            else:
                # ✅ Delete non-recurring event
                event.delete()
                return JsonResponse({"message": "Non-recurring event deleted successfully"})

        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)



@csrf_exempt
def update_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_id = data.get('id')

        try:
            event = Event.objects.get(id=event_id)

            event.title = data.get('title', event.title)
            event.class_name = data.get('class_name', event.class_name)

            # Convert date string to a proper Date object
            date_str = data.get('date', event.date)
            event.date = datetime.strptime(date_str, "%Y-%m-%d").date() if isinstance(date_str, str) else date_str

            # Convert time strings to proper Time objects
            start_time_str = data.get('start_time', event.start_time)
            end_time_str = data.get('end_time', event.end_time)

            event.start_time = datetime.strptime(start_time_str, "%H:%M").time() if isinstance(start_time_str, str) else start_time_str
            event.end_time = datetime.strptime(end_time_str, "%H:%M").time() if isinstance(end_time_str, str) else end_time_str

            event.is_recurring = data.get('is_recurring', event.is_recurring)
            event.recurring_type = data.get('recurring_type', event.recurring_type)

            event.save()

            return JsonResponse({"message": "Event updated successfully"})
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)


@csrf_exempt
@login_required
def update_flashcard_status(request, flashcard_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            learned = data.get("learned")

            flashcard = Flashcard.objects.get(id=flashcard_id)

            if learned:
                flashcard.learned_by.add(request.user)
                print(f"✅ {request.user.email} marked flashcard {flashcard.term} as learned.")
            else:
                flashcard.learned_by.remove(request.user)
                print(f"❌ {request.user.email} marked flashcard {flashcard.term} as NOT learned.")

            flashcard.save()

            # Debugging: Confirm update
            print(f"📌 Saved status: {flashcard.learned_by.all()}")

            return JsonResponse({"success": True, "learned": learned})
        except Flashcard.DoesNotExist:
            return JsonResponse({"success": False, "error": "Flashcard not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


@csrf_exempt
def update_star_status(request, term_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            favorite = data.get("favorite", False)  # True/False from the JS

            flashcard = Flashcard.objects.get(id=term_id)
            flashcard.is_favorite = favorite
            flashcard.save()

            return JsonResponse({"success": True})
        except Flashcard.DoesNotExist:
            return JsonResponse({"success": False, "error": "Flashcard not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})
