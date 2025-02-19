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

