from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify 



# Custom user model
class CustomUser(AbstractUser):
    """Extends Django's built-in User model to use email instead of username."""
    email = models.EmailField(unique=True)
    
    # Explicitly remove the username field
    username = None  

    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    study_goal = models.IntegerField(default=30)  
    study_time = models.IntegerField(default=0)  

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_users_groups",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_users_permissions",
        blank=True
    )

    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = []  

    def __str__(self):
        return self.email
    
# Folder model for grouping decks 
class Folder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Generate slug from the name
            # Ensure slug uniqueness
            while Folder.objects.filter(slug=self.slug).exists():
                self.slug += "-" + str(Folder.objects.filter(slug__startswith=self.slug).count())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
# The flashcard set model hold the overall title and description of the flashcard set
class FlashcardSet(models.Model):
    title = models.CharField(max_length=200)  # required text for flashcard
    description = models.TextField(blank=True, null = True) # optional description for flashcard (can be blank)
    created_at = models.DateTimeField(auto_now_add=True)  # auto set the created date
    updated_at = models.DateTimeField(auto_now=True)  # auto set the updated date
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='flashcard_sets') # added by Gulbanu
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)


    
    # returns the title of the flashcard set
    def __str__(self):
        return self.title

# The flashcard model holds the question and answer for the flashcard
class Flashcard(models.Model):
    # flashcard_set: a foreign key referencing the flashcard set the flashcard belongs to
    # on_delete=models.CASCADE: when the flashcard set is deleted, delete the flashcard
    # related_name='flashcards': lets you access cards with flashcard_set.flashcards.all()
    flashcard_set = models.ForeignKey(
        FlashcardSet, 
        on_delete=models.CASCADE, 
        related_name='flashcards',
        default=None
    )
    term = models.CharField(max_length=200, default="")  # required text for flashcard
    definition = models.TextField()  # required text for flashcard
    image = models.ImageField(upload_to='images/', blank=True, null=True)  # optional image for flashcard (can be blank)
    is_favorite = models.BooleanField(default=False)  # Starred flashcards
    
    def __str__(self):
        return f"{self.term}: {self.definition}"  # flashcard term and answer
    
# User profile model
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,  default=None)
    folders = models.ManyToManyField(Folder)

    def __str__(self):
        return self.user.email
    
#  Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    deck = models.ManyToManyField(FlashcardSet) 

    def __str__(self):
        return self.name

# Progress model - reviewed
class Progress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,  default=None)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    deck = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)
    last_reviewed = models.DateTimeField(auto_now=True)
    study_attempts = models.IntegerField(default=0)
    correct_attempts = models.PositiveIntegerField(default=0)

    def success_rate(self):
        return (self.correct_attempts / self.study_attempts * 100) if self.study_attempts > 0 else 0


# Study streak model - reviewed
class StudyStreak(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,  default=None)
    last_study_date = models.DateField(auto_now=True)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0) 
    streak_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}\'s study streak'  # User's study streak
    
    

    
