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
from django.contrib.auth.decorators import login_required
from .models import RecyclingProof , UserChallenge , Reward
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from .models import VolunteerOpportunity, VolunteerSignup



def home(request):
    return render(request, 'home.html') 

def recycling_guide_view(request):
    return render(request, 'recycling_guide.html')


def forum(request):
    return render(request, 'forum.html') 

def pickup(request):
    return render(request, 'pickup_schedule.html') 


def event(request):
    return render(request, 'event.html') 


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



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  
            return redirect('user_profile') 
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')



@login_required
def challenges_page(request):
    user_progress = 0

    try:
        challenge = UserChallenge.objects.get(user=request.user)
        user_progress = challenge.progress
    except UserChallenge.DoesNotExist:
        pass

    return render(request, 'challenges.html', {'user_progress': user_progress})


@login_required
def join_challenge(request):
    if request.method == 'POST':
        UserChallenge.objects.get_or_create(user=request.user)
    return redirect('challenges')


@login_required
def user_profile(request):
    user = request.user
    challenge = UserChallenge.objects.filter(user=user).first()
    proofs = RecyclingProof.objects.filter(challenge=challenge) if challenge else None
    recent_rewards = Reward.objects.filter(user=user).order_by('-date_awarded')[:5]
    volunteer_signups = VolunteerSignup.objects.filter(user=user)

    return render(request, 'user_profile.html', {
        'user': user,
        'challenge': challenge,
        'proofs': proofs,
        'recent_rewards': recent_rewards,
        'volunteer_signups': volunteer_signups,
    })



@require_POST
@login_required
def update_progress(request):
    increment = int(request.POST.get('increment', 0))
    try:
        challenge = UserChallenge.objects.get(user=request.user)
        challenge.progress = min(100, challenge.progress + increment)
        challenge.save()

        # Reward logic: only if 100% and not already rewarded
        if challenge.progress >= 100 and not Reward.objects.filter(user=request.user, title="Challenge Completed").exists():
            Reward.objects.create(
                user=request.user,
                title="Challenge Completed",
                description="Congratulations on completing the recycling challenge!"
            )

        messages.success(request, f"Progress updated to {challenge.progress}%")

    except UserChallenge.DoesNotExist:
        messages.error(request, "You haven't joined the challenge yet.")

    return redirect('user_profile')

def upload_proof(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        challenge = UserChallenge.objects.get(user=request.user)

        # Only allow 1 proof per challenge
        if RecyclingProof.objects.filter(challenge=challenge).count() >= 10:
            messages.warning(request, "You've already uploaded 10 proofs for this challenge.")
            return redirect('user_profile')

        # Save proof
        RecyclingProof.objects.create(
            challenge=challenge,
            image=image,
            verified=True
        )

        # Update progress by 10 points per proof
        challenge.progress = min(100, challenge.progress + 10)
        challenge.save()

        # If user has uploaded 10 proofs (1000 points), give reward
        total_proofs = RecyclingProof.objects.filter(challenge=challenge).count()
        if total_proofs == 10 and not Reward.objects.filter(user=request.user, title="1000 Point Milestone").exists():
            Reward.objects.create(
                user=request.user,
                title="1000 Point Milestone",
                description="You've uploaded 10 proofs and earned 1000 points!"
            )

        messages.success(request, "Proof uploaded and auto-verified!")
        return redirect('user_profile')

    return render(request, 'upload_proof.html')
@login_required
def volunteer_opportunities(request):
    opportunities = VolunteerOpportunity.objects.all()
    signups = VolunteerSignup.objects.filter(user=request.user).values_list('opportunity_id', flat=True)

    return render(request, 'volunteer_opportunities.html', {
        'opportunities': opportunities,
        'user_signups': signups,
    })


@login_required
def volunteer_signup(request, opportunity_id):
    opportunity = VolunteerOpportunity.objects.get(id=opportunity_id)
    VolunteerSignup.objects.get_or_create(user=request.user, opportunity=opportunity)
    messages.success(request, f"You've signed up for: {opportunity.title}")
    return redirect('volunteer_opportunities')
