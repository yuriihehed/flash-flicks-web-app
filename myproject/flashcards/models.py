from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class CustomUser(AbstractUser):
    """Extends Django's built-in User model."""
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    study_goal = models.IntegerField(default=30)  # Goal in minutes per day
    study_time = models.IntegerField(default=0)  # Total study time in minutes

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

# Folder model for grouping decks 
class Folder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
# Single deck model - reviewed
class Deck(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="decks")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
# The flashcard set model hold the overall title and description of the flashcard set
class FlashcardSet(models.Model):
    title = models.CharField(max_length=200)  # required text for flashcard
    description = models.TextField(blank=True, null = True) # optional description for flashcard (can be blank)
    created_at = models.DateTimeField(auto_now_add=True)  # auto set the created date
    updated_at = models.DateTimeField(auto_now=True)  # auto set the updated date
    
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
    term = models.CharField(max_length=200, default = None)  # required text for flashcard
    answer = models.TextField()  # required text for flashcard
    image = models.ImageField(upload_to='images/', blank=True, null=True)  # optional image for flashcard (can be blank)
    is_favorite = models.BooleanField(default=False)  # Starred flashcards
    
    def __str__(self):
        return f"{self.term}: {self.answer}"  # flashcard term and answer
    
# User profile model
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    folders = models.ManyToManyField(Folder)

    def __str__(self):
        return self.user.username
    
#  Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    decks = models.ManyToManyField(Deck) 

    def __str__(self):
        return self.name


# Progress model - reviewed
class Progress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    last_reviewed = models.DateTimeField(auto_now=True)
    study_attempts = models.IntegerField(default=0)
    correct_attempts = models.PositiveIntegerField(default=0)

    def success_rate(self):
        return (self.correct_attempts / self.study_attempts * 100) if self.study_attempts > 0 else 0


# Study streak model - reviewed
class StudyStreak(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    last_study_date = models.DateField(auto_now=True)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0) 
    streak_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}\'s study streak'  # User's study streak
    
    

    
