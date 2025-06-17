from django.db import models
from django.contrib.auth.models import User

class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class RecyclingCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # one user can have multiple challenges
    progress = models.FloatField(default=0.0)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Challenge Progress"


class RecyclingProof(models.Model):
    challenge = models.ForeignKey(UserChallenge, related_name='proofs', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='proofs/')
    verified = models.BooleanField(default=False)

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_awarded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class VolunteerOpportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.title


class VolunteerSignup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    hours_completed = models.PositiveIntegerField(default=0)
    certified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.opportunity.title}"


