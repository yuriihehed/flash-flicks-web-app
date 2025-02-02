from django.shortcuts import render, redirect, get_object_or_404

def landing_page(request):
   return render(request, 'landing.html')

def base_page(request):
   return render(request, 'base.html')

def studypage(request):
    cards = range(1, 7)  # Example card range
    return render(request, 'studypage.html', {'cards': cards})

def edit_learn_mode(request):
    return render(request, 'edit_learn_mode.html')