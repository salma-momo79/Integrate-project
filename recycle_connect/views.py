from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
import os
# from dotenv import load_dotenv
# from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Material, RecyclingCenter
from .serializers import MaterialSerializer, RecyclingCenterSerializer

def home(request):
    return render(request, 'home.html') 

def recycling_guide_view(request):
    return render(request, 'recycling_guide.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')


from django.shortcuts import render

def signup_view(request):
    return render(request, 'signup.html') 

def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1, first_name=full_name)
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'template/signup.html')




@api_view(['GET'])
def search_material(request):
    name = request.GET.get('name', '').lower()
    try:
        material = Material.objects.get(name__iexact=name)
        serializer = MaterialSerializer(material)
        return Response(serializer.data)
    except Material.DoesNotExist:
        return Response({'error': 'Material not found'}, status=404)

@api_view(['GET'])
def get_centers(request):
    centers = RecyclingCenter.objects.all()
    serializer = RecyclingCenterSerializer(centers, many=True)
    return Response(serializer.data)
