from django.shortcuts import render
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def recycling_guide(request):
    return render(request, 'recycling_guide.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')

