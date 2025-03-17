from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import FlashcardSetForm, FlashcardForm, FlashcardFormSet
from django.forms.models import modelformset_factory 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.models import User
from .models import Folder, Flashcard, UserProfile, Category, Progress, StudyStreak, FlashcardSet
from django.db.models import Count
import json
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Event
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def landing_page(request):
    #ensure_superuser()
    return render(request, 'landing.html')

def base_page(request):
    return render(request, 'base.html')
    
def about_page(request):
    return render(request, 'about.html')

def studypage(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    terms = flashcard_set.flashcards.all()

    for term in terms:
        term.is_learned = term.learned_by.filter(id=request.user.id).exists()
    return render(request, 'studypage.html', {
        'flashcard_set': flashcard_set,
        'terms': terms,
        })

def edit_learn_mode(request):
    return render(request, 'edit_learn_mode.html')

#Forgot Password

def forgot_password(request):
    return render(request, 'forgot_password.html')
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")
            return redirect('forgot_password')

        # Generate a token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset URL (e.g., https://yourdomain.com/reset/<uid>/<token>/ )
        reset_url = request.build_absolute_uri(
            reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
        )

        # Send email
        subject = "Reset Your FlashFlicks Password"
        from_email = settings.EMAIL_HOST_USER
        to_email = [user.email]

        # Render the HTML message
        html_content = render_to_string('email_templates/reset_password_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        # Optionally render a plain-text fallback
        plain_content = (
            f"Hi {user.first_name or user.username},\n\n"
            f"Please click the link to reset your password:\n{reset_url}\n\n"
            "If you did not request this, ignore this email."
        )

        send_mail(
            subject,
            plain_content,          # Plain-text fallback
            from_email,
            to_email,
            fail_silently=False,
            html_message=html_content  # The HTML version
        )

        messages.success(request, "A password reset link has been sent to your email.")
        return redirect('forgot_password')

    return render(request, 'forgot_password.html')

def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Token is valid; allow user to change password
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                user.set_password(password)
                user.save()

                messages.success(request, "Your password has been reset successfully. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match. Try again.")

        return render(request, 'reset_password.html', {'validlink': True})
    else:
        # Invalid or expired link
        messages.error(request, "This link is invalid or has expired.")
        return redirect('forgot_password')


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
def accounts_settings(request):
    if request.method == "POST":
        field = request.POST.get("field")
        value = request.POST.get("value")

        if field and value:
            user = request.user  # Get the logged-in user
            if field == "username":
                user.first_name = value
            elif field == "password":
                confirm_password = request.POST.get("confirm_password")
                if value != confirm_password:
                    messages.error(request, "Passwords do not match!")
                    return redirect("settings")
                user.set_password(value)  # Encrypts new password
                user.save()
                update_session_auth_hash(request, user)  # Prevent logout
                login(request, user)  # Log the user back in
                messages.success(request, "Password updated successfully!")
                return redirect("settings")
            user.save()
            messages.success(request, f"{field.capitalize()} updated successfully!")
            return redirect("settings")  # Redirect to account settings
    return render(request, 'accounts_settings.html')    

@login_required
def folder_list(request):
    """View for showing all folders and flashcard sets without a folder"""
    folders = Folder.objects.filter(user=request.user)
    
    # Get flashcard sets that don't have a folder assigned
    flashcard_sets_without_folder = FlashcardSet.objects.filter(user=request.user, folder=None)

    return render(request, 'folder.html', {
        'folders': folders,
        'flashcard_sets': flashcard_sets_without_folder  # Now shows sets without a folder
    })


@login_required
def folder_detail(request, slug):
    """View for showing a specific folder and its contents"""
    if not slug:
        return redirect('folder_list')
    
    try:
        # Get the specific folder (no special case for General anymore)
        folder = get_object_or_404(Folder, slug=slug, user=request.user)
        
        flashcard_sets = FlashcardSet.objects.filter(folder=folder, user=request.user) \
        .annotate(flashcard_count=Count('flashcards'))
        
        context = {
            'folder': folder,
            'flashcard_sets': flashcard_sets,
            
            'folders': Folder.objects.filter(user=request.user)  # For sidebar
        }
        return render(request, 'folder_detail.html', context)
    
    except Folder.DoesNotExist:
        messages.error(request, "Folder not found.")
        return redirect('folder_list')
    

def folder_view(request):
    folders = Folder.objects.filter(user=request.user)
    flashcard_sets_without_folder = FlashcardSet.objects.filter(user=request.user, folder=None)
    
    return render(request, 'folder.html', {
        'folders': folders,
        'flashcard_sets_without_folder': flashcard_sets_without_folder
    })

@require_POST
def create_folder(request):
    """View for creating a new folder via AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        name = request.POST.get('name', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Folder name is required'})
        
        # Generate a slug from the name
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        # Ensure slug is unique per user
        while Folder.objects.filter(user=request.user, slug=slug).exists():
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
            'redirect_url': f'/folder/{folder.slug}/'
        })
        
    except Exception as e:
        print(f"Folder creation error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})



# @login_required
# @require_POST
# def delete_folder(request):
#     """View for deleting a folder and its contents"""
#     try:
#         # Decode JSON request body
#         data = json.loads(request.body)
#         folder_id = data.get('folder_id')  # Get the folder_id from the request body

#         # Ensure folder exists and belongs to current user
#         folder = get_object_or_404(Folder, id=folder_id, user=request.user)
        
#         folder_name = folder.name
#         folder.delete()
        
#         messages.success(request, f'Folder "{folder_name}" was successfully deleted.')
        
#         return JsonResponse({
#             'success': True,
#             'redirect_url': reverse('folder_list')  # Redirect to folder list
#         })
#     except Folder.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Folder not found.'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_folder(request):
    """View for deleting a folder and its contents"""
    try:
        data = json.loads(request.body)
        folder_id = data.get('folder_id')

        folder = get_object_or_404(Folder, id=folder_id, user=request.user)
        folder_name = folder.name
        folder.delete()

        return JsonResponse({
            'success': True,
            'message': f'Folder "{folder_name}" was successfully deleted.',
            'redirect_url': reverse('folder_list')
        })
    except Folder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Folder not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    
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

# This view is for testing purposes only.
def create_test_flashcard_set(request):
    # Get the current user (or choose a specific user if desired)
    user = request.user

    # Create a flashcard set programmatically
    flashcard_set = FlashcardSet.objects.create(
        title="Test Coding",
        description="A test set of coding terms and definitions.",
        user=user
    )
    # A dictionary of 100 coding terms and definitions
    coding_terms = {
        "variable": "A storage location identified by a memory address and an associated symbolic name.",
        "function": "A block of code designed to perform a specific task.",
        "class": "A blueprint for creating objects.",
        "object": "An instance of a class containing data and behavior.",
        "inheritance": "A mechanism where a new class uses the properties of an existing class.",
        "encapsulation": "The bundling of data with the methods that operate on that data.",
        "polymorphism": "The ability of different objects to be accessed through the same interface.",
        "abstraction": "The process of hiding complex implementation details and showing only essential features.",
        "algorithm": "A step-by-step procedure for solving a problem.",
        "recursion": "A function calling itself to solve a problem.",
        "iteration": "Repeating a block of code until a condition is met.",
        "loop": "A sequence of instructions that repeats until a condition is satisfied.",
        "array": "A data structure consisting of a collection of elements.",
        "list": "An ordered collection of items.",
        "tuple": "An immutable ordered collection of elements.",
        "dictionary": "A collection of key-value pairs.",
        "set": "A collection of unique elements.",
        "string": "A sequence of characters.",
        "integer": "A whole number, positive or negative, without decimals.",
        "float": "A number that has a decimal place.",
        "boolean": "A data type with two possible values: True or False.",
        "operator": "A symbol that tells the compiler or interpreter to perform specific mathematical or logical manipulations.",
        "condition": "An expression that evaluates to True or False.",
        "loop control": "Statements like break and continue that control the flow of loops.",
        "exception": "An event that occurs during the execution of a program that disrupts the normal flow.",
        "error": "A mistake in the code that prevents correct execution.",
        "debugging": "The process of finding and fixing errors in the code.",
        "comment": "A piece of text in the code that is ignored during execution.",
        "syntax": "The set of rules that defines the combinations of symbols considered correctly structured.",
        "semicolon": "A punctuation mark used to separate statements in some programming languages.",
        "compiler": "A program that translates code into executable machine language.",
        "interpreter": "A program that executes code directly, translating it line by line.",
        "bytecode": "A form of instruction set designed for efficient execution by a software interpreter.",
        "runtime": "The period during which a program is running.",
        "framework": "A platform for developing software applications.",
        "library": "A collection of precompiled routines that a program can use.",
        "API": "Application Programming Interface, a set of functions and procedures allowing the creation of applications.",
        "module": "A file containing Python definitions and statements.",
        "package": "A way of organizing related modules into a single directory hierarchy.",
        "loop variable": "A variable that takes on the value of each element in an iterable.",
        "recursion depth": "The maximum number of recursive calls before reaching an error.",
        "lambda": "An anonymous function expressed as a single statement.",
        "closure": "A record storing a function together with an environment.",
        "generator": "A function that returns an iterator which yields one value at a time.",
        "iterator": "An object representing a stream of data.",
        "comprehension": "A concise way to create lists, dictionaries, or sets.",
        "decorator": "A function that modifies the behavior of another function.",
        "multithreading": "The ability of a CPU to execute multiple threads concurrently.",
        "concurrency": "The execution of multiple instruction sequences at the same time.",
        "parallelism": "The simultaneous execution of multiple computations.",
        "asynchronous": "Operations that occur without waiting for previous ones to complete.",
        "synchronous": "Operations that occur in sequence, each waiting for the previous to finish.",
        "I/O": "Input/Output, operations that involve data exchange between the computer and the external world.",
        "file handling": "Techniques to read from and write to files.",
        "database": "A structured set of data held in a computer.",
        "SQL": "Structured Query Language, used to manage relational databases.",
        "query": "A request for information from a database.",
        "transaction": "A unit of work that is performed against a database.",
        "commit": "To save changes in a database.",
        "rollback": "To undo changes in a database transaction.",
        "join": "An operation to combine rows from two or more tables.",
        "index": "A data structure that improves the speed of data retrieval operations.",
        "normalization": "The process of organizing data to reduce redundancy.",
        "denormalization": "The process of attempting to optimize the read performance of a database.",
        "constraint": "A rule enforced on data columns in a table.",
        "primary key": "A unique identifier for a table record.",
        "foreign key": "A field in one table that uniquely identifies a row in another table.",
        "migration": "The process of moving data between databases.",
        "branch": "A parallel version of a repository.",
        "merge": "Combining multiple sequences of commits into one unified history.",
        "pull request": "A request to merge code changes.",
        "repository": "A central location where data is stored and managed.",
        "clone": "A copy of a repository.",
        "fork": "A personal copy of someone else's project.",
        "continuous integration": "A development practice where developers integrate code into a shared repository frequently.",
        "continuous deployment": "A strategy for software releases where any commit that passes tests is automatically deployed.",
        "unit test": "A test that validates a small, isolated piece of code.",
        "integration test": "A test that verifies the interactions between components.",
        "system test": "A test of the complete and integrated software system.",
        "test-driven development": "A development process where tests are written before code.",
        "mock": "A simulated object that mimics the behavior of real objects in controlled ways.",
        "stub": "A minimal implementation of an interface used during testing.",
        "patch": "A set of changes to a computer program designed to update, fix, or improve it.",
        "refactoring": "The process of restructuring existing computer code without changing its external behavior.",
        "code review": "The systematic examination of computer source code.",
        "profiling": "The process of measuring the space or time complexity of a program.",
        "memory leak": "A situation where memory is not released after use.",
        "recursion error": "An error that occurs when the recursion limit is exceeded.",
        "stack overflow": "A type of error when the call stack exceeds its limit.",
        "heap": "A region of a process's memory used for dynamic memory allocation.",
        "pointer": "A variable that stores the memory address of another variable.",
        "reference": "An alias for an object.",
        "call stack": "A stack data structure that stores information about the active subroutines of a computer program.",
        "binary search": "An efficient algorithm for finding an item from a sorted list of items.",
        "sorting": "The process of arranging items in a certain order.",
        "quicksort": "A divide and conquer algorithm for sorting.",
        "merge sort": "A sorting algorithm that divides the list into halves and merges them in order.",
        "bubble sort": "A simple sorting algorithm that repeatedly steps through the list.",
        "selection sort": "A sorting algorithm that repeatedly finds the minimum element.",
        "object-oriented programming": "A programming paradigm based on the concept of objects containing data and behavior."
    }
    # Create flashcards for each term
    for term, definition in coding_terms.items():
        Flashcard.objects.create(
            flashcard_set=flashcard_set,
            term=term,
            definition=definition
        )

    return redirect('flashcard_set_details', set_id=flashcard_set.id)

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
        'set_id': flashcard_set.id,
        'flashcard_set': flashcard_set,
        'user_folders': user_folders
    }
    # Render the edit_flashcard_set.html template with the context
    return render(request, 'edit_flashcard_set.html', context)

@csrf_exempt  # Only use if CSRF token is not available
def update_flashcard(request, term_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate input
            term = data.get("term", "").strip()
            definition = data.get("definition", "").strip()
            if not term or not definition:
                return JsonResponse({"success": False, "error": "Term and definition cannot be empty"}, status=400)

            # Fetch the flashcard and update fields
            flashcard = get_object_or_404(Flashcard, id=term_id)
            flashcard.term = term
            flashcard.definition = definition
            flashcard.save()

            return JsonResponse({"success": True})
        
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


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
    return render(request, 'calendar.html')  # This is the new calendar pages

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







@require_POST
def update_star_status(request, term_id):
    try:
        data = json.loads(request.body)
        new_status = data.get("starred")  # Expecting true/false from JS
        flashcard = Flashcard.objects.get(id=term_id)
        flashcard.is_starred = new_status
        flashcard.save()
        return JsonResponse({"success": True})
    except Flashcard.DoesNotExist:
        return JsonResponse({"success": False, "error": "Flashcard not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

def search_terms(request, set_id):
    # Get the flashcard set by ID (or 404 if not found)
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    
    # Get the search query from GET parameters
    query = request.GET.get("q", "")
    
    if query:
        # Filter flashcards within this set where the term or definition matches the query
        filtered_flashcards = flashcard_set.flashcards.filter(
            Q(term__icontains=query) | Q(definition__icontains=query)
        )
        # If we found matches, use them; otherwise, show all flashcards in this set
        flashcards = filtered_flashcards if filtered_flashcards.exists() else flashcard_set.flashcards.all()
    else:
        # No search query provided, so display all flashcards in the set
        flashcards = flashcard_set.flashcards.all()
    
    # Optionally, set a flag on each flashcard (if needed for your template logic)
    for flashcard in flashcards:
        flashcard.is_learned = flashcard.learned_by.filter(id=request.user.id).exists()
    
    return render(request, "set_page.html", {
        "flashcard_set": flashcard_set,
        "terms": flashcards,  # your template might loop over "terms"
        "query": query,
    })
    
@login_required
@require_POST
def update_learn_settings(request):
    data = json.loads(request.body)
    starred = data.get("starred", False)
    shuffle = data.get("shuffle", False)
    timer = data.get("timer", "none")
    ultradian = data.get("ultradian", False)
    answer_with_term = data.get("answer_with_term", False)
    answer_with_definition = data.get("answer_with_definition", False)
    round_length = data.get("round_length", 1)

    # Example: if you have a UserSettings model (or store these in the UserProfile)
    # user_settings = request.user.settings  # assuming a OneToOneField linking a settings model to your user
    # user_settings.study_starred = starred
    # user_settings.study_shuffle = shuffle
    # user_settings.study_timer = timer
    # user_settings.ultradian = ultradian
    # user_settings.answer_with_term = answer_with_term
    # user_settings.answer_with_definition = answer_with_definition
    # user_settings.round_length = round_length
    # user_settings.save()

    return JsonResponse({"success": True})

def delete_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, pk=set_id)
    if request.method == 'POST':
        flashcard_set.delete()
        return redirect('home')  
    return redirect('flashcard_set_details', set_id=set_id)
    
    
