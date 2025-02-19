from django.test import TestCase
from .models import FlashcardSet, Flashcard
# Create your tests here.

class FlashcardSetTestCase(TestCase):
    def setUp(self):
        FlashcardSet.objects.create(title="Test Flashcard Set", description="This is a test flashcard set.")
        Flashcard.objects.create(term="Test Term", definition="This is a test definition.")