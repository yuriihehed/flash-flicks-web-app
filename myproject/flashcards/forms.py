from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Flashcard
from .models import Folder
from .models import Deck

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]

        error_messages = {
            'username': {
                "required": "A username is required.",
                'unique': 'A user with that name already exists.'
            }
        }

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ["deck", "question", "answer"] #, "is_favorite"


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name"]

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["folder", "name", "description"]

