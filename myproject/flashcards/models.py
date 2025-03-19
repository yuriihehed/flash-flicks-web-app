from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify 
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings 


# Custom user model
class CustomUser(AbstractUser):
    """Extends Django's built-in User model to use email instead of username."""
    first_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
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

class Folder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True) 

    class Meta:
        unique_together = ('user', 'name')  

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            count = 1
            while Folder.objects.filter(user=self.user, slug=self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class FlashcardSet(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='flashcard_sets', null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.title
    


# The flashcard model holds the question and answer for the flashcard
class Flashcard(models.Model):
    flashcard_set = models.ForeignKey(
        FlashcardSet, 
        on_delete=models.CASCADE, 
        related_name='flashcards',
        default=None
    )
    term = models.CharField(max_length=200, default="")  
    definition = models.TextField()  
    image = models.ImageField(upload_to='images/', blank=True, null=True)  
    is_favorite = models.BooleanField(default=False)  
    is_starred = models.BooleanField(default=False)
    learned_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="learned_flashcards", blank=True)

    def has_been_learned(self, user):
        """Checks if the flashcard has been marked as learned by the given user."""
        is_learned = self.learned_by.filter(id=user.id).exists()
        print(f" Checking learned status for {self.term}: {user.email} -> {is_learned}")  
        return is_learned

    def __str__(self):
        return f"{self.term}: {self.definition}"
    
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
        return f'{self.user.username}\'s study streak' 
    

#Calender
class Event(models.Model):
    title = models.CharField(max_length=200)
    class_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()    # Used as the first occurrence
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    
    # Recurring event fields
    is_recurring = models.BooleanField(default=False)  
    recurring_type = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.title} - {self.class_name} ({self.start_time} - {self.end_time})" 
