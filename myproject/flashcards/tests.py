from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from flashcards.models import FlashcardSet, Flashcard, Folder


class CreateFlashcardSetTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        # Manually create a test user without using create_user
        self.user = User(
            email="test@example.com",
            first_name="testuser"
        )
        self.user.set_password("password")
        self.user.save()
        # Log in using the email as the username
        self.client.login(username="test@example.com", password="password")


    def test_create_flashcard_set_with_100_flashcards(self):
        url = reverse('create_flashcard_set')

        # A dictionary of 100 coding terms and definitions
        coding_terms = {
            "variable": "A storage location identified by a memory address and an associated symbolic name.",
            "function": "A block of code designed to perform a specific task.",
            "class": "A blueprint for creating objects.",
            "object": "An instance of a class containing data and behavior.",
            "inheritance": "A mechanism where a new class uses the properties of an existing class.",
            "encapsulation": "The bundling of data with the methods that operate on that data.",
            "polymorphism": "The ability of different objects to be accessed through the same interface.",
            "abstraction": "The process of hiding complex implementation details and showing only essential features.",
            "algorithm": "A step-by-step procedure for solving a problem.",
            "recursion": "A function calling itself to solve a problem.",
            "iteration": "Repeating a block of code until a condition is met.",
            "loop": "A sequence of instructions that repeats until a condition is satisfied.",
            "array": "A data structure consisting of a collection of elements.",
            "list": "An ordered collection of items.",
            "tuple": "An immutable ordered collection of elements.",
            "dictionary": "A collection of key-value pairs.",
            "set": "A collection of unique elements.",
            "string": "A sequence of characters.",
            "integer": "A whole number, positive or negative, without decimals.",
            "float": "A number that has a decimal place.",
            "boolean": "A data type with two possible values: True or False.",
            "operator": "A symbol that tells the compiler or interpreter to perform specific mathematical or logical manipulations.",
            "condition": "An expression that evaluates to True or False.",
            "loop control": "Statements like break and continue that control the flow of loops.",
            "exception": "An event that occurs during the execution of a program that disrupts the normal flow.",
            "error": "A mistake in the code that prevents correct execution.",
            "debugging": "The process of finding and fixing errors in the code.",
            "comment": "A piece of text in the code that is ignored during execution.",
            "syntax": "The set of rules that defines the combinations of symbols considered correctly structured.",
            "semicolon": "A punctuation mark used to separate statements in some programming languages.",
            "compiler": "A program that translates code into executable machine language.",
            "interpreter": "A program that executes code directly, translating it line by line.",
            "bytecode": "A form of instruction set designed for efficient execution by a software interpreter.",
            "runtime": "The period during which a program is running.",
            "framework": "A platform for developing software applications.",
            "library": "A collection of precompiled routines that a program can use.",
            "API": "Application Programming Interface, a set of functions and procedures allowing the creation of applications.",
            "module": "A file containing Python definitions and statements.",
            "package": "A way of organizing related modules into a single directory hierarchy.",
            "loop variable": "A variable that takes on the value of each element in an iterable.",
            "recursion depth": "The maximum number of recursive calls before reaching an error.",
            "lambda": "An anonymous function expressed as a single statement.",
            "closure": "A record storing a function together with an environment.",
            "generator": "A function that returns an iterator which yields one value at a time.",
            "iterator": "An object representing a stream of data.",
            "comprehension": "A concise way to create lists, dictionaries, or sets.",
            "decorator": "A function that modifies the behavior of another function.",
            "multithreading": "The ability of a CPU to execute multiple threads concurrently.",
            "concurrency": "The execution of multiple instruction sequences at the same time.",
            "parallelism": "The simultaneous execution of multiple computations.",
            "asynchronous": "Operations that occur without waiting for previous ones to complete.",
            "synchronous": "Operations that occur in sequence, each waiting for the previous to finish.",
            "I/O": "Input/Output, operations that involve data exchange between the computer and the external world.",
            "file handling": "Techniques to read from and write to files.",
            "database": "A structured set of data held in a computer.",
            "SQL": "Structured Query Language, used to manage relational databases.",
            "query": "A request for information from a database.",
            "transaction": "A unit of work that is performed against a database.",
            "commit": "To save changes in a database.",
            "rollback": "To undo changes in a database transaction.",
            "join": "An operation to combine rows from two or more tables.",
            "index": "A data structure that improves the speed of data retrieval operations.",
            "normalization": "The process of organizing data to reduce redundancy.",
            "denormalization": "The process of attempting to optimize the read performance of a database.",
            "constraint": "A rule enforced on data columns in a table.",
            "primary key": "A unique identifier for a table record.",
            "foreign key": "A field in one table that uniquely identifies a row in another table.",
            "migration": "The process of moving data between databases.",
            "branch": "A parallel version of a repository.",
            "merge": "Combining multiple sequences of commits into one unified history.",
            "pull request": "A request to merge code changes.",
            "repository": "A central location where data is stored and managed.",
            "clone": "A copy of a repository.",
            "fork": "A personal copy of someone else's project.",
            "continuous integration": "A development practice where developers integrate code into a shared repository frequently.",
            "continuous deployment": "A strategy for software releases where any commit that passes tests is automatically deployed.",
            "unit test": "A test that validates a small, isolated piece of code.",
            "integration test": "A test that verifies the interactions between components.",
            "system test": "A test of the complete and integrated software system.",
            "test-driven development": "A development process where tests are written before code.",
            "mock": "A simulated object that mimics the behavior of real objects in controlled ways.",
            "stub": "A minimal implementation of an interface used during testing.",
            "patch": "A set of changes to a computer program designed to update, fix, or improve it.",
            "refactoring": "The process of restructuring existing computer code without changing its external behavior.",
            "code review": "The systematic examination of computer source code.",
            "profiling": "The process of measuring the space or time complexity of a program.",
            "memory leak": "A situation where memory is not released after use.",
            "recursion error": "An error that occurs when the recursion limit is exceeded.",
            "stack overflow": "A type of error when the call stack exceeds its limit.",
            "heap": "A region of a process's memory used for dynamic memory allocation.",
            "pointer": "A variable that stores the memory address of another variable.",
            "reference": "An alias for an object.",
            "call stack": "A stack data structure that stores information about the active subroutines of a computer program.",
            "binary search": "An efficient algorithm for finding an item from a sorted list of items.",
            "sorting": "The process of arranging items in a certain order.",
            "quicksort": "A divide and conquer algorithm for sorting.",
            "merge sort": "A sorting algorithm that divides the list into halves and merges them in order.",
            "bubble sort": "A simple sorting algorithm that repeatedly steps through the list.",
            "selection sort": "A sorting algorithm that repeatedly finds the minimum element.",
            "object-oriented programming": "A programming paradigm based on the concept of objects containing data and behavior."
        }

        # Build the POST data for the flashcard set form and the flashcard formset
        post_data = {
            # FlashcardSet form fields
            "title": "Coding Terms Set",
            "description": "A set of 100 coding terms and definitions.",
            "folder": "",
            # Management form fields for the formset (prefix is 'form' by default)
            "form-TOTAL_FORMS": str(len(coding_terms)),
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": str(len(coding_terms))
        }

        # Add flashcard data for each term/definition pair
        for index, (term, definition) in enumerate(coding_terms.items()):
            post_data[f"form-{index}-term"] = term
            post_data[f"form-{index}-definition"] = definition

        response = self.client.post(url, data=post_data)

        # Check that the response is a redirect (HTTP 302)
        self.assertEqual(response.status_code, 302)

        # Verify that a FlashcardSet was created for the test user
        flashcard_set = FlashcardSet.objects.filter(user=self.user).first()
        self.assertIsNotNone(flashcard_set)
        self.assertEqual(flashcard_set.title, "Coding Terms Set")

        # Verify that 100 Flashcard objects have been created and linked to the set
        flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
        self.assertEqual(flashcards.count(), len(coding_terms))