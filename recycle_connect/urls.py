from django.shortcuts import render
from django.urls import path 
from . import views
# from .views import  home, login, signup
from django.contrib.auth import views as auth_views
from recycle_connect import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('recycling_guide/', views.recycling_guide_view, name='recycling_guide'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('api/material/', views.search_material),
    path('api/centers/', views.get_centers),
    path('profile/', views.user_profile, name='user_profile'),
    path('update-progress/', views.update_progress, name='update_progress'),
    path('upload-proof/', views.upload_proof, name='upload_proof'),
    path('challenges/', views.challenges_page, name='challenges'),
    path('join-challenge/', views.join_challenge, name='join_challenge'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('forum/', views.forum, name='forum'),
    path('pickup/', views.pickup, name='pickup'),
    path('event/', views.event, name='event'),
    path('news/', views.news, name='news'),
    path('volunteer/', views.volunteer_opportunities, name='volunteer_opportunities'),
    path('volunteer/signup/<int:opportunity_id>/', views.volunteer_signup, name='volunteer_signup'),
    path('volunteer/', views.volunteer_opportunities, name='volunteer_opportunities'),
    path('volunteer/track/', views.track_volunteer_hours, name='track_volunteer_hours'),
   path('volunteer/signup/<int:opportunity_id>/', views.volunteer_signup, name='signup_volunteer'),


       
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
