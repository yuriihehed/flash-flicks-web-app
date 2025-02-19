from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
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

# This view function handles displaying and processing the form for creating a new flashcard set.
# along with multiple flashcards in a single form
def create_flashcard_set(request):
    
    # check if the form was submitted(POST request) or is being loaded(GET request)
    if request.method == 'POST':
        set_form = FlashcardSetForm(request.POST) # create a form instance with the submitted data
        # create a formset instance with the submitted data
        # and the queryset is set to an empty list to prevent any existing flashcards from being displayed
        formset = FlashcardFormSet(request.POST, request.FILES, queryset=Flashcard.objects.none())
        
        # check if the form and formset are valid, if so save it to the database
        if set_form.is_valid() and formset.is_valid():
            flashcard_set = set_form.save()
            
            # iterate through the forms in the formset to create individual flashcard objects
            for form in formset:
                # check if the form is not empty and the DELETE checkbox is not checked
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    # create a flashcard object and set the flashcard_set attribute to the newly created flashcard set
                    flashcard = form.save(commit=False)
                    # set the flashcard_set attribute to the newly created flashcard set
                    flashcard.flashcard_set = flashcard_set
                    flashcard.save() # and of course save it to the database
            # after saving the flashcard set and flashcards, redirect the page that lists all flashcard sets (which should be the homepage)
            return redirect('homepage')
    else:
        # if the form was not submitted, create a blank form and formset
        set_form = FlashcardSetForm()
        formset = FlashcardFormSet(queryset=Flashcard.objects.none())
    # Pass the forms and formets to the template
    context = {
        'set_form': set_form,
        'formset': formset
    }
    # render the template with the context
    return render(request, 'create_flashcard_set.html', context)