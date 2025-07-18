from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('recycling_guide/', views.recycling_guide_view, name='recycling_guide'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('api/material/', views.search_material),
    path('material-result/', views.search_material_result, name='material_result'),
    path('api/centers/', views.get_centers),

    path('profile/', views.user_profile, name='user_profile'),
    path('update-progress/', views.update_progress, name='update_progress'),
    path('upload-proof/', views.upload_proof, name='upload_proof'),
    path('challenges/', views.challenges_page, name='challenges'),
    path('join-challenge/', views.join_challenge, name='join_challenge'),
    path('news/', views.news_view, name='news'),

    # Volunteer 
    path('volunteer/', views.volunteer_opportunities, name='volunteer_opportunities'),
    path('volunteer/signup/<int:opportunity_id>/', views.volunteer_signup, name='volunteer_signup'),
    path('volunteer/track/', views.track_volunteer_hours, name='track_volunteer_hours'),

    # Forum 
    path('forum/', views.forum, name='forum'),
    path('forum/new/', views.new_forum_post, name='new_forum_post'),
    path('forum/<int:post_id>/', views.post_detail, name='forum_post_detail'),
    path('forum/<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('forum/<int:post_id>/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('forum/<int:post_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.confirm_delete_post, name='confirm_delete_post'),

    path('api/post/<int:post_id>/reactions/', views.get_post_reactions, name='get_post_reactions'),
    path('api/post/<int:post_id>/react/', views.react_to_post, name='react_to_post'),

    #Suggestion
    path('vote/<int:suggestion_id>/', views.vote_suggestion, name='vote_suggestion'),

    #Poll
    path('polls/', views.poll_list, name='poll_list'),
    path('polls/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('polls/<int:poll_id>/vote/', views.vote_poll_option, name='poll_vote'),
    
    #super admin dashboard
    path('dashboard/admin/users/', views.manage_users, name='manage_users'),
    path('dashboard/admin/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('dashboard/admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('dashboard/admin/volunteers/', views.manage_volunteers, name='manage_volunteers'),
    path('dashboard/admin/volunteers/<int:signup_id>/certify/', views.certify_volunteer, name='certify_volunteer'),
    path('dashboard/admin/volunteers/<int:signup_id>/hours/', views.update_hours, name='update_volunteer_hours'),
    path('dashboard/admin/proofs/', views.approve_proofs, name='approve_proofs'),
    path('dashboard/admin/proofs/<int:proof_id>/verify/', views.verify_proof, name='verify_proof'),
    path('events/', views.event, name='event'),
    path('events/register/<int:event_id>/', views.register_event, name='register_event'),
    path('pickup/', views.pickup, name='pickup'),
    path('pickup/send-reminder/', views.send_reminder, name='send_reminder'),
]
