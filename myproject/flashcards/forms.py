from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Flashcard
from .models import Folder
from .models import FlashcardSet
from django.forms.models import modelformset_factory

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = CustomUser # removing username from the form since models.py does not use it
        fields = [ "email", "password1", "password2"]

        error_messages = {
            'email': {
                "required": "A email is required.",
                'unique': 'A user with that email already exists.'
            }
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)

# class FlashcardSetForm(forms.ModelForm):
#     class Meta:
#         model = FlashcardSet
#         fields = ["title", "description", "folder"]
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'placeholder': "Enter a title, like 'Algebra'",
#                 'style': "border: 1px solid #ccc; padding: 1rem; width: 100%;"
#             }),
#             'description': forms.TextInput(attrs={
#                 'placeholder': "Add a description.....",
#                 'style': "border: 1px solid #ccc; padding: 1rem; width: 100%;"
#             }),
#         }
    
#     def __init__(self, *args, **kwargs):
#         email = kwargs.pop('email', None)
#         super().__init__(*args, **kwargs)
#         # Make folder optional in the form
#         self.fields['folder'].required = False
#         if email:
#             self.fields['folder'].queryset = Folder.objects.filter(user__email=email)
class FlashcardSetForm(forms.ModelForm):
    class Meta:
        model = FlashcardSet
        fields = ["title", "description", "folder"]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': "Enter a title, like 'Algebra'",
                'style': "border: 1px solid #ccc; padding: 1rem; width: 100%;"
            }),
            'description': forms.TextInput(attrs={
                'placeholder': "Add a description.....",
                'style': "border: 1px solid #ccc; padding: 1rem; width: 100%;"
            }),
        }
    
    def __init__(self, *args, **kwargs):
        email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)
        
        # Make folder field optional
        self.fields['folder'].required = False
        
        # Add an empty choice for "No folder"
        if email:
            folder_queryset = Folder.objects.filter(user__email=email)
            self.fields['folder'].queryset = folder_queryset
            self.fields['folder'].empty_label = "No folder"
# # The form manages creating/updating a FlashcardSet object in the database
# class FlashcardSetForm(forms.ModelForm):
#     class Meta:
#         # This form is based on the FlashcardSet model
#         model = FlashcardSet
#         # These are the fields that will be displayed in the form
#         fields = ["title", "description", "folder"]
#         # These are the widgets that will be used to render the form fields
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'placeholder': "Enter a title, like 'Algebra'",
#                 'style': "border: 1px solid #ccc; padding: 1rem; width: 100%;"
#             }),
#             'description': forms.TextInput(attrs={
#                 'placeholder': "Add a description.....",
#                 'style': "border: 1px solid #ccc; padding: 1rem; width: 100%;"
#             }),
#         }  
#     def __init__(self, *args, **kwargs):
#         email = kwargs.pop('email', None)  # Get the email from kwargs
#         super().__init__(*args, **kwargs)
        
#         if email:  # Filter folders by email instead of user
#             self.fields['folder'].queryset = Folder.objects.filter(user__email=email)

# The form manages creating/updating a single Flashcard object and its fields in the database
class FlashcardForm(forms.ModelForm):
    class Meta:
        # This form is based on the Flashcard model
        model = Flashcard
        # These are the fields that will be displayed in the form
        fields = ["term", "definition", "image"] 
        # Adding this here so its easier to modify my html file 
        widgets = {
            'term': forms.TextInput(attrs={
                'placeholder': "Enter term",
                'style': "width: 100%; border: 1px solid #ccc; padding: 0.5rem;"
            }),
            'definition': forms.TextInput(attrs={
                'placeholder': "Enter definition",
                'style': "width: 100%; border: 1px solid #ccc; padding: 0.5rem;"
            }),
        }

# The formset lets you manage multiple Flashcard objects in a single form(add, edit, delete)
FlashcardFormSet = modelformset_factory (
    Flashcard, 
    form=FlashcardForm, 
    extra=3,  # how many blank forms are displayed
    can_delete=True # can delete existing forms (a checkbox is displayed on each form to allow removal of the card if needed)
)

        
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']
        



