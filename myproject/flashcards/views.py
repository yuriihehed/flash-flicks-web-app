from django.shortcuts import render, redirect, get_object_or_404

def landing_page(request):
   return render(request, 'landing.html')

def base_page(request):
   return render(request, 'base.html')