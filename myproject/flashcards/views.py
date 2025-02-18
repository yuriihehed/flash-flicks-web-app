from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

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

def homepage(request):
    return render(request, 'homepage.html')