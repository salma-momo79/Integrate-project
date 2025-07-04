from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import (
    Material, RecyclingCenter,
    RecyclingProof, UserChallenge, Reward,
    VolunteerOpportunity, VolunteerSignup
)
from .serializers import MaterialSerializer, RecyclingCenterSerializer
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
def news(request):
    return render(request, 'news.html')

#  Auth Views 
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

        user = User.objects.create_user(username=username, email=email, password=password1, first_name=full_name)
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'template/signup.html')

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


#  Recycling Guide API 

@api_view(['GET'])
def search_material(request):
    name = request.GET.get('name', '').strip().lower()
    
    if not name:
        return Response({'error': 'Please provide a material name to search.'}, status=400)
    
    try:
        material = Material.objects.get(name__iexact=name)
        serializer = MaterialSerializer(material)
        return Response(serializer.data)
    except Material.DoesNotExist:
        return Response({'error': 'Material not found'}, status=404)

@api_view(['GET'])
def get_centers(request):
    centers = RecyclingCenter.objects.all()  # Fetch all recycling centers
    serializer = RecyclingCenterSerializer(centers, many=True)
    return Response(serializer.data)  # Return the full list of centers without pagination


# Challenge Progress 
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

        # Reward if completed
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


# Proof Upload 
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


#  User Profile 
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


#  Volunteer Features 
@login_required
def volunteer_opportunities(request):
    query = request.GET.get('q')
    if query:
        opportunities = VolunteerOpportunity.objects.filter(title__icontains=query)
    else:
        opportunities = VolunteerOpportunity.objects.all()

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
        messages.success(request, f"You've signed up for: {opportunity.title}")
    else:
        messages.info(request, f"You're already signed up for: {opportunity.title}")

    return redirect('volunteer_opportunities')


# Track Hours View 
@login_required
def track_volunteer_hours(request):
    signups = VolunteerSignup.objects.filter(user=request.user)

    return render(request, 'volunteer/track_hours.html', {
        'signups': signups
    })
