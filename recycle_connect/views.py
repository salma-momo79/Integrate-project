from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.conf import settings
from .models import Reminder
from django.core.mail import send_mail
from twilio.rest import Client
import threading
import time
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


from .models import (
    Material, RecyclingCenter, RecyclingProof, UserChallenge,
    Reward, VolunteerOpportunity, VolunteerSignup,
    ForumPost, Comment, Suggestion, PostReaction,
    ReactionType, Poll, PollOption, Vote ,PickupReminder,
)
from .forms import ForumPostForm,CommentForm
from .models import ForumPost

def home(request):
    return render(request, 'home.html')

def recycling_guide_view(request):
    return render(request, 'recycling_guide.html')


#Auth view
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

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=full_name
        )
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'template/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('user_profile')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


#Material Search
@api_view(['GET'])
def search_material(request):
    name = request.GET.get('name', '').strip().lower()
    if not name:
        return Response({'error': 'Please provide a material name.'}, status=400)

    try:
        material = Material.objects.get(name__iexact=name)
        from .serializers import MaterialSerializer
        serializer = MaterialSerializer(material)
        return Response(serializer.data)
    except Material.DoesNotExist:
        return Response({'error': 'Material not found'}, status=404)


def search_material_result(request):
    name = request.GET.get('name', '').strip().lower()
    material = None
    description_list = []

    if name:
        try:
            material = Material.objects.get(name__iexact=name)
            description_list = [
                sent.strip() for sent in material.description.split('.') if sent.strip()
            ]
        except Material.DoesNotExist:
            material = None

    return render(request, 'material_result.html', {
        'material': material,
        'description_list': description_list,
    })


@api_view(['GET'])
def get_centers(request):
    centers = RecyclingCenter.objects.all()
    from .serializers import RecyclingCenterSerializer
    serializer = RecyclingCenterSerializer(centers, many=True)
    return Response(serializer.data)


#Challenge
@login_required
def challenges_page(request):
    user_progress = 0
    challenge = UserChallenge.objects.filter(user=request.user).first()
    if challenge:
        user_progress = challenge.progress
    return render(request, 'challenges.html', {'user_progress': user_progress})


@login_required
def join_challenge(request):
    if request.method == 'POST':
        UserChallenge.objects.get_or_create(user=request.user)
    return redirect('challenges')


@require_POST
@login_required
def update_progress(request):
    increment = int(request.POST.get('increment', 0))
    challenge = UserChallenge.objects.filter(user=request.user).first()

    if challenge:
        challenge.progress = min(100, challenge.progress + increment)
        challenge.save()

        if challenge.progress >= 100 and not Reward.objects.filter(user=request.user, title="Challenge Completed").exists():
            Reward.objects.create(
                user=request.user,
                title="Challenge Completed",
                description="Congratulations on completing the recycling challenge!"
            )
        messages.success(request, f"Progress updated to {challenge.progress}%")
    else:
        messages.error(request, "You haven't joined the challenge yet.")
    return redirect('user_profile')


#Proof Upload 
@login_required
def upload_proof(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        challenge = UserChallenge.objects.get(user=request.user)

        if RecyclingProof.objects.filter(challenge=challenge).count() >= 10:
            messages.warning(request, "You've already uploaded 10 proofs.")
            return redirect('user_profile')

        RecyclingProof.objects.create(
            challenge=challenge,
            image=image,
            verified=True
        )

        challenge.progress = min(100, challenge.progress + 10)
        challenge.save()

        if challenge.progress == 100 and not Reward.objects.filter(user=request.user, title="1000 Point Milestone").exists():
            Reward.objects.create(
                user=request.user,
                title="1000 Point Milestone",
                description="You've uploaded 10 proofs and earned 1000 points!"
            )

        messages.success(request, "Proof uploaded and auto-verified!")
        return redirect('user_profile')

    return render(request, 'upload_proof.html')


@login_required
def user_profile(request):
    user = request.user
    challenge = UserChallenge.objects.filter(user=user).first()
    proofs = RecyclingProof.objects.filter(challenge=challenge) if challenge else None
    recent_rewards = Reward.objects.filter(user=user).order_by('-date_awarded')[:5]
    volunteer_signups = VolunteerSignup.objects.filter(user=user)
    registrations = EventRegistration.objects.filter(user=user).select_related('event').order_by('-registered_at')

    return render(request, 'user_profile.html', {
        'user': user,
        'challenge': challenge,
        'proofs': proofs,
        'recent_rewards': recent_rewards,
        'volunteer_signups': volunteer_signups,
        'registrations': registrations, 
    })


#Volunteer
@login_required
def volunteer_opportunities(request):
    query = request.GET.get('q')
    opportunities = VolunteerOpportunity.objects.filter(title__icontains=query) if query else VolunteerOpportunity.objects.all()
    user_signups = VolunteerSignup.objects.filter(user=request.user).values_list('opportunity_id', flat=True)

    return render(request, 'opportunity.html', {
        'opportunities': opportunities,
        'user_signups': user_signups,
    })


@login_required
def volunteer_signup(request, opportunity_id):
    opportunity = get_object_or_404(VolunteerOpportunity, id=opportunity_id)
    signup, created = VolunteerSignup.objects.get_or_create(user=request.user, opportunity=opportunity)

    if created:
        messages.success(request, f"Signed up for: {opportunity.title}")
    else:
        messages.info(request, f"Already signed up for: {opportunity.title}")
    return redirect('volunteer_opportunities')


@login_required
def track_volunteer_hours(request):
    signups = VolunteerSignup.objects.filter(user=request.user)
    return render(request, 'volunteer/track_hours.html', {'signups': signups})


#Forum 
@login_required
def new_forum_post(request):
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.is_approved = False
            post.save()
            return redirect('forum')
    else:
        form = ForumPostForm()
    return render(request, 'new_forum_post.html', {'form': form})


def forum(request):
    posts = ForumPost.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'forum.html', {'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, is_approved=True)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    suggestions = Suggestion.objects.filter(post=post)
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'suggestions': suggestions
    })

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, user=request.user)
    if request.method == 'POST':
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('forum')
    else:
        form = ForumPostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form})
@login_required
def confirm_delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('forum')
    return render(request, 'confirm_delete_post.html', {'post': post})

@login_required
def post_comment(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
    return redirect('forum_post_detail', post_id=post.id)
@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id, user=request.user)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully.")
            return redirect('forum')  
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'edit_comment.html', {'form': form, 'post_id': post_id})
@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id, user=request.user)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('forum') 
    
    return render(request, 'confirm_delete_comment.html', {'comment': comment, 'post_id': post_id})

@login_required
def vote_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    suggestion.votes.add(request.user)
    return redirect('forum_post_detail', post_id=suggestion.post.id)


#Reaction API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_reactions(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    reactions = post.reactions.all()
    counts = {r: reactions.filter(reaction=r).count() for r in ReactionType.values}
    user_reaction = reactions.filter(user=request.user).first().reaction if request.user.is_authenticated and reactions.filter(user=request.user).exists() else None
    return Response({'counts': counts, 'user_reaction': user_reaction})


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def react_to_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    user = request.user

    if request.method == 'POST':
        reaction = request.data.get('reaction')
        if reaction not in ReactionType.values:
            return Response({'error': 'Invalid reaction'}, status=400)
        PostReaction.objects.update_or_create(post=post, user=user, defaults={'reaction': reaction})
        return Response({'status': 'reaction set'})

    if request.method == 'DELETE':
        try:
            PostReaction.objects.get(post=post, user=user).delete()
            return Response({'status': 'reaction removed'})
        except PostReaction.DoesNotExist:
            return Response({'error': 'No reaction to remove'}, status=400)


#POLLS
def poll_list(request):
    polls = Poll.objects.all().order_by('-created_at')
    return render(request, 'polls/list.html', {'polls': polls})


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    options = poll.options.all()
    has_voted = Vote.objects.filter(option__poll=poll, user=request.user).exists() if request.user.is_authenticated else False

    return render(request, 'polls/detail.html', {
        'poll': poll,
        'options': options,
        'has_voted': has_voted,
    })


@login_required
def vote_poll_option(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    option_id = request.POST.get('option')

    if not option_id:
        messages.error(request, "No option selected.")
        return redirect('poll_detail', poll_id=poll_id)

    option = get_object_or_404(PollOption, id=option_id, poll=poll)

    if Vote.objects.filter(option__poll=poll, user=request.user).exists():
        messages.warning(request, "You have already voted.")
    else:
        Vote.objects.create(option=option, user=request.user)
        messages.success(request, "Vote recorded successfully.")

    return redirect('poll_detail', poll_id=poll_id)


#super admin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import VolunteerSignup, RecyclingProof

@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    users = User.objects.exclude(is_superuser=True)
    return render(request, 'admin_dashboard.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f"User '{user.username}' has been banned.")
    return redirect('manage_users')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('manage_users')

@user_passes_test(lambda u: u.is_superuser)
def manage_volunteers(request):
    signup = VolunteerSignup.objects.select_related('user', 'opportunity')
    return render(request, 'admin_manage_volunteers.html', {'signup': signup})

@user_passes_test(lambda u: u.is_superuser)
def certify_volunteer(request, signup_id):
    signup = get_object_or_404(VolunteerSignup, id=signup_id)
    signup.certified = True
    signup.save()
    messages.success(request, "Volunteer certified successfully.")
    return redirect('manage_volunteers')

@user_passes_test(lambda u: u.is_superuser)
def update_hours(request, signup_id):
    signup = get_object_or_404(VolunteerSignup, id=signup_id)
    if request.method == "POST":
        hours = request.POST.get('hours')
        if hours.isdigit():
            signup.hours_completed = int(hours)
            signup.save()
            messages.success(request, "Hours updated.")
    return redirect('manage_volunteers')

@user_passes_test(lambda u: u.is_superuser)
def approve_proofs(request):
    proofs = RecyclingProof.objects.filter(verified=False)
    return render(request, 'admin_approve_proofs.html', {'proofs': proofs})

@user_passes_test(lambda u: u.is_superuser)
def verify_proof(request, proof_id):
    proof = get_object_or_404(RecyclingProof, id=proof_id)
    proof.verified = True
    proof.save()
    messages.success(request, "Proof approved.")
    return redirect('approve_proofs')

from .models import Event, EventRegistration
from .forms import EventRegistrationForm

def event(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'event.html', {'events': events})

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.info(request, "You have already registered for this event.")
        return redirect('event_page')

    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.event = event
            registration.save()
            messages.success(request, f"Successfully registered for {event.title}!")
            return redirect('user_profile')  
    else:
        form = EventRegistrationForm()

    return render(request, 'register_event.html', {'form': form, 'event': event})

def pickup(request):
    return render(request, 'pickup_schedule.html')

def pickup(request):
    return render(request, 'pickup_schedule.html')

def send_sms_later(phone, message, send_at):
    delay = (send_at - timezone.now()).total_seconds()
    if delay > 0:
        time.sleep(delay)
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone)

def send_email_later(email, subject, body, send_at):
    delay = (send_at - timezone.now()).total_seconds()
    if delay > 0:
        time.sleep(delay)
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])

@csrf_exempt
def send_reminder(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        reminder_time_str = request.POST.get('reminder_time')
        message = "Don't forget your recycling pickup!"

        if not reminder_time_str:
            return render(request, 'pickup_schedule.html', {'error': 'Reminder time required!'})

        reminder_time = datetime.fromisoformat(reminder_time_str)
        reminder_time = timezone.make_aware(reminder_time)

        reminder = Reminder(phone=phone or '', email=email or '', reminder_time=reminder_time)
        reminder.save()

        if phone:
            threading.Thread(target=send_sms_later, args=(phone, message, reminder.reminder_time)).start()
        if email:
            threading.Thread(target=send_email_later, args=(email, 'Recycle Pickup Reminder', message, reminder.reminder_time)).start()

        return render(request, 'pickup_schedule.html', {'success': 'Reminder scheduled successfully!'})

    return redirect('pickup_schedule')
from datetime import time
from itertools import chain
from django.utils.timezone import now, make_aware
from django.shortcuts import render
from .models import Event, ForumPost, PickupReminder  

def news_view(request):
    current_time = now()

    events = Event.objects.filter(date__gte=current_time.date()).order_by('-date')
    forum_posts = ForumPost.objects.filter(is_approved=True).order_by('-created_at')
    pickups = PickupReminder.objects.filter(reminder_time__gte=current_time).order_by('-reminder_time')

    event_items = []
    for e in events:
        
        naive_datetime = datetime.combine(e.date, time.min)
        aware_datetime = make_aware(naive_datetime) if naive_datetime.tzinfo is None else naive_datetime

        event_items.append({
            'type': 'event',
            'title': e.title,
            'content': e.description or 'No description',
            'date': aware_datetime,
            'url': f'/events/register/{e.id}/',
        })

    forum_items = [{
        'type': 'forum_post',
        'title': fp.title,
        'content': fp.description or 'No content',
        'date': fp.created_at,
        'url': f'/forum/{fp.id}/',
    } for fp in forum_posts]

    pickup_items = [{
        'type': 'pickup',
        'title': 'Pickup Reminder',
        'content': getattr(pr, 'message', 'Upcoming recycling pickup scheduled.'),
        'date': pr.reminder_time,
        'url': '/pickup/',
    } for pr in pickups]

    combined_news = sorted(
        chain(event_items, forum_items, pickup_items),
        key=lambda x: x['date'],
        reverse=True
    )

    return render(request, 'news.html', {'news_items': combined_news})
