from django.shortcuts import render
from django.urls import path 
from . import views
from .views import  home, login, signup
from recycle_connect import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recycling_guide/', views.recycling_guide_view, name='recycling_guide'),
    # path('signup/', signup, name='signup'),
    path('signup/', signup, name='signup'),
    # path('signup/', views.signup, name='signup'),
    path('login/', login, name='login'),
    path('api/material/', views.search_material),
    path('api/centers/', views.get_centers),

    
]

