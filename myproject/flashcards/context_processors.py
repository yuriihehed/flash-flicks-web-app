# context_processors.py
from flashcards.models import Folder

def folder_context(request):
    if request.user.is_authenticated:
        folders = Folder.objects.filter(user=request.user)
        return {'user_folders': folders}
    return {'user_folders': []}