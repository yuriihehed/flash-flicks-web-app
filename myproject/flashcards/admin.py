from django.contrib import admin
from .models import CustomUser, Folder, FlashcardSet, Flashcard, UserProfile, Category, Progress, StudyStreak
from django.contrib.auth.admin import UserAdmin

# Customizing the admin panel for CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'study_goal', 'study_time', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('profile_picture', 'study_goal', 'study_time')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)

# Admin for Folder model
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__email')

# Admin for FlashcardSet model
@admin.register(FlashcardSet)
class FlashcardSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'user__email')
    list_filter = ('folder',)

# Admin for Flashcard model
@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('term', 'flashcard_set', 'is_favorite')
    search_fields = ('term', 'flashcard_set__title')
    list_filter = ('is_favorite', 'flashcard_set')

# Admin for UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)

# Admin for Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin for Progress model
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'flashcard', 'deck', 'last_reviewed', 'study_attempts', 'correct_attempts')
    search_fields = ('user__email', 'flashcard__term', 'deck__title')
    list_filter = ('deck',)

# Admin for StudyStreak model
@admin.register(StudyStreak)
class StudyStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_study_date', 'current_streak', 'longest_streak')
    search_fields = ('user__email',)
