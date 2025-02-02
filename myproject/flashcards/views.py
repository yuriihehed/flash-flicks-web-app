from django.shortcuts import render

# Create your views here.
def landing_page(request):
   return render(request, 'landing.html')

def base_page(request):
   return render(request, 'base.html')